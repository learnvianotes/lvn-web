import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { createAnalytics, type Page } from '@/lib/analytics'
import { CONSENT_KEY, getAnalyticsConsent, resetConsentCache, setAnalyticsConsent, subscribeConsent } from '@/lib/consent'

/** A tab: its own window events; lib/consent.ts reads the localStorage all tabs share (`storage` below). */
function fakeTab() {
  const events = new EventTarget()
  const appended: { src: string }[] = []
  const cookies = new Map<string, string>()
  const page: Page = {
    window: Object.assign(events, { location: { origin: 'https://www.learnvianotes.in', hostname: 'www.learnvianotes.in' } }) as unknown as Page['window'],
    document: {
      createElement: (() => ({ async: false, src: '' })) as unknown as Page['document']['createElement'],
      head: { appendChild: (el: { src: string }) => appended.push(el) } as unknown as HTMLHeadElement,
      get cookie() {
        return [...cookies].map(([k, v]) => `${k}=${v}`).join('; ')
      },
      set cookie(raw: string) {
        const [pair] = raw.split(';')
        const [name, value] = pair!.split('=')
        if (/Max-Age=0/.test(raw)) cookies.delete(name!)
        else cookies.set(name!, value ?? '')
      },
    },
  }
  return { page, appended, cookies, events }
}

const storage = new Map<string, string>()
beforeEach(() => {
  storage.clear()
  resetConsentCache()
  // lib/consent.ts reads the browser's storage; here, the shared map.
  Object.assign(globalThis, {
    window: Object.assign(new EventTarget(), {
      localStorage: { getItem: (k: string) => storage.get(k) ?? null, setItem: (k: string, v: string) => void storage.set(k, v), removeItem: (k: string) => void storage.delete(k) },
    }),
  })
})
afterEach(() => {
  delete (globalThis as { window?: unknown }).window
})

/** The gtag commands pushed so far, as arrays. */
const commands = (page: Page) => (page.window.dataLayer ?? []).map((a) => Array.from(a as ArrayLike<unknown>))

describe('Google Analytics (lvn-backend ADR-0092)', () => {
  it('is off, asks nothing and loads nothing without a measurement id', () => {
    const { page, appended } = fakeTab()
    setAnalyticsConsent('granted')
    const a = createAnalytics(undefined, page)
    a.start()
    a.pageView('/subjects')
    expect(a.available).toBe(false)
    expect(appended).toEqual([])
  })

  it('downloads nothing until the visitor allows it', () => {
    const { page, appended } = fakeTab()
    const a = createAnalytics('G-TEST123', page)
    a.start()
    expect(appended).toEqual([])
    setAnalyticsConsent('denied')
    expect(appended).toEqual([])
    setAnalyticsConsent('granted')
    expect(appended.map((s) => s.src)).toEqual(['https://www.googletagmanager.com/gtag/js?id=G-TEST123'])
    expect(commands(page)[0]).toEqual(['consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' }])
    expect(commands(page)).toContainEqual(['consent', 'update', { analytics_storage: 'granted' }])
    expect(commands(page)).toContainEqual(['config', 'G-TEST123', { send_page_view: false }])
  })

  it('sends page views with the path only: no query, fragment or document title', () => {
    const { page } = fakeTab()
    setAnalyticsConsent('granted')
    const a = createAnalytics('G-TEST123', page)
    a.start()
    a.pageView('/reset?token=secret#x')
    expect(commands(page).slice(-2)).toEqual([
      ['set', { page_location: 'https://www.learnvianotes.in/reset', page_referrer: '', page_title: '/reset' }],
      ['event', 'page_view'],
    ])
  })

  it('withdrawing stops collection and deletes the _ga cookies', () => {
    const { page, cookies } = fakeTab()
    setAnalyticsConsent('granted')
    const a = createAnalytics('G-TEST123', page)
    a.start()
    cookies.set('_ga', 'GA1.1.1').set('_ga_TEST123', 'GS1').set('theme', 'dark')
    setAnalyticsConsent('denied')
    expect(page.window['ga-disable-G-TEST123']).toBe(true)
    expect(commands(page).at(-1)).toEqual(['consent', 'update', { analytics_storage: 'denied' }])
    expect([...cookies.keys()]).toEqual(['theme'])
    const before = commands(page).length
    a.pageView('/subjects')
    expect(commands(page)).toHaveLength(before)
  })

  it('a choice made in another tab applies in this one at once', () => {
    const { page, events } = fakeTab()
    const a = createAnalytics('G-TEST123', page)
    a.start()
    expect(a.loaded).toBe(false)
    // The other tab writes the shared storage; the browser tells this tab with a storage event.
    storage.set(CONSENT_KEY, JSON.stringify({ analytics: 'granted', at: 1 }))
    events.dispatchEvent(Object.assign(new Event('storage'), { key: CONSENT_KEY }))
    expect(getAnalyticsConsent()).toBe('granted')
    expect(a.loaded).toBe(true)
    storage.set(CONSENT_KEY, JSON.stringify({ analytics: 'denied', at: 2 }))
    events.dispatchEvent(Object.assign(new Event('storage'), { key: CONSENT_KEY }))
    expect(page.window['ga-disable-G-TEST123']).toBe(true)
  })

  it('ignores storage events about other keys, and forgets the choice when asked to ask again', () => {
    const heard: number[] = []
    const target = new EventTarget()
    const stop = subscribeConsent(() => heard.push(1), target)
    target.dispatchEvent(Object.assign(new Event('storage'), { key: 'lvn.theme' }))
    expect(heard).toEqual([])
    setAnalyticsConsent('granted')
    setAnalyticsConsent(null)
    expect(heard).toEqual([1, 1])
    expect(storage.has(CONSENT_KEY)).toBe(false)
    stop()
  })
})
