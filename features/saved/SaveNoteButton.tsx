'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Bookmark, BookmarkCheck } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { Button } from '@/components/ui/button'
import { NoteSavedDocument, SaveNoteDocument, UnsaveNoteDocument } from '@/graphql/generated/graphql'
import { useSession } from '@/state/session'

/**
 * Save on a note (lvn-backend ADR-0076): to the viewer's Bookmarks, private to them. Visitors are asked to sign in and
 * come back to it.
 */
/** `saved`: already known (a feed's card), so nothing more is asked. */
export function SaveNoteButton({ noteId, saved }: { noteId: string; saved?: boolean }) {
  const t = useTranslations('saved')
  const status = useSession((s) => s.status)
  const path = usePathname()
  const signedIn = status === 'signed-in'
  const { data } = useQuery(NoteSavedDocument, { variables: { id: noteId }, skip: !signedIn || saved !== undefined })
  const [save, saving] = useMutation(SaveNoteDocument)
  const [unsave, unsaving] = useMutation(UnsaveNoteDocument)
  if (!signedIn) {
    return (
      <Link href={`/sign-in?next=${encodeURIComponent(path)}`} className="inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-sm font-semibold text-accent hover:underline">
        <Bookmark className="size-4" aria-hidden />
        {t('save')}
      </Link>
    )
  }
  const viewerSaved = saved ?? data?.note?.viewerSaved
  if (viewerSaved === undefined) return null
  const note = { viewerSaved }
  const Icon = note.viewerSaved ? BookmarkCheck : Bookmark
  return (
    <Button
      type="button"
      size="sm"
      variant="secondary"
      aria-pressed={note.viewerSaved}
      title={t('hint')}
      disabled={saving.loading || unsaving.loading}
      className="gap-1.5"
      onClick={() => void (note.viewerSaved ? unsave : save)({ variables: { noteId } })}
    >
      <Icon className={note.viewerSaved ? 'size-4 text-accent' : 'size-4'} aria-hidden />
      {note.viewerSaved ? t('savedOne') : t('save')}
    </Button>
  )
}

/** The same on a public note's page, which renders without the app's providers. */
export function PublicSaveNoteButton({ noteId }: { noteId: string }) {
  return (
    <AuthProvider>
      <SaveNoteButton noteId={noteId} />
    </AuthProvider>
  )
}
