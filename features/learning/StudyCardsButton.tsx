'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { GraduationCap } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { NoteStudyingDocument, StopStudyingNoteCardsDocument, StudyNoteCardsDocument } from '@/graphql/generated/graphql'

/**
 * "Study these cards" on a note the person reads (lvn-backend ADR-0068): its flashcards join their reviews, read as the
 * note is published; they can stop. Their own notes' flashcards are always in their reviews.
 */
export function StudyCardsButton({ noteId }: { noteId: string }) {
  const t = useTranslations('review')
  const { data } = useQuery(NoteStudyingDocument, { variables: { id: noteId } })
  const studying = data?.note?.viewerStudying
  const refresh = { refetchQueries: [{ query: NoteStudyingDocument, variables: { id: noteId } }], awaitRefetchQueries: true }
  const [study, starting] = useMutation(StudyNoteCardsDocument, refresh)
  const [stop, stopping] = useMutation(StopStudyingNoteCardsDocument, refresh)
  if (studying === undefined || studying === null) return null
  if (studying) {
    return (
      <span className="inline-flex items-center gap-2 text-sm">
        <Link href="/review" className="inline-flex items-center gap-1.5 font-medium text-accent hover:underline">
          <GraduationCap className="size-4" aria-hidden />
          {t('studying')}
        </Link>
        <Button size="sm" variant="ghost" disabled={stopping.loading} onClick={() => void stop({ variables: { input: { noteId } } })}>
          {t('stopStudying')}
        </Button>
      </span>
    )
  }
  return (
    <Button size="sm" variant="secondary" disabled={starting.loading} onClick={() => void study({ variables: { input: { noteId } } })}>
      <GraduationCap className="size-4" aria-hidden />
      {t('study')}
    </Button>
  )
}
