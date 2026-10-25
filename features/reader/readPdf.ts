'use client'

import { useApolloClient } from '@apollo/client/react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { CreateNoteDocument, UpdateNoteDraftDocument } from '@/graphql/generated/graphql'
import { isLimitCode, refusalMessage } from '@/lib/limit-error'
import { UploadLimits } from '@/lib/contracts/domain/enums'
import { positionBetween } from '@/lib/contracts/validation'
import { mimeOf, uploadToNote, UploadError } from '@/features/notes/media'
import { newCardId } from '@/features/notes/model/doc'

/** A note's title from a PDF's file name: no extension, spaces for underscores. */
export function titleFromFileName(name: string): string {
  return name.replace(/\.pdf$/i, '').replace(/_+/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 200)
}

/**
 * "Read a PDF" (lvn-backend ADR-0040): a new private note holding the PDF in a file card, opened in the reader. The
 * upload reports its progress; a refusal (not a PDF, too large, storage full) comes back as `error`.
 */
export function useReadPdf() {
  const t = useTranslations('notes.home')
  const client = useApolloClient()
  const router = useRouter()
  const [uploading, setUploading] = useState<{ name: string; progress: number } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [limit, setLimit] = useState(false)

  const start = async (file: File, folderId?: string | null) => {
    setError(null)
    setLimit(false)
    if (mimeOf(file) !== 'application/pdf') return setError(t('readPdfNotPdf'))
    if (file.size > UploadLimits.document) return setError(t('readPdfTooLarge', { mb: UploadLimits.document / 1024 ** 2 }))
    setUploading({ name: file.name, progress: 0 })
    try {
      const created = await client.mutate({ mutation: CreateNoteDocument, variables: { input: { title: titleFromFileName(file.name), ...(folderId ? { folderId } : {}) } } })
      const problem = created.data?.createNote.userErrors[0]
      const noteId = created.data?.createNote.note?.id
      if (!noteId) throw new UploadError(problem?.message ?? t('readPdfFailed'), isLimitCode(problem?.code))
      const fileId = await uploadToNote(client, noteId, file, (progress) => setUploading({ name: file.name, progress }))
      const saved = await client.mutate({ mutation: UpdateNoteDraftDocument, variables: { input: { noteId, ops: [{ kind: 'UPSERT', id: newCardId(), type: 'file', position: positionBetween(null, null), content: { fileId } }] } } })
      const savedProblem = saved.data?.updateNoteDraft.userErrors[0]
      if (saved.data?.updateNoteDraft.userErrors.length) throw new UploadError(savedProblem!.message, isLimitCode(savedProblem?.code))
      router.push(`/notes/${noteId}/read/${fileId}`)
    } catch (e) {
      const refused = e instanceof UploadError ? e.message : refusalMessage(e)
      setLimit(Boolean((e instanceof UploadError && e.limit) || refusalMessage(e)))
      setError(refused ?? t('readPdfFailed'))
    } finally {
      setUploading(null)
    }
  }
  return { start, uploading, error, limit }
}
