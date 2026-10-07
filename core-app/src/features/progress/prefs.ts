/* ============================================================
   PREFS — how the learner likes the app arranged: their own
   subject order, the chosen sort, the courses they track in the
   progress wheel, and upcoming courses they asked to be notified
   about. Synced by progress/sync.ts.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import type { Prefs, SubjectSort } from '@core-schema/firestore'
import { get, set } from '@core/services/storage'

const KEY = 'prefs'
export const defaultPrefs = (): Prefs => ({ subjectOrder: [], sort: 'default', interests: [], dailyGoal: 30, updatedAt: 0 })

let state: Prefs = { ...defaultPrefs(), ...(get<Partial<Prefs>>(KEY) ?? {}) }
const listeners = new Set<() => void>()
const localListeners = new Set<() => void>()

function update(next: Prefs, fromSync = false) {
  state = next
  set(KEY, state)
  listeners.forEach((l) => l())
  if (!fromSync) localListeners.forEach((l) => l())
}

export function usePrefs(): Prefs {
  return useSyncExternalStore((l) => { listeners.add(l); return () => { listeners.delete(l) } }, () => state)
}

export const getPrefs = () => state
export const replacePrefs = (next: Prefs) => update(next, true)
export function onLocalPrefsChange(listener: () => void) {
  localListeners.add(listener)
  return () => { localListeners.delete(listener) }
}

export function setSort(sort: SubjectSort) {
  update({ ...state, sort, updatedAt: Date.now() })
}

export function setSubjectOrder(subjectOrder: string[]) {
  update({ ...state, subjectOrder, sort: 'custom', updatedAt: Date.now() })
}

export function toggleInterest(courseId: string) {
  const has = state.interests.includes(courseId)
  update({ ...state, interests: has ? state.interests.filter((c) => c !== courseId) : [...state.interests, courseId], updatedAt: Date.now() })
  return !has
}

export const DAILY_GOALS = [15, 30, 45, 60, 90, 120]

export function setDailyGoal(dailyGoal: number) {
  update({ ...state, dailyGoal, updatedAt: Date.now() })
}

export function resetSubjectOrder() {
  update({ ...state, subjectOrder: [], sort: 'default', updatedAt: Date.now() })
}

/** The courses tracked in the progress wheel (at least one). */
export function setMyCourses(ids: string[]) {
  if (!ids.length) return
  update({ ...state, myCourses: [...new Set(ids)], updatedAt: Date.now() })
}

/** Back to the default selection (the essentials + whatever the learner has started). */
export function resetMyCourses() {
  const next: Prefs = { ...state, updatedAt: Date.now() }
  delete next.myCourses
  update(next)
}
