/* ============================================================
   ACTIVITY — study history, one log per day:

     'YYYY-MM-DD' → {
        topics: { 'subjectId/topicId' → { title, subject, sec, visits, last } },
        focus:  seconds of completed focus-timer sessions
     }

   Written by useStudyTime (time actually spent on a page, only
   while visible and active) and the focus timer. A page is only
   logged once the reader engaged with it (read to the end, or a
   minute of reading) — opening it isn't studying it. A topic that
   also appears on an earlier day counts as a revisit.
   ============================================================ */

import { useMemo, useSyncExternalStore } from 'react'
import type { DayDoc, TopicVisit } from '@schema/firestore'
import { get, set } from '@/services/storage'
import { useUser } from '@/features/auth/auth'
import { dayKey } from '@/features/progress/store'

export type { TopicVisit }
export type DayLog = Omit<DayDoc, 'updatedAt'>

export type Activity = Record<string, DayLog>

const KEY = 'activity'
const emptyDay = (): DayLog => ({ topics: {}, focus: 0 })

let state: Activity = get<Activity>(KEY) ?? {}
const listeners = new Set<() => void>()
const localListeners = new Set<(day: string) => void>()

function update(day: string, log: DayLog, fromSync = false) {
  state = { ...state, [day]: log }
  set(KEY, state)
  listeners.forEach((l) => l())
  if (!fromSync) localListeners.forEach((l) => l(day))
}

window.addEventListener('storage', (e) => {
  if (e.key?.endsWith(`:${KEY}`)) {
    state = get<Activity>(KEY) ?? {}
    listeners.forEach((l) => l())
  }
})

const GUEST: Activity = {}

/** Seconds of reading below which a logged page doesn't count as studied (entries from before
    engagement tracking, when merely opening a page logged it). Matches ENGAGED_AT_END_SECONDS. */
const MIN_STUDIED_SECONDS = 20

export const isStudied = (v: TopicVisit) => v.sec >= MIN_STUDIED_SECONDS

/** The log with only studied pages (drops days left with nothing). */
function studiedOnly(all: Activity): Activity {
  const out: Activity = {}
  for (const [day, log] of Object.entries(all)) {
    const topics = Object.fromEntries(Object.entries(log.topics).filter(([, v]) => isStudied(v)))
    if (Object.keys(topics).length || log.focus) out[day] = { ...log, topics }
  }
  return out
}

/** The learner's study log (studied pages only) — empty for guests. */
export function useActivity(): Activity {
  const user = useUser()
  const s = useSyncExternalStore(
    (l) => { listeners.add(l); return () => { listeners.delete(l) } },
    () => state,
  )
  const studied = useMemo(() => studiedOnly(s), [s])
  return user ? studied : GUEST
}

export const getActivity = () => state
export function replaceActivity(next: Activity) {
  state = next
  set(KEY, state)
  listeners.forEach((l) => l())
}
/** Learner-made changes, with the day that changed (sync.ts uploads that day). */
export function onLocalActivityChange(listener: (day: string) => void) {
  localListeners.add(listener)
  return () => { localListeners.delete(listener) }
}

function today() {
  const day = dayKey()
  return { day, log: state[day] ?? emptyDay() }
}

export function recordVisit(key: string, title: string, subject: string) {
  const { day, log } = today()
  const prev = log.topics[key]
  update(day, {
    ...log,
    topics: { ...log.topics, [key]: { title, subject, sec: prev?.sec ?? 0, visits: (prev?.visits ?? 0) + 1, last: Date.now() } },
  })
}

export function addStudyTime(key: string, title: string, subject: string, seconds: number) {
  if (seconds <= 0) return
  const { day, log } = today()
  const prev = log.topics[key] ?? { title, subject, sec: 0, visits: 1, last: Date.now() }
  update(day, { ...log, topics: { ...log.topics, [key]: { ...prev, title, subject, sec: prev.sec + seconds, last: Date.now() } } })
}

export function addFocusTime(seconds: number) {
  if (seconds <= 0) return
  const { day, log } = today()
  update(day, { ...log, focus: log.focus + seconds })
}

/* ── derived values ──────────────────────────────────────── */

export function daySeconds(log: DayLog | undefined): number {
  if (!log) return 0
  return Object.values(log.topics).reduce((n, t) => n + t.sec, 0)
}

/** First day each topic was seen — used to tell a revisit from a first visit. */
export function firstSeen(activity: Activity): Map<string, string> {
  const first = new Map<string, string>()
  for (const day of Object.keys(activity).sort()) {
    for (const key of Object.keys(activity[day].topics)) if (!first.has(key)) first.set(key, day)
  }
  return first
}

/** Most recent visit of all (for "Continue where you left off"). */
export function lastVisit(activity: Activity): ({ key: string } & TopicVisit) | null {
  let best: ({ key: string } & TopicVisit) | null = null
  for (const log of Object.values(activity)) {
    for (const [key, v] of Object.entries(log.topics)) if (!best || v.last > best.last) best = { key, ...v }
  }
  return best
}

export function formatDuration(seconds: number): string {
  const m = Math.round(seconds / 60)
  if (seconds < 60) return seconds > 0 ? '<1 min' : '0 min'
  if (m < 60) return `${m} min`
  const h = Math.floor(m / 60)
  return m % 60 ? `${h} h ${m % 60} min` : `${h} h`
}
