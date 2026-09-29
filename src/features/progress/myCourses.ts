/* ============================================================
   MY COURSES — which subjects the progress wheel tracks.

   Until the learner picks their own list (prefs.myCourses), the
   wheel shows the essentials — the core interview subjects —
   plus any subject they've already made progress in, so it never
   hides work they did.
   ============================================================ */

import type { Subject } from '@/features/catalog/types'
import type { Prefs } from '@schema/firestore'
import type { SubjectProgress } from './stats'

/** The default selection: core CS every learner is expected to know. */
export const ESSENTIAL_COURSES = ['dsa-basics', 'dsa-advanced', 'oops', 'dbms', 'operating-systems', 'computer-networks']

export interface MyCourses {
  /** tracked subjects, in catalog order */
  items: SubjectProgress[]
  /** true when the learner chose the list themselves */
  custom: boolean
}

export function myCourses(all: SubjectProgress[], prefs: Prefs): MyCourses {
  const chosen = prefs.myCourses?.length ? new Set(prefs.myCourses) : null
  if (chosen) {
    const items = all.filter((i) => chosen.has(i.subject.id))
    // A saved list whose subjects all disappeared from the catalog falls back to the default.
    if (items.length) return { items, custom: true }
  }
  return { items: all.filter((i) => ESSENTIAL_COURSES.includes(i.subject.id) || i.done > 0), custom: false }
}

/** Subject ids of the current selection (the editor's starting point). */
export const selectedIds = (m: MyCourses) => m.items.map((i) => i.subject.id)

/** Subjects grouped by category, groups in `order` (the landing page's filter order), then any others. */
export const groupByCategory = (subjects: Subject[], order: string[] = []) => {
  const groups = new Map<string, Subject[]>(order.map((id) => [id, []]))
  for (const s of subjects) {
    const key = s.category ?? ''
    groups.set(key, [...(groups.get(key) ?? []), s])
  }
  return new Map([...groups].filter(([, list]) => list.length))
}
