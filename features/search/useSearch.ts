'use client'

import { useQuery } from '@apollo/client/react'
import { useEffect, useRef, useState } from 'react'
import { SearchDocument, type NoteKind, type NoteSource, type SearchQuery, type SearchScope } from '@/graphql/generated/graphql'
import { searchScopeOf, trackSearchNoResults, trackUsage, wordCountOf } from '@/lib/analytics'
import { track } from '@/lib/learning'

/** What narrows the notes found (lvn-backend ADR-0056); a topic alone lists its notes. */
export interface SearchFilters {
  kinds?: NoteKind[]
  sources?: NoteSource[]
  topicId?: string | null
  /** Any of these topics (an exam's, lvn-backend ADR-0076) */
  topicIds?: string[]
}

const filtered = (f: SearchFilters) => !!(f.kinds?.length || f.sources?.length || f.topicId || f.topicIds?.length)

/**
 * Search as you type: asks the API 200 ms after the last keystroke, from two characters on, or at once with filters
 * alone. `more` brings the next notes of the same search; `failed` says this search could not be asked, `retry` asks
 * again. Words left in place for two seconds are a search made (SEARCH_PERFORMED, lvn-backend ADR-0067); the words
 * themselves are not sent. The usage events (lvn-backend ADR-0107) say the same with a scope and a word count, and a
 * search that found nothing in any scope sends `search_no_results` once.
 */
export function useSearch(query: string, first: number, filters: SearchFilters = {}, scopes?: SearchScope[]) {
  const [settled, setSettled] = useState(query)
  useEffect(() => {
    const timer = setTimeout(() => setSettled(query.trim()), 200)
    return () => clearTimeout(timer)
  }, [query])
  useEffect(() => {
    if (settled.length < 2) return
    const words = settled.split(/\s+/).length
    trackUsage('search', { scope: searchScopeOf(scopes), wordCount: wordCountOf(settled) })
    const timer = setTimeout(() => track('SEARCH_PERFORMED', { metadata: { scopes: scopes?.join(',') ?? 'ALL', words } }), 2_000)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settled])
  const ready = settled.length >= 2 || filtered(filters)
  const variables = {
    query: settled,
    first,
    ...(scopes ? { scopes } : {}),
    ...(filtered(filters)
      ? { filters: { kinds: filters.kinds?.length ? filters.kinds : null, sources: filters.sources?.length ? filters.sources : null, topicId: filters.topicId ?? null, ...(filters.topicIds?.length ? { topicIds: filters.topicIds } : {}) } }
      : {}),
  }
  const result = useQuery(SearchDocument, { variables, skip: !ready, fetchPolicy: 'cache-first' })
  const data = ready ? (result.data ?? result.previousData)?.search : undefined
  // A search of words (not filters alone) whose answer has nothing at all: reported once per settled search.
  const reported = useRef<string | null>(null)
  const answered = settled.length >= 2 && !result.loading && result.data?.search ? result.data.search : undefined
  const empty = !!answered && !answered.notes.length && !answered.people.length && !answered.topics.length && !answered.groups.length && !answered.classrooms.length && !answered.resources.length
  useEffect(() => {
    if (!empty) return
    // The first settled value is the query as typed, before it is trimmed: the same search either way.
    const key = `${settled.trim().replace(/\s+/g, ' ')}\u0000${scopes?.join(',') ?? ''}`
    if (reported.current === key) return
    reported.current = key
    trackSearchNoResults(searchScopeOf(scopes), wordCountOf(settled))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [empty, settled])
  const [loadingMore, setLoadingMore] = useState(false)
  const more = async () => {
    if (!data?.notesCursor) return
    setLoadingMore(true)
    try {
      await result.fetchMore({
        variables: { ...variables, after: data.notesCursor },
        updateQuery: (previous, { fetchMoreResult }) => {
          const prev = previous as SearchQuery
          const next = fetchMoreResult as SearchQuery
          return { search: { ...prev.search, notes: [...prev.search.notes, ...next.search.notes], notesCursor: next.search.notesCursor } }
        },
      })
    } finally {
      setLoadingMore(false)
    }
  }
  return {
    notes: data?.notes ?? [],
    people: data?.people ?? [],
    topics: data?.topics ?? [],
    groups: data?.groups ?? [],
    classrooms: data?.classrooms ?? [],
    resources: data?.resources ?? [],
    hasMore: !!data?.notesCursor,
    more,
    loadingMore,
    loading: ready && result.loading,
    searched: ready && !!result.data,
    failed: ready && !result.loading && !result.data && !!result.error,
    retry: () => result.refetch(),
    settled,
  }
}
