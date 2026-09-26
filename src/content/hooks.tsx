/* ============================================================
   CONTENT HOOKS
   ============================================================ */

import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { content } from './source'
import type { Catalog, Problem, Subject, TopicDoc } from './types'

export type AsyncState<T> =
  | { status: 'loading'; data?: undefined; error?: undefined }
  | { status: 'ready'; data: T; error?: undefined }
  | { status: 'error'; data?: undefined; error: Error }

/** Run `load` whenever `key` changes; ignores stale responses. */
export function useAsync<T>(key: string, load: () => Promise<T>): AsyncState<T> & { retry: () => void } {
  const [attempt, setAttempt] = useState(0)
  const [state, setState] = useState<{ key: string; value: AsyncState<T> }>({ key: '', value: { status: 'loading' } })

  useEffect(() => {
    let alive = true
    load().then(
      (data) => alive && setState({ key, value: { status: 'ready', data } }),
      (error: Error) => alive && setState({ key, value: { status: 'error', error } }),
    )
    return () => { alive = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- `key` identifies the request
  }, [key, attempt])

  const value: AsyncState<T> = state.key === key ? state.value : { status: 'loading' }
  return { ...value, retry: () => setAttempt((n) => n + 1) }
}

/* ── Catalog (loaded once, shared app-wide) ──────────────── */

const CatalogContext = createContext<(AsyncState<Catalog> & { retry: () => void }) | null>(null)

export function CatalogProvider({ children }: { children: ReactNode }) {
  const state = useAsync('catalog', () => content.catalog())
  return <CatalogContext.Provider value={state}>{children}</CatalogContext.Provider>
}

export function useCatalog() {
  const ctx = useContext(CatalogContext)
  if (!ctx) throw new Error('useCatalog must be used inside <CatalogProvider>')
  return ctx
}

export function useSubject(subjectId: string | undefined): Subject | undefined {
  const { data } = useCatalog()
  return useMemo(() => data?.subjects.find((s) => s.id === subjectId), [data, subjectId])
}

export function useTopic(subjectId: string, topicId: string) {
  return useAsync<TopicDoc>(`topic:${subjectId}/${topicId}`, () => content.topic(subjectId, topicId))
}

export function useProblems(subjectId: string, categoryId: string) {
  return useAsync<Problem[]>(`problems:${subjectId}/${categoryId}`, () => content.problems(subjectId, categoryId))
}
