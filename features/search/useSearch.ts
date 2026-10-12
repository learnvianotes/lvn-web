'use client'

import { useQuery } from '@apollo/client/react'
import { useEffect, useState } from 'react'
import { SearchDocument } from '@/graphql/generated/graphql'

/** Search as you type: asks the API 200 ms after the last keystroke, from two characters on. */
export function useSearch(query: string, first: number) {
  const [settled, setSettled] = useState(query)
  useEffect(() => {
    const timer = setTimeout(() => setSettled(query.trim()), 200)
    return () => clearTimeout(timer)
  }, [query])
  const ready = settled.length >= 2
  const result = useQuery(SearchDocument, { variables: { query: settled, first }, skip: !ready, fetchPolicy: 'cache-first' })
  const data = ready ? (result.data ?? result.previousData)?.search : undefined
  return { notes: data?.notes ?? [], people: data?.people ?? [], topics: data?.topics ?? [], loading: ready && result.loading, searched: ready && !!result.data, settled }
}
