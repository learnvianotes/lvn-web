/* ============================================================
   CONSENT — the visitor's choice about Google Analytics, kept on
   this device. null = not asked yet (the banner asks). Nothing is
   loaded from Google Analytics unless the choice is 'granted'
   (services/analytics.ts).
   ============================================================ */

import { useSyncExternalStore } from 'react'
import { get, set, storageKey } from '@/services/storage'

export type Choice = 'granted' | 'denied'
interface Stored { analytics: Choice; at: number }

const KEY = 'consent'
const listeners = new Set<() => void>()
let current: Choice | null = read()

function read(): Choice | null {
  const s = get<Stored>(KEY)
  return s?.analytics === 'granted' || s?.analytics === 'denied' ? s.analytics : null
}

export const getAnalyticsConsent = () => current

export function setAnalyticsConsent(choice: Choice) {
  set<Stored>(KEY, { analytics: choice, at: Date.now() })
  current = choice
  listeners.forEach((l) => l())
}

// A choice made in another tab (or an under-18 refusal there) applies here at once.
if (typeof window !== 'undefined') window.addEventListener('storage', (e) => {
  if (e.key !== null && e.key !== storageKey(KEY)) return
  const next = read()
  if (next === current) return
  current = next
  listeners.forEach((l) => l())
})

export function subscribeConsent(l: () => void) {
  listeners.add(l)
  return () => { listeners.delete(l) }
}

export function useAnalyticsConsent() {
  return useSyncExternalStore(subscribeConsent, getAnalyticsConsent)
}
