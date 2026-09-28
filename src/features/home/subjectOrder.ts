/* ============================================================
   Subject ordering for the landing page: filter by category,
   then sort (default / the learner's own order / A–Z / progress
   / recently studied).
   ============================================================ */

import type { SubjectSort } from '@schema/firestore'
import type { Subject } from '@/features/catalog/types'
import type { Activity } from '@/features/progress/activity'
import type { ProgressState } from '@/features/progress/store'
import { subjectProgress } from '@/features/progress/stats'

export const SORTS: { id: SubjectSort; label: string }[] = [
  { id: 'default', label: 'Recommended' },
  { id: 'custom', label: 'My order' },
  { id: 'recent', label: 'Recently studied' },
  { id: 'progress', label: 'Most progress' },
  { id: 'az', label: 'A – Z' },
]

/** The learner's saved order; subjects added later go at the end in catalog order. */
export function customOrder(subjects: Subject[], saved: string[]): Subject[] {
  const byId = new Map(subjects.map((s) => [s.id, s]))
  const known = saved.filter((id) => byId.has(id)).map((id) => byId.get(id)!)
  const rest = subjects.filter((s) => !saved.includes(s.id))
  return [...known, ...rest]
}

/** Most recent time each subject was studied. */
function lastStudied(activity: Activity): Map<string, number> {
  const last = new Map<string, number>()
  for (const log of Object.values(activity)) {
    for (const [key, v] of Object.entries(log.topics)) {
      const subjectId = key.split('/')[0]
      last.set(subjectId, Math.max(last.get(subjectId) ?? 0, v.last))
    }
  }
  return last
}

export function sortSubjects(
  subjects: Subject[],
  sort: SubjectSort,
  ctx: { saved: string[]; progress: ProgressState; activity: Activity },
): Subject[] {
  const list = [...subjects].sort((a, b) => a.order - b.order)
  switch (sort) {
    case 'custom':
      return customOrder(list, ctx.saved)
    case 'az':
      return list.sort((a, b) => a.title.localeCompare(b.title))
    case 'progress': {
      const ratio = new Map(list.map((s) => [s.id, subjectProgress(s, ctx.progress).ratio]))
      return list.sort((a, b) => ratio.get(b.id)! - ratio.get(a.id)!)
    }
    case 'recent': {
      const last = lastStudied(ctx.activity)
      return list.sort((a, b) => (last.get(b.id) ?? 0) - (last.get(a.id) ?? 0))
    }
    default:
      return list
  }
}

export function move<T>(list: T[], from: number, to: number): T[] {
  const next = [...list]
  const [item] = next.splice(from, 1)
  next.splice(Math.max(0, Math.min(to, next.length)), 0, item)
  return next
}
