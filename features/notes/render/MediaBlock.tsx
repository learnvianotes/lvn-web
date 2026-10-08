'use client'

import { Download, FileText, ImageOff } from 'lucide-react'
import { useTranslations } from 'next-intl'
import type { Inline } from '@/lib/contracts/validation'
import { formatBytes, useMedia, type MediaCardType } from '../media'
import { InlineText } from './RichText'

export interface MediaContent {
  fileId?: string
  alt?: string
  caption?: Inline
}

/** A picture, video, audio or file card as people see it; the read URL comes from the page's media (../media). */
export function MediaBlock({ type, content, editing }: { type: MediaCardType; content: MediaContent; editing?: boolean }) {
  const t = useTranslations('notes.editor.media')
  const file = useMedia().get(content.fileId)
  const caption = !editing && content.caption?.length ? (
    <figcaption className="mt-2 text-center text-sm text-muted">
      <InlineText content={content.caption} />
    </figcaption>
  ) : null
  if (!file) {
    return (
      <p className="flex items-center gap-2 rounded-xl border border-dashed border-border px-4 py-6 text-sm text-muted">
        <ImageOff className="size-4" aria-hidden />
        {t('unavailable')}
      </p>
    )
  }
  switch (type) {
    case 'image':
      return (
        <figure>
          {/* eslint-disable-next-line @next/next/no-img-element -- short-lived storage URLs, not for next/image */}
          <img src={file.url} alt={content.alt ?? ''} loading="lazy" className="mx-auto max-h-[70vh] w-auto rounded-xl object-contain shadow-sm" />
          {caption}
        </figure>
      )
    case 'video':
      return (
        <figure>
          <video src={file.url} controls preload="metadata" playsInline className="w-full rounded-xl bg-black shadow-sm" />
          {caption}
        </figure>
      )
    case 'audio':
      return (
        <figure className="rounded-xl border border-border bg-surface-2 p-3">
          <p className="mb-2 truncate text-sm font-medium">{file.fileName}</p>
          <audio src={file.url} controls preload="metadata" className="w-full" />
          {caption}
        </figure>
      )
    default:
      return (
        <figure>
          <a href={file.url} target="_blank" rel="noopener noreferrer" className="lvn-chip group flex items-center gap-3 rounded-xl border border-border bg-surface p-3 transition hover:border-accent/50 hover:shadow-md">
            <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent">
              <FileText className="size-5" aria-hidden />
            </span>
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="truncate font-medium">{file.fileName}</span>
              <span className="text-xs text-muted">{formatBytes(file.sizeBytes)}</span>
            </span>
            <span className="inline-flex items-center gap-1 rounded-full bg-surface-2 px-3 py-1 text-sm text-muted group-hover:text-accent">
              <Download className="size-4" aria-hidden />
              {t('open')}
            </span>
          </a>
          {caption}
        </figure>
      )
  }
}
