/* ============================================================
   PROGRESS STATS — derived values for the insights panel.
   ============================================================ */

import type { Subject } from '@/features/catalog/types'
import { dayKey, topicKey, type ProgressState } from '@/features/progress/store'
import { daySeconds, type Activity } from '@/features/progress/activity'

export interface SubjectProgress {
  subject: Subject
  done: number
  total: number
  /** 0..1 */
  ratio: number
}

export function subjectProgress(subject: Subject, p: ProgressState): SubjectProgress {
  let done = 0
  if (subject.kind === 'problems') {
    for (const t of subject.topics) for (const q of t.problems ?? []) if (p.problems[q.id] === 'solved') done++
  } else {
    for (const t of subject.topics) if (p.topics[topicKey(subject.id, t.id)]) done++
  }
  const total = subject.itemCount
  return { subject, done, total, ratio: total ? done / total : 0 }
}

/** Seconds of reading/solving (or focus time) that make a day count toward the streak. */
export const ACTIVE_DAY_SECONDS = 60

/** Days that count toward the streak: something completed, or at least a minute studied. */
export function activeDays(p: ProgressState, activity: Activity): Set<string> {
  const days = new Set(Object.keys(p.studied).filter((k) => (p.studied[k] ?? 0) >= 1))
  for (const [day, log] of Object.entries(activity)) {
    if (daySeconds(log) + log.focus >= ACTIVE_DAY_SECONDS) days.add(day)
  }
  return days
}

/** Consecutive active days ending today (or yesterday, if today isn't done yet). */
export function currentStreak(days: Set<string>): number {
  const d = new Date()
  if (!days.has(dayKey(d))) d.setDate(d.getDate() - 1)
  let n = 0
  while (days.has(dayKey(d))) {
    n++
    d.setDate(d.getDate() - 1)
  }
  return n
}

export function longestStreak(days: Set<string>): number {
  let best = 0
  let run = 0
  let prev: Date | null = null
  for (const k of [...days].sort()) {
    const [y, m, d] = k.split('-').map(Number)
    const date = new Date(y, m - 1, d)
    run = prev && Math.round((date.getTime() - prev.getTime()) / 86_400_000) === 1 ? run + 1 : 1
    best = Math.max(best, run)
    prev = date
  }
  return best
}

/* ── Review queue (spaced repetition) ────────────────────── */

const INTERVALS = [1, 3, 7, 14, 30, 60] // days, grows with each day the topic was studied

export interface DueTopic {
  key: string
  title: string
  subject: string
  /** days since last studied */
  daysAgo: number
  /** marked "revisit" by the learner */
  flagged: boolean
}

/**
 * Topics worth reviewing now: ones the learner flagged to revisit, and
 * completed ones whose review interval has passed since they were last studied.
 */
export function dueForReview(p: ProgressState, activity: Activity, now = new Date()): DueTopic[] {
  const seen = new Map<string, { title: string; subject: string; days: number; last: string }>()
  for (const day of Object.keys(activity).sort()) {
    for (const [key, v] of Object.entries(activity[day].topics)) {
      const s = seen.get(key)
      seen.set(key, { title: v.title, subject: v.subject, days: (s?.days ?? 0) + 1, last: day })
    }
  }
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const ago = (day: string) => {
    const [y, m, d] = day.split('-').map(Number)
    return Math.round((today - new Date(y, m - 1, d).getTime()) / 86_400_000)
  }
  const out: DueTopic[] = []
  for (const [key, s] of seen) {
    const daysAgo = ago(s.last)
    const flagged = Boolean(p.revisitTopics[key])
    const interval = INTERVALS[Math.min(s.days, INTERVALS.length) - 1]
    if (flagged || (p.topics[key] && daysAgo >= interval)) out.push({ key, title: s.title, subject: s.subject, daysAgo, flagged })
  }
  return out.sort((a, b) => Number(b.flagged) - Number(a.flagged) || b.daysAgo - a.daysAgo)
}
