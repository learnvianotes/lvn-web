/* A single shared 1-second clock for the focus timer views; each tick also lets the store notice the end. */

import { useSyncExternalStore } from 'react'
import { tick } from './focus'

let now = Date.now()
const clockListeners = new Set<() => void>()
let clockTimer: number | undefined

function subscribeClock(l: () => void) {
  clockListeners.add(l)
  if (clockTimer === undefined) {
    clockTimer = window.setInterval(() => {
      now = Date.now()
      tick()
      clockListeners.forEach((f) => f())
    }, 1000)
  }
  return () => {
    clockListeners.delete(l)
    if (!clockListeners.size) { window.clearInterval(clockTimer); clockTimer = undefined }
  }
}

/** Refresh the shared time now (e.g. when the page becomes visible again). */
export function syncClock() {
  now = Date.now()
}

/** Re-renders the caller every second while `active`. */
export function useSecondTick(active: boolean) {
  return useSyncExternalStore(active ? subscribeClock : noopSubscribe, () => (active ? now : 0))
}
const noopSubscribe = () => () => {}

