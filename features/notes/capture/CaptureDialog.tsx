'use client'

import { useApolloClient } from '@apollo/client/react'
import { FileText, ImagePlus, X } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { CreateNoteDocument, RunAiTaskDocument, UpdateNoteDraftDocument } from '@/graphql/generated/graphql'
import { isLimitCode, refusalMessage } from '@/lib/limit-error'
import { QuickNoteLimits } from '@/lib/contracts/domain/enums'
import { positionBetween } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { mimeOf, uploadToNote, UploadError } from '@/features/notes/media'
import { newCardId } from '@/features/notes/model/doc'
import { compressPicture } from './compress'
import { addToTray, sizeLabel, type TrayItem } from './tray'
import { useFeatureUse } from '@/lib/analytics'

type Busy = { adding: true } | { upload: number; of: number; progress: number } | { making: true } | null

let next = 0
const key = () => `t${Date.now()}-${next++}`

/**
 * Notes from photos and PDFs (lvn-backend ADR-0084): a tray filled by choosing or dropping files, up to
 * QuickNoteLimits.files. Pictures are made smaller in the browser as they are added; a PDF over the limit is turned
 * away with its size. Make notes puts them all in a new note, uploads each with progress, has AI make one note of them
 * and opens it with the AI panel. A failed upload keeps the tray: trying again carries on where it stopped.
 */
export function CaptureDialog({ open, onClose, folderId }: { open: boolean; onClose: () => void; folderId?: string | null }) {
  const t = useTranslations('notes.capture')
  useFeatureUse(open ? 'quick_capture' : null)
  const client = useApolloClient()
  const router = useRouter()
  const input = useRef<HTMLInputElement>(null)
  const [items, setItems] = useState<TrayItem[]>([])
  const [busy, setBusy] = useState<Busy>(null)
  const [problems, setProblems] = useState<string[]>([])
  const [dragging, setDragging] = useState(false)
  /** The note made by the first Make notes, the items already in it as cards, and the last card's position. */
  const made = useRef<{ noteId: string; carded: Set<string>; last: string | null } | null>(null)
  const full = items.length >= QuickNoteLimits.files
  const total = items.reduce((sum, i) => sum + i.file.size, 0)

  // Previews are object URLs: let them go with the tray.
  const previews = useRef(new Set<string>())
  useEffect(() => () => previews.current.forEach((url) => URL.revokeObjectURL(url)), [])

  const add = async (files: File[]) => {
    if (!files.length) return
    setProblems([])
    setBusy({ adding: true })
    const added: TrayItem[] = []
    const bad: string[] = []
    for (const file of files) {
      const mime = mimeOf(file)
      if (mime === 'application/pdf') added.push({ key: key(), file, kind: 'pdf', preview: null })
      else if (mime.startsWith('image/')) {
        try {
          const small = await compressPicture(file)
          const preview = URL.createObjectURL(small)
          previews.current.add(preview)
          added.push({ key: key(), file: small, kind: 'image', preview })
        } catch {
          bad.push(t('unreadable', { name: file.name }))
        }
      } else bad.push(t('notSupported', { name: file.name }))
    }
    const { tray, refused } = addToTray(items, added)
    setItems(tray)
    setProblems([...bad, ...refused.map((r) => (r.reason === 'pdfTooLarge' ? t('pdfTooLarge', { name: r.name, size: r.size, mb: QuickNoteLimits.pdfBytes / 1024 ** 2 }) : t('tooMany', { max: QuickNoteLimits.files, left: r.left })))])
    setBusy(null)
  }

  const remove = (item: TrayItem) => {
    if (item.preview) {
      URL.revokeObjectURL(item.preview)
      previews.current.delete(item.preview)
    }
    setItems((all) => all.filter((x) => x.key !== item.key))
  }

  const make = async () => {
    setProblems([])
    try {
      if (!made.current) {
        setBusy({ upload: 0, of: items.length, progress: 0 })
        const when = new Date().toLocaleString([], { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' })
        const created = await client.mutate({ mutation: CreateNoteDocument, variables: { input: { title: t('noteTitle', { when }), ...(folderId ? { folderId } : {}) } } })
        const createdProblem = created.data?.createNote.userErrors[0]
        const noteId = created.data?.createNote.note?.id
        if (!noteId) throw new UploadError(createdProblem?.message ?? t('failed'), isLimitCode(createdProblem?.code))
        made.current = { noteId, carded: new Set(), last: null }
      }
      const state = made.current
      const list = [...items]
      for (const [i, item] of list.entries()) {
        if (item.fileId) continue
        setBusy({ upload: i + 1, of: list.length, progress: 0 })
        const fileId = await uploadToNote(client, state.noteId, item.file, (progress) => setBusy({ upload: i + 1, of: list.length, progress }))
        list[i] = { ...item, fileId }
        setItems([...list])
      }
      let last = state.last
      const ops = list.filter((item) => !state.carded.has(item.key)).map((item) => {
        last = positionBetween(last, null)
        return { kind: 'UPSERT' as const, id: newCardId(), type: item.kind === 'pdf' ? ('file' as const) : ('image' as const), position: last, content: item.kind === 'pdf' ? { fileId: item.fileId } : { fileId: item.fileId, alt: '' } }
      })
      if (ops.length) {
        const saved = await client.mutate({ mutation: UpdateNoteDraftDocument, variables: { input: { noteId: state.noteId, ops } } })
        const savedProblem = saved.data?.updateNoteDraft.userErrors[0]
        if (saved.data?.updateNoteDraft.userErrors.length) throw new UploadError(savedProblem!.message, isLimitCode(savedProblem?.code))
        list.forEach((item) => state.carded.add(item.key))
        state.last = last
      }
      setBusy({ making: true })
      // AI's answer (or why it cannot) shows in the note's AI panel.
      await client.mutate({ mutation: RunAiTaskDocument, variables: { input: { noteId: state.noteId, task: 'QUICK_NOTE' } } })
      router.push(`/notes/${state.noteId}?ai=1`)
    } catch (e) {
      const refused = e instanceof UploadError && !/^(network|storage answered)/.test(e.message) ? e.message : refusalMessage(e)
      setProblems([refused ?? t('failed')])
      setBusy(null)
    }
  }

  return (
    <Dialog open={open} onClose={() => (busy ? undefined : onClose())} title={t('title')} wide>
      <div className="flex flex-col gap-4">
        <p className="text-sm text-muted">{t('lead', { max: QuickNoteLimits.files, mb: QuickNoteLimits.pdfBytes / 1024 ** 2 })}</p>
        <input
          ref={input}
          type="file"
          multiple
          accept="image/*,application/pdf,.pdf"
          className="sr-only"
          tabIndex={-1}
          aria-label={t('choose')}
          data-testid="capture-input"
          onChange={(e) => {
            const files = Array.from(e.target.files ?? [])
            e.target.value = ''
            void add(files)
          }}
        />
        <button
          type="button"
          disabled={full || !!busy}
          onClick={() => input.current?.click()}
          onDragOver={(e) => {
            e.preventDefault()
            setDragging(true)
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={(e) => {
            e.preventDefault()
            setDragging(false)
            if (!full && !busy) void add(Array.from(e.dataTransfer.files))
          }}
          className={cn('flex flex-col items-center gap-2 rounded-2xl border-2 border-dashed border-border px-4 py-8 text-center transition-colors hover:border-accent hover:bg-accent-soft disabled:pointer-events-none disabled:opacity-50', dragging && 'border-accent bg-accent-soft')}
        >
          <ImagePlus className="size-7 text-accent" aria-hidden />
          <span className="font-semibold">{full ? t('full') : t('choose')}</span>
          <span className="text-xs text-muted">{t('drop')}</span>
        </button>
        <div className="flex items-center justify-between text-sm">
          <span className="font-semibold">{t('count', { n: items.length, max: QuickNoteLimits.files })}</span>
          {items.length ? <span className="text-muted">{sizeLabel(total)}</span> : null}
        </div>
        {busy && 'adding' in busy ? <p className="text-sm text-muted">{t('adding')}</p> : null}
        {items.length ? (
          <ul aria-label={t('tray')} className="grid grid-cols-3 gap-3 sm:grid-cols-5">
            {items.map((item, i) => (
              <li key={item.key} className="flex flex-col gap-1">
                <div className="relative aspect-[3/4] overflow-hidden rounded-xl border border-border bg-surface-2">
                  {item.preview ? (
                    // eslint-disable-next-line @next/next/no-img-element -- a local object URL, not an optimisable image
                    <img src={item.preview} alt={t('photoN', { n: items.slice(0, i + 1).filter((x) => x.kind === 'image').length })} className="size-full object-cover" />
                  ) : (
                    <div className="flex size-full items-center justify-center">
                      <FileText className="size-8 text-muted" aria-hidden />
                    </div>
                  )}
                  <button type="button" disabled={!!busy} onClick={() => remove(item)} aria-label={t('remove', { name: item.file.name })} className="absolute right-1 top-1 rounded-full bg-bg/90 p-1 hover:bg-bg disabled:opacity-50">
                    <X className="size-3.5" aria-hidden />
                  </button>
                </div>
                <span className="truncate text-xs">{item.kind === 'pdf' ? item.file.name : t('photoN', { n: items.slice(0, i + 1).filter((x) => x.kind === 'image').length })}</span>
                <span className="text-xs text-muted">{item.fileId ? t('uploaded') : sizeLabel(item.file.size)}</span>
              </li>
            ))}
          </ul>
        ) : null}
        {problems.length ? (
          <div role="alert" className="flex flex-col gap-1 text-sm text-bad">
            {problems.map((p) => (
              <p key={p}>{p}</p>
            ))}
          </div>
        ) : null}
        {busy && 'upload' in busy ? (
          <div className="flex flex-col gap-1.5" role="status">
            <span className="text-sm">{busy.upload ? t('uploading', { n: busy.upload, of: busy.of }) : t('creating')}</span>
            <span className="block h-1.5 overflow-hidden rounded-full bg-surface-2">
              <span className="block h-full rounded-[10px] bg-accent transition-[width]" style={{ width: `${Math.round(((Math.max(0, busy.upload - 1) + busy.progress) / Math.max(1, busy.of)) * 100)}%` }} />
            </span>
          </div>
        ) : null}
        {busy && 'making' in busy ? (
          <p role="status" className="text-sm">
            {t('making')}
          </p>
        ) : null}
        <div className="flex justify-end gap-2">
          <Button variant="secondary" disabled={!!busy} onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button disabled={!items.length || !!busy} onClick={() => void make()}>
            {items.length ? t('makeN', { n: items.length }) : t('make')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
