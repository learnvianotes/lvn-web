/**
 * Google Analytics 4 (lvn-backend ADR-0092): only where NEXT_PUBLIC_GA_MEASUREMENT_ID is set, and only after the visitor
 * allows it (lib/consent.ts).
 * - Until then Google's script isn't even downloaded: no cookie, no request.
 * - Ads storage, ad user data and ad personalisation are always denied.
 * - Page views are sent by hand with the path only: addresses can carry one-time tokens (email links, sign-in
 *   callbacks), and titles can name private notes, so no query, fragment or document title leaves the browser.
 * - Withdrawing stops collection at once and deletes the _ga cookies.
 */
import { getAnalyticsConsent, subscribeConsent } from '../consent'

type Gtag = (...args: unknown[]) => void
interface GaWindow {
  dataLayer?: unknown[]
  gtag?: Gtag
  [disable: `ga-disable-${string}`]: boolean | undefined
}

/** The page's parts this module touches; the browser's own in the app, fakes in tests. */
export interface Page {
  window: GaWindow & Pick<Window, 'addEventListener' | 'removeEventListener'> & { location: Pick<Location, 'origin' | 'hostname'> }
  document: Pick<Document, 'createElement' | 'head'> & { cookie: string }
}

const browserPage = (): Page | null => (typeof window === 'undefined' ? null : { window: window as unknown as Page['window'], document })

export function createAnalytics(id: string | undefined, page: Page | null = browserPage()) {
  let loaded = false
  let previous = ''

  const gtag: Gtag = (...args) => {
    if (!page) return
    page.window.dataLayer ??= []
    // gtag.js reads the arguments object itself, as Google's snippet pushes it.
    page.window.dataLayer.push(args.length ? argumentsOf(args) : args)
  }

  const load = () => {
    if (!page || !id || loaded) return
    loaded = true
    page.window.gtag = gtag
    gtag('consent', 'default', { ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied', analytics_storage: 'denied' })
    gtag('js', new Date())
    gtag('config', id, { send_page_view: false })
    const script = page.document.createElement('script')
    script.async = true
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`
    page.document.head.appendChild(script)
  }

  const apply = () => {
    if (!page || !id) return
    if (getAnalyticsConsent() === 'granted') {
      page.window[`ga-disable-${id}`] = false
      load()
      gtag('consent', 'update', { analytics_storage: 'granted' })
    } else {
      page.window[`ga-disable-${id}`] = true
      if (loaded) gtag('consent', 'update', { analytics_storage: 'denied' })
      deleteGaCookies(page)
    }
  }

  return {
    /** Whether this deployment runs analytics at all (so whether to ask). */
    available: Boolean(id),
    /** Follows the visitor's choice from now on; returns the unsubscribe. */
    start(): () => void {
      if (!page || !id) return () => undefined
      apply()
      return subscribeConsent(apply, page.window)
    },
    /** A page view for `path` (a pathname, without query or fragment), when allowed. */
    pageView(path: string): void {
      if (!page || !id || !loaded || getAnalyticsConsent() !== 'granted') return
      const location = page.window.location.origin + path.split(/[?#]/)[0]
      gtag('set', { page_location: location, page_referrer: previous, page_title: path.split(/[?#]/)[0] })
      gtag('event', 'page_view')
      previous = location
    },
    /** Whether Google's script was added to the page (tests). */
    get loaded() {
      return loaded
    },
  }
}

/** gtag.js expects each command as an `arguments` object, not an array. */
function argumentsOf(args: unknown[]): IArguments {
  return (function (..._: unknown[]) {
    // eslint-disable-next-line prefer-rest-params
    return arguments
  })(...args)
}

/** _ga and _ga_<id> live on the site's top domain (e.g. .learnvianotes.in); every level is tried. */
function deleteGaCookies({ window, document }: Page): void {
  const names = document.cookie
    .split(';')
    .map((c) => c.trim().split('=')[0] ?? '')
    .filter((n) => n === '_ga' || n.startsWith('_ga_'))
  if (!names.length) return
  const parts = window.location.hostname.split('.')
  const domains = ['', ...parts.map((_, i) => `.${parts.slice(i).join('.')}`).filter((d) => d.indexOf('.', 1) > 0)]
  for (const name of names) {
    for (const domain of domains) document.cookie = `${name}=; Max-Age=0; path=/${domain ? `; domain=${domain}` : ''}`
  }
}
