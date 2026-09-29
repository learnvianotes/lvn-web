/* ============================================================
   CONTENT SOURCE — all study content comes from the database
   (Firestore, see firestoreSource.ts), and is cached on the
   device so it opens instantly and keeps working offline.

   Caching (IndexedDB, services/cache/idb.ts):
     • Anything fetched is stored on the device.
     • Once per session the app reads the tiny `meta/content`
       document. If its version differs from the cached one, the
       device cache is cleared and content is fetched fresh — so
       the database always stays the source of truth.
     • Offline, cached content is used as-is.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import { idbClear, idbGet, idbSet } from '@/services/cache/idb'
import type { Catalog, Problem, TopicDoc } from './types'
import { NotFoundError } from './errors'

export { NotFoundError }

export interface ContentSource {
  catalog(): Promise<Catalog>
  topic(subjectId: string, topicId: string): Promise<TopicDoc>
  problems(subjectId: string, categoryId: string): Promise<Problem[]>
}

/** Firestore reads are code-split: the SDK loads with the first request. */
const remote = () => import('./firestoreSource')

const VERSION_KEY = 'content:version'

/* ── cache validity (once per session) ───────────────────── */

let epoch = 0
const epochListeners = new Set<() => void>()
/** Bumps when the database has newer content than this device had — views then reload. */
export function useContentEpoch() {
  return useSyncExternalStore((l) => { epochListeners.add(l); return () => { epochListeners.delete(l) } }, () => epoch)
}

let check: Promise<void> | null = null

function validate(): Promise<void> {
  check ??= (async () => {
    const [meta, cached] = await Promise.all([
      remote().then((r) => r.fetchMeta()).catch(() => null), // offline → keep what we have
      idbGet<string>(VERSION_KEY),
    ])
    if (!meta || meta.version === cached) return
    await idbClear()
    await idbSet(VERSION_KEY, meta.version)
    memo.clear()
    if (cached) {
      // The device was showing an older version: reload what's on screen.
      epoch++
      epochListeners.forEach((l) => l())
    }
  })()
  return check
}

/* ── cached reads ────────────────────────────────────────── */

const memo = new Map<string, Promise<unknown>>()

function cached<T>(key: string, load: () => Promise<T>): Promise<T> {
  const hit = memo.get(key)
  if (hit) return hit as Promise<T>
  const p = (async () => {
    const stored = await idbGet<T>(key)
    if (stored !== undefined) {
      void validate() // show cached content now; check the version in the background
      return stored
    }
    await validate() // nothing cached: make sure the cache belongs to the current version first
    const fresh = await load()
    void idbSet(key, fresh)
    return fresh
  })()
  p.catch(() => memo.delete(key)) // allow retry after failures
  memo.set(key, p)
  return p
}

export const content: ContentSource = {
  catalog: () => cached('catalog', () => remote().then((r) => r.fetchCatalog())),
  topic: (s, t) => cached(`topic:${s}/${t}`, () => remote().then((r) => r.fetchTopic(s, t))),
  problems: (s, c) => cached(`problems:${s}/${c}`, () => remote().then((r) => r.fetchProblems(s, c))),
}
