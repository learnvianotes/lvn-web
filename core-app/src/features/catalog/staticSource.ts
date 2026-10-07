/* ============================================================
   STATIC SOURCE — the same content the old site read from
   Firestore, now served as static JSON by lvn-web
   (app/(core)/core/data/[...path]/route.ts, generated at build
   time from content-build/). Replaces firestoreSource.ts.
   ============================================================ */

import type { Catalog, Problem, TopicDoc } from './types'
import { NotFoundError } from './errors'

const BASE = '/core/data'

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}/${path}`)
  if (res.status === 404) throw new NotFoundError()
  if (!res.ok) throw new Error(`Content request failed (${res.status})`)
  return (await res.json()) as T
}

export const fetchMeta = () => get<{ version: string }>('meta.json')
export const fetchCatalog = () => get<Catalog>('catalog.json')
export const fetchTopic = (subjectId: string, topicId: string) => get<TopicDoc>(`topics/${subjectId}/${topicId}.json`)
export const fetchProblems = (subjectId: string, categoryId: string) => get<Problem[]>(`problems/${subjectId}/${categoryId}.json`)
