/* ============================================================
   ANALYTICS — Firebase Analytics (Google Analytics 4), production
   builds only, and only after the visitor allows it (consent.ts).

   • Until then the analytics SDK isn't even downloaded: no
     cookies, no requests (Google's "basic" consent mode).
   • Withdrawing turns collection off and deletes the _ga cookies.
   • A device that was refused an account as under-18 never runs
     it (features/auth/age.ts sets the choice to 'denied').
   Page views are logged on every client-side navigation.
   ============================================================ */

import { firebaseApp, firebaseConfigured } from '@/services/firebase/app'
import { getAnalyticsConsent, subscribeConsent } from '@/services/consent'

type Log = (path: string, title: string) => void
type Mod = typeof import('firebase/analytics')
let logPageView: Log | null = null
let started: Promise<{ mod: Mod; analytics: import('firebase/analytics').Analytics } | null> | null = null

/** Whether this build can run analytics at all (so whether to ask). */
export function analyticsAvailable() {
  return import.meta.env.PROD && firebaseConfigured && Boolean(import.meta.env.VITE_FIREBASE_MEASUREMENT_ID)
}

export function initAnalytics() {
  if (!analyticsAvailable()) return
  const apply = () => void (getAnalyticsConsent() === 'granted' ? start() : stop())
  subscribeConsent(apply)
  apply()
}

async function start() {
  started ??= (async () => {
    const mod = await import('firebase/analytics')
    if (!(await mod.isSupported())) return null
    // No ads storage or personalisation, ever; analytics storage only because the visitor allowed it.
    mod.setConsent({ analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' })
    return { mod, analytics: mod.getAnalytics(firebaseApp()) }
  })()
  const s = await started
  if (!s || getAnalyticsConsent() !== 'granted') return
  s.mod.setAnalyticsCollectionEnabled(s.analytics, true)
  logPageView = (path, title) => s.mod.logEvent(s.analytics, 'page_view', { page_path: path, page_title: title })
}

async function stop() {
  logPageView = null
  const s = started && (await started)
  if (s) s.mod.setAnalyticsCollectionEnabled(s.analytics, false)
  deleteGaCookies()
}

/** _ga and _ga_<id> live on the site's top domain (e.g. .learnvianotes.in); try every level. */
function deleteGaCookies() {
  const names = document.cookie.split(';').map((c) => c.trim().split('=')[0]).filter((n) => n === '_ga' || n.startsWith('_ga_'))
  if (!names.length) return
  const parts = location.hostname.split('.')
  const domains = ['', ...parts.map((_, i) => `.${parts.slice(i).join('.')}`).filter((d) => d.includes('.', 1))]
  for (const name of names) {
    for (const domain of domains) {
      document.cookie = `${name}=; Max-Age=0; path=/${domain ? `; domain=${domain}` : ''}`
    }
  }
}

export function trackPageView(path: string) {
  logPageView?.(path, document.title)
}
