'use client'

import { ChevronRight } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import type { NoteMeta } from '../api'

/**
 * Board A's breadcrumb (lvn-backend ADR-0076): subject › topic › note, from the note's first topic; the topic opens its
 * notes on /search. A note without a topic shows where it lives instead: the person's notes, or its author's.
 */
export function Breadcrumb({ meta, own }: { meta: Pick<NoteMeta, 'title' | 'topics'> & { owner: { displayName: string; handle: string } }; own: boolean }) {
  const t = useTranslations('notes')
  const topic = meta.topics?.[0]
  const title = meta.title || t('editor.untitled')
  return (
    <nav aria-label={t('view.breadcrumb')} className="min-w-0">
      <ol className="flex min-w-0 items-center gap-1 text-sm text-muted">
        {topic ? (
          <>
            <li className="hidden shrink-0 sm:block">{topic.subject.title}</li>
            <li aria-hidden className="hidden sm:block">
              <ChevronRight className="size-3.5" />
            </li>
            <li className="shrink-0">
              <Link href={`/search?${new URLSearchParams({ topic: topic.id, topicTitle: topic.title }).toString()}`} className="rounded px-1 hover:bg-surface-2 hover:text-fg">
                {topic.title}
              </Link>
            </li>
          </>
        ) : (
          <li className="shrink-0">
            <Link href={own ? '/notes' : `/u/${meta.owner.handle}`} className="rounded px-1 hover:bg-surface-2 hover:text-fg">
              {own ? t('view.myNotes') : meta.owner.displayName}
            </Link>
          </li>
        )}
        <li aria-hidden>
          <ChevronRight className="size-3.5" />
        </li>
        <li aria-current="page" className="min-w-0 truncate font-medium text-fg">
          {title}
        </li>
      </ol>
    </nav>
  )
}
