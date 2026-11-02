'use client'

import { useApolloClient } from '@apollo/client/react'
import { useRef, useState } from 'react'
import { CreateNoteDocument, MakeNotesFromTranscriptDocument } from '@/graphql/generated/graphql'

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
      const made = await client.mutate({
        mutation: MakeNotesFromTranscriptDocument,
        variables: { input: { noteId: noteId.current, transcript: text.trim() || title } },
      })
      const payload = made.data?.makeNotesFromTranscript
      const problem = payload?.userErrors[0]?.message
      const notes = payload?.notes
      if (problem || !notes) setError(problem ?? 'The note could not be started.')
      else setResult([notes.title, notes.summary].filter(Boolean).join('\n\n') || 'Notes are ready.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'That did not work. Try again.')
    } finally {
      setBusy(false)
    }
  }

  return { ask, busy, error, result }
}
