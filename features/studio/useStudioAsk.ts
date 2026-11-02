'use client'

import { useApolloClient } from '@apollo/client/react'
import { useRef, useState } from 'react'
import { makeNotesFromTranscript } from '@/features/beta/api'
import { CreateNoteDocument } from '@/graphql/generated/graphql'

/** Ask AI from a studio page: one note for that page, then notes made from what is on the page. */
export function useStudioAsk(title: string, text: string) {
  const client = useApolloClient()
  const noteId = useRef<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<string | null>(null)

  const ask = async () => {
    setBusy(true)
    setError(null)
    try {
      if (!noteId.current) {
        const created = await client.mutate({ mutation: CreateNoteDocument, variables: { input: { title } } })
        const problem = created.data?.createNote.userErrors[0]?.message
        const id = created.data?.createNote.note?.id
        if (!id) {
          setError(problem ?? 'The note could not be started.')
          return
        }
        noteId.current = id
      }
      const made = await makeNotesFromTranscript(client, noteId.current, text.trim() || title)
      const problem = made.userErrors?.[0]?.message
      if (problem) setError(problem)
      else setResult(made.markdown?.trim() || 'Notes are ready.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'That did not work. Try again.')
    } finally {
      setBusy(false)
    }
  }

  return { ask, busy, error, result }
}
