'use client'

import { BookOpenText, Download, FileText, ImageOff } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import type { Inline } from '@/lib/contracts/validation'
import { safeLinkHref } from '@/lib/http-url'
import { formatBytes, srcSetOf, useMedia, type MediaCardType } from '../media'
import { InlineText } from './RichText'

export interface MediaContent {
  fileId?: string
  alt?: string
  caption?: Inline
}

/** A picture, video, audio or file card as people see it; the read URL comes from the page's media (../media). */
export function MediaBlock({ type, content, editing }: { type: MediaCardType; content: MediaContent; editing?: boolean }) {
  const t = useTranslations('notes.editor.media')
  const store = useMedia()
  const file = store.get(content.fileId)
  const caption = !editing && content.caption?.length ? (
    <figcaption className="mt-2 text-center text-sm text-muted">
      <InlineText content={content.caption} />
    </figcaption>
  ) : null
  if (!file && store.loading) return <div aria-hidden className="h-48 animate-pulse rounded-xl bg-surface-2" />
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
          <img
            src={file.mediumUrl ?? file.url}
            srcSet={srcSetOf(file)}
            sizes="(min-width: 48rem) 48rem, 100vw"
            width={file.width ?? undefined}
            height={file.height ?? undefined}
            alt={content.alt ?? ''}
            loading="lazy"
            className="mx-auto max-h-[70vh] w-auto rounded-xl object-contain shadow-sm"
          />
          {caption}
        </figure>
      )
    case 'video':
      return (
        <figure>
          <video src={file.playbackUrl ?? file.url} poster={file.posterUrl ?? undefined} controls preload="metadata" playsInline className="w-full rounded-xl bg-black shadow-sm" />
          {caption}
        </figure>
      )
    case 'audio':
      return (
        <figure className="rounded-xl border border-border bg-surface-2 p-3">
          <p className="mb-2 truncate text-sm font-medium">{file.fileName}</p>
          <audio src={file.playbackUrl ?? file.url} controls preload="metadata" className="w-full" />
          {caption}
        </figure>
      )
    default: {
      const reader = file.mimeType === 'application/pdf' && content.fileId ? store.readerHref?.(content.fileId) : undefined
      return (
        <figure className="flex flex-col gap-2">
          {reader ? (
            <Link href={reader} className="flex items-center gap-3 rounded-xl bg-accent px-4 py-3 font-semibold text-accent-fg shadow-md shadow-accent/20 transition hover:bg-accent/90">
              <BookOpenText className="size-5 shrink-0" aria-hidden />
              <span className="flex min-w-0 flex-col">
                <span>{t('read')}</span>
                <span className="text-xs font-normal opacity-85">{t('readLead')}</span>
              </span>
            </Link>
          ) : null}
          <FileLink url={file.url} name={file.fileName} detail={`${formatBytes(file.sizeBytes)}${file.pageCount ? ` · ${t('pages', { count: file.pageCount })}` : ''}`} open={t('open')} />
          {caption}
        </figure>
      )
    }
  }
}

/** The file's read URL. A non-http(s) value is shown, not followed. */
function FileLink({ url, name, detail, open }: { url: string; name: string; detail: string; open: string }) {
  const href = safeLinkHref(url)
  const body = (
    <>
      <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent">
        <FileText className="size-5" aria-hidden />
      </span>
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="truncate font-medium">{name}</span>
        <span className="text-xs text-muted">{detail}</span>
      </span>
      <span className="inline-flex items-center gap-1 rounded-full bg-surface-2 px-3 py-1 text-sm text-muted group-hover:text-accent">
        <Download className="size-4" aria-hidden />
        {open}
      </span>
    </>
  )
  const className = 'lvn-chip group flex items-center gap-3 rounded-xl border border-border bg-surface p-3 transition hover:border-accent/50 hover:shadow-md'
  if (!href) return <div className={className}>{body}</div>
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={className}>
      {body}
    </a>
  )
}
