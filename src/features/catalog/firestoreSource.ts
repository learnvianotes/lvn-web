/* ============================================================
   FIRESTORE CONTENT READS — the only place study content is
   fetched from. Document layout: schema/content.ts; written by
   scripts/content/seed (npm run content:seed).
   ============================================================ */

import { collection, doc, getDoc, getDocs, query, where } from 'firebase/firestore/lite'
import {
  PROBLEM_RICH_FIELDS, unflatten, type ContentMeta, type FlatContent, type SolutionFlat, type TopicDocFlat,
} from '@schema/content'
import { db } from '@/services/firebase/firestore'
import { firebaseConfigured } from '@/services/firebase/app'
import type { Catalog, Problem, Solution, TopicDoc } from './types'
import { NotFoundError } from './errors'

function ensureConfigured() {
  if (!firebaseConfigured) throw new Error('Firebase is not configured — set the VITE_FIREBASE_* variables (.env.local for npm run dev; .env.production.local or .env.test.local for builds).')
}

export async function fetchMeta(): Promise<ContentMeta> {
  ensureConfigured()
  const snap = await getDoc(doc(db(), 'meta', 'content'))
  if (!snap.exists()) throw new NotFoundError('meta/content — has the database been seeded? (npm run content:seed)')
  return snap.data() as ContentMeta
}

export async function fetchCatalog(): Promise<Catalog> {
  ensureConfigured()
  const snap = await getDoc(doc(db(), 'catalog', 'current'))
  if (!snap.exists()) throw new NotFoundError('catalog/current — has the database been seeded? (npm run content:seed)')
  return snap.data() as Catalog
}

export async function fetchTopic(subjectId: string, topicId: string): Promise<TopicDoc> {
  ensureConfigured()
  const ref = doc(db(), 'subjects', subjectId, 'topics', topicId)
  const snap = await getDoc(ref)
  if (!snap.exists()) throw new NotFoundError(ref.path)
  const d = snap.data() as TopicDocFlat
  return { subjectId: d.subjectId, id: d.id, title: d.title, group: d.group, order: d.order, content: unflatten(d.content) }
}

type ProblemDoc = Omit<Problem, (typeof PROBLEM_RICH_FIELDS)[number] | 'naive' | 'optimal' | 'extra'> &
  Partial<Record<(typeof PROBLEM_RICH_FIELDS)[number], FlatContent>> & {
    naive?: SolutionFlat
    optimal?: SolutionFlat
    extra?: { title: string; content: FlatContent }[]
  }

const solution = (s: SolutionFlat | undefined): Solution | undefined => s && { ...s, content: unflatten(s.content) }

function toProblem(d: ProblemDoc): Problem {
  const p = { ...d } as unknown as Problem
  for (const f of PROBLEM_RICH_FIELDS) if (d[f]) p[f] = unflatten(d[f]!)
  p.naive = solution(d.naive)
  p.optimal = solution(d.optimal)
  if (d.extra) p.extra = d.extra.map((x) => ({ title: x.title, content: unflatten(x.content) }))
  return p
}

export async function fetchProblems(subjectId: string, categoryId: string): Promise<Problem[]> {
  ensureConfigured()
  const q = query(collection(db(), 'subjects', subjectId, 'problems'), where('category', '==', categoryId))
  const snap = await getDocs(q)
  if (snap.empty) throw new NotFoundError(`${subjectId}/problems?category=${categoryId}`)
  return snap.docs.map((d) => toProblem(d.data() as ProblemDoc)).sort((a, b) => a.order - b.order)
}
