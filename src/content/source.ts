/* ============================================================
   CONTENT SOURCE
   One interface, two implementations with identical data:
     firestore — reads the seeded Firestore database
     static    — reads the JSON in /public/content (offline / pre-seed)
   Chosen by VITE_CONTENT_SOURCE (default: static).
   Results are memoized per session.
   ============================================================ */

import type { Catalog, Problem, TopicDoc } from './types'

export interface ContentSource {
  catalog(): Promise<Catalog>
  topic(subjectId: string, topicId: string): Promise<TopicDoc>
  problems(subjectId: string, categoryId: string): Promise<Problem[]>
}

export class NotFoundError extends Error {}

const staticSource: ContentSource = {
  async catalog() {
    return getJson<Catalog>('/content/catalog.json')
  },
  async topic(subjectId, topicId) {
    return getJson<TopicDoc>(`/content/topics/${subjectId}/${topicId}.json`)
  },
  async problems(_subjectId, categoryId) {
    return (await getJson<{ problems: Problem[] }>(`/content/problems/${categoryId}.json`)).problems
  },
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  // Vite's dev server answers unknown paths with index.html, so check the type too.
  if (res.status === 404 || !res.headers.get('content-type')?.includes('json')) throw new NotFoundError(url)
  if (!res.ok) throw new Error(`${res.status} loading ${url}`)
  return res.json() as Promise<T>
}

/** Firestore implementation is code-split so the static build never loads the SDK. */
const firestoreSource: ContentSource = {
  catalog: async () => (await import('./firestoreSource')).firestoreSource.catalog(),
  topic: async (s, t) => (await import('./firestoreSource')).firestoreSource.topic(s, t),
  problems: async (s, c) => (await import('./firestoreSource')).firestoreSource.problems(s, c),
}

export const contentSourceName: 'firestore' | 'static' =
  import.meta.env.VITE_CONTENT_SOURCE === 'firestore' ? 'firestore' : 'static'

const base = contentSourceName === 'firestore' ? firestoreSource : staticSource

const memo = new Map<string, Promise<unknown>>()
function cached<T>(key: string, load: () => Promise<T>): Promise<T> {
  if (!memo.has(key)) {
    const p = load()
    p.catch(() => memo.delete(key)) // allow retry after failures
    memo.set(key, p)
  }
  return memo.get(key) as Promise<T>
}

export const content: ContentSource = {
  catalog: () => cached('catalog', () => base.catalog()),
  topic: (s, t) => cached(`topic:${s}/${t}`, () => base.topic(s, t)),
  problems: (s, c) => cached(`problems:${s}/${c}`, () => base.problems(s, c)),
}
