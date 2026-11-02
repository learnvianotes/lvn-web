'use client'

import { useApolloClient } from '@apollo/client/react'
import { useEffect, useState } from 'react'
import { loadForkState } from '@/features/beta/api'

/** allowForks from contracts 0.74.0, with forkingEnabled until that field answers. */
export function useAllowForks(noteId: string, fallback: boolean) {
  const client = useApolloClient()
  const [allow, setAllow] = useState<boolean | null>(null)
  const [forkCount, setForkCount] = useState(0)
  useEffect(() => {
    let cancel = false
    void loadForkState(client, noteId)
      .then((state) => {
        if (cancel || !state) return
        setAllow(state.allowForks)
        setForkCount(state.forkCount)
      })
      .catch(() => undefined)
    return () => {
      cancel = true
    }
  }, [client, noteId])
  return { allowForks: allow ?? fallback, forkCount }
}
