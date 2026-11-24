'use client'

import { NodeViewWrapper, type ReactNodeViewProps } from '@tiptap/react'
import { FileUp, ImagePlus, Mic, RefreshCw, Video } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useId, useRef, useState } from 'react'
import { inlineText } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { LimitNotice } from '@/components/ui/limit-notice'
import { refusalMessage } from '@/lib/limit-error'
import { acceptFor, pendingFiles, UploadError, useMedia, type MediaCardType } from '../media'
import { MediaBlock, type MediaContent } from '../render/MediaBlock'
import { writeCard } from './views'
import { useUploadsEnabled } from '../uploads'

const ICONS = { image: ImagePlus, video: Video, audio: Mic, file: FileUp } as const

/**
 * The editor's picture, video, audio and file card: a place to choose or drop a file, its progress while it uploads,
 * then the file itself with its description and caption. Files dropped or pasted into the note arrive through
 * `pendingFiles` under the card's `upload` key; a card made from a menu opens the file picker (`upload: 'pick'`).
 */
export function MediaView({ node, updateAttributes, selected, editor, getPos }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const media = useMedia()
  const type = node.attrs.cardType as MediaCardType
  const data = (node.attrs.data ?? null) as MediaContent | null
  const latest = useRef(node)
  latest.current = node
  const input = useRef<HTMLInputElement>(null)
  const [progress, setProgress] = useState<{ name: string; value: number } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [limit, setLimit] = useState(false)
  const [over, setOver] = useState(false)
  const altId = useId()
  const captionId = useId()
  const Icon = ICONS[type]
  const uploadsOn = useUploadsEnabled()

  const start = useCallback(
    async (file: File) => {
      setError(null)
      setLimit(false)
      setProgress({ name: file.name, value: 0 })
      try {
        const fileId = await media.upload(file, (value) => setProgress({ name: file.name, value }))
        const current = (latest.current.attrs.data ?? {}) as MediaContent
        updateAttributes({ data: { ...current, fileId, ...(type === 'image' ? { alt: current.alt ?? '' } : {}) }, upload: null })
      } catch (e) {
        // The API's words when it refused the file (too big, a plan limit); ours for network trouble.
        const refused = e instanceof UploadError && !/^(network|storage answered)/.test(e.message) ? e.message : refusalMessage(e)
        setLimit(Boolean((e instanceof UploadError && e.limit) || refusalMessage(e)))
        setError(refused ?? t('media.failed'))
      } finally {
        setProgress(null)
      }
    },
    [media, t, type, updateAttributes],
  )

  useEffect(() => {
    const key = latest.current.attrs.upload as string | null
    if (!key) return
    if (key === 'pick') {
      updateAttributes({ upload: null })
      input.current?.click()
      return
    }
    const file = pendingFiles.get(key)
    pendingFiles.delete(key)
    if (file) void start(file)
    else updateAttributes({ upload: null })
    // Once, when the card appears.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Onto the card's data as it is now, so a quick second edit keeps the first (see writeCard).
  const set = (patch: Partial<MediaContent>) => writeCard<MediaContent | null>({ editor, getPos, node }, (d) => ({ ...(d as MediaContent), ...patch }))
  const pick = (
    <input
      ref={input}
      type="file"
      accept={acceptFor(type)}
      className="sr-only"
      tabIndex={-1}
      aria-hidden
      onChange={(e) => {
        const file = e.target.files?.[0]
        e.target.value = ''
        if (file) void start(file)
      }}
    />
  )

  return (
    <NodeViewWrapper className={cn('lvn-card rounded-2xl border bg-surface p-3', selected ? 'border-accent ring-2 ring-accent/30' : 'border-border')} data-card={type}>
      <div contentEditable={false} className="flex flex-col gap-3">
        {uploadsOn ? pick : null}
        {progress ? (
          <div role="status" className="flex flex-col gap-2 rounded-xl bg-surface-2 px-4 py-5">
            <p className="truncate text-sm font-medium">{t('media.uploading', { name: progress.name })}</p>
            <div className="h-2 overflow-hidden rounded-full bg-border" aria-hidden>
              <div className="h-full rounded-[10px] bg-accent transition-[width] duration-200" style={{ width: `${Math.round(progress.value * 100)}%` }} />
            </div>
            <p className="text-xs text-muted">{Math.round(progress.value * 100)}%</p>
          </div>
        ) : data?.fileId ? (
          <>
            <MediaBlock type={type} content={data} editing />
            {editor.isEditable ? (
              <div className="grid gap-2 sm:grid-cols-[1fr_auto] sm:items-end">
                <div className="flex flex-col gap-2">
                  {type === 'image' ? (
                    <label htmlFor={altId} className="flex flex-col gap-1">
                      <span className="text-xs font-semibold text-muted">{t('media.alt')}</span>
                      <input id={altId} className="rounded-lg border border-border bg-bg px-2.5 py-1.5 text-sm focus-visible:border-accent focus-visible:outline-none" value={data.alt ?? ''} maxLength={500} onChange={(e) => set({ alt: e.target.value })} />
                    </label>
                  ) : null}
                  <label htmlFor={captionId} className="flex flex-col gap-1">
                    <span className="text-xs font-semibold text-muted">{t('media.caption')}</span>
                    <input
                      id={captionId}
                      className="rounded-lg border border-border bg-bg px-2.5 py-1.5 text-sm focus-visible:border-accent focus-visible:outline-none"
                      value={data.caption ? inlineText(data.caption) : ''}
                      onChange={(e) => set({ caption: e.target.value ? [{ type: 'text', text: e.target.value }] : undefined })}
                    />
                  </label>
                </div>
                {uploadsOn ? (
                  <button type="button" className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-border px-3 py-1.5 text-sm text-muted hover:border-accent hover:text-accent" onClick={() => input.current?.click()}>
                    <RefreshCw className="size-4" aria-hidden />
                    {t('media.replace')}
                  </button>
                ) : null}
              </div>
            ) : null}
          </>
        ) : !uploadsOn ? (
          // Uploads are off (lvn-backend ADR-0097): an empty media card says so instead of offering a picker.
          <p className="flex flex-col items-center gap-2 rounded-xl border-2 border-dashed border-border px-4 py-8 text-center text-sm text-muted">
            <Icon className="size-6" aria-hidden />
            {t('media.uploadsOff')}
          </p>
        ) : (
          <button
            type="button"
            className={cn('flex flex-col items-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 text-center transition', over ? 'border-accent bg-accent-soft' : 'border-border hover:border-accent/60 hover:bg-surface-2')}
            onClick={() => input.current?.click()}
            onDragOver={(e) => {
              e.preventDefault()
              e.stopPropagation()
              setOver(true)
            }}
            onDragLeave={() => setOver(false)}
            onDrop={(e) => {
              e.preventDefault()
              e.stopPropagation()
              setOver(false)
              const file = e.dataTransfer.files[0]
              if (file) void start(file)
            }}
          >
            <span className="grid size-12 place-items-center rounded-2xl bg-accent-soft text-accent">
              <Icon className="size-6" aria-hidden />
            </span>
            <span className="font-semibold">{t(`media.choose.${type}`)}</span>
            <span className="text-xs text-muted">{t(`media.limits.${type}`)}</span>
          </button>
        )}
        {error ? limit ? <LimitNotice>{error}</LimitNotice> : (
          <p role="alert" className="text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        ) : null}
      </div>
    </NodeViewWrapper>
  )
}
