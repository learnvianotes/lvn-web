'use client'

import { useQuery } from '@apollo/client/react'
import { useEffect, useState } from 'react'
import { SearchDocument, type NoteKind, type NoteSource, type SearchQuery, type SearchScope } from '@/graphql/generated/graphql'
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
 * themselves are not sent.
 */
export function useSearch(query: string, first: number, filters: SearchFilters = {}, scopes?: SearchScope[]) {
  const [settled, setSettled] = useState(query)
  useEffect(() => {
    const timer = setTimeout(() => setSettled(query.trim()), 200)
    return () => clearTimeout(timer)
  }, [query])
  useEffect(() => {
    if (settled.length < 2) return
    const timer = setTimeout(() => track('SEARCH_PERFORMED', { metadata: { scopes: scopes?.join(',') ?? 'ALL', words: settled.split(/\s+/).length } }), 2_000)
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
