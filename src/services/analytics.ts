/* ============================================================
   ANALYTICS — Firebase Analytics, production builds only.
   Loaded after the first render; page views are logged on every
   client-side navigation.
   ============================================================ */

import { firebaseApp, firebaseConfigured } from '@/services/firebase/app'

type Log = (path: string, title: string) => void
let logPageView: Log | null = null

export async function initAnalytics() {
  if (!import.meta.env.PROD || !firebaseConfigured || !import.meta.env.VITE_FIREBASE_MEASUREMENT_ID) return
  const { getAnalytics, isSupported, logEvent } = await import('firebase/analytics')
  if (!(await isSupported())) return
  const analytics = getAnalytics(firebaseApp())
  logPageView = (path, title) => logEvent(analytics, 'page_view', { page_path: path, page_title: title })
}

export function trackPageView(path: string) {
  logPageView?.(path, document.title)
}
