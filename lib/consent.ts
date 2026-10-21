/**
 * The visitor's choice about Google Analytics (lvn-backend ADR-0092), kept on this device. null: not asked yet (the
 * banner asks). Nothing loads from Google unless the choice is 'granted' (lib/analytics.ts). A choice made in another
 * tab — or an under-age refusal there (lib/age.ts) — applies in this one at once, through the storage event.
 */

export type AnalyticsChoice = 'granted' | 'denied'

export const CONSENT_KEY = 'lvn.consent'

type Store = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>
const browserStore = (): Store | null => {
  try {
    return typeof window === 'undefined' ? null : window.localStorage
  } catch {
    return null
  }
}

const listeners = new Set<() => void>()
let current: AnalyticsChoice | null | undefined

function read(store: Store | null): AnalyticsChoice | null {
  try {
    const v = (JSON.parse(store?.getItem(CONSENT_KEY) ?? 'null') as { analytics?: unknown } | null)?.analytics
    return v === 'granted' || v === 'denied' ? v : null
  } catch {
    return null
  }
}

export function getAnalyticsConsent(store: Store | null = browserStore()): AnalyticsChoice | null {
  current ??= read(store)
  return current
}

/** Records the choice (or forgets it, so the banner asks again) and tells every listener in this tab. */
export function setAnalyticsConsent(choice: AnalyticsChoice | null, store: Store | null = browserStore(), now = Date.now()): void {
  try {
    if (choice) store?.setItem(CONSENT_KEY, JSON.stringify({ analytics: choice, at: now }))
    else store?.removeItem(CONSENT_KEY)
  } catch {
    // Private mode: the choice lasts for this tab.
  }
  current = choice
  listeners.forEach((l) => l())
}

/** Listens for this tab's changes and other tabs' (storage events on the same key, or a cleared storage). */
export function subscribeConsent(listener: () => void, target: Pick<Window, 'addEventListener' | 'removeEventListener'> | null = typeof window === 'undefined' ? null : window): () => void {
  listeners.add(listener)
  const onStorage = (e: Event) => {
    const key = (e as StorageEvent).key
    if (key !== null && key !== CONSENT_KEY) return
    const next = read(browserStore())
    if (next === current) return
    current = next
    listeners.forEach((l) => l())
  }
  target?.addEventListener('storage', onStorage)
  return () => {
    listeners.delete(listener)
    target?.removeEventListener('storage', onStorage)
  }
}

/** For tests: forget the cached choice. */
export function resetConsentCache(): void {
  current = undefined
}
