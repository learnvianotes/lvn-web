/* ============================================================
   PROGRESS STATS — derived values for the insights panel.
   ============================================================ */

import type { Subject } from '@/content/types'
import { dayKey, topicKey, type ProgressState } from './store'

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

export function isActiveDay(p: ProgressState, key: string) {
  return (p.studied[key] ?? 0) >= 1
}

/** Consecutive active days ending today (or yesterday, if today isn't done yet). */
export function currentStreak(p: ProgressState): number {
  const d = new Date()
  if (!isActiveDay(p, dayKey(d))) d.setDate(d.getDate() - 1)
  let n = 0
  while (isActiveDay(p, dayKey(d))) {
    n++
    d.setDate(d.getDate() - 1)
  }
  return n
}

export function longestStreak(p: ProgressState): number {
  const days = Object.keys(p.studied).filter((k) => isActiveDay(p, k)).sort()
  let best = 0
  let run = 0
  let prev: Date | null = null
  for (const k of days) {
    const [y, m, d] = k.split('-').map(Number)
    const date = new Date(y, m - 1, d)
    run = prev && Math.round((date.getTime() - prev.getTime()) / 86_400_000) === 1 ? run + 1 : 1
    best = Math.max(best, run)
    prev = date
  }
  return best
}
