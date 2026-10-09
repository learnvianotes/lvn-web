'use client'

import { ArrowLeft, Clock } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useState } from 'react'
import { cardPlainText } from '@/lib/contracts/validation'
import type { NoteMeta } from './api'
import { accentOf, readingMinutes } from './look'
import { ReadAloudControls } from './ReadAloudControls'
import { ReportButton } from '@/features/moderation/ReportDialog'
import { ForkCredit, MakeCopyButton, useMakeCopy } from './ShareDialog'
import type { StoredCard } from './model/doc'
import { useReadAloud } from './readAloud'
import { CardView } from './render/CardView'

/** A note the viewer can read but not edit: its published version, with an outline and read aloud. */
export function NoteReader({ meta, cards }: { meta: NoteMeta; cards: StoredCard[] }) {
  const t = useTranslations('notes')
  const router = useRouter()
  const spoken = useCallback(() => cards.map((c) => ({ id: c.id, text: cardPlainText(c.type, c.content) })), [cards])
  const reader = useReadAloud(spoken)
  const copy = useMakeCopy(meta.id)
  const headings = cards.filter((c) => c.type === 'heading')
  const minutes = readingMinutes(cards.map((c) => cardPlainText(c.type, c.content)).join(' '))
  const accent = accentOf(meta.id)
  const [progress, setProgress] = useState(0)
  useEffect(() => {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight
      setProgress(max > 0 ? Math.min(1, window.scrollY / max) : 1)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])
  return (
    <div className="grid gap-6 lg:grid-cols-[13rem_minmax(0,1fr)]">
      <div aria-hidden className="fixed inset-x-0 top-0 z-50 h-1 origin-left bg-accent transition-transform duration-150" style={{ transform: `scaleX(${progress})` }} />
      <nav aria-label={t('editor.outline')} className="hidden lg:block">
        <div className="sticky top-20 flex flex-col gap-1">
          {headings.map((h) => (
            <a key={h.id} href={`#card-${h.id}`} className="truncate rounded-md px-2 py-1 text-sm text-muted hover:bg-surface-2 hover:text-fg">
              {cardPlainText('heading', h.content) || t('editor.untitledHeading')}
            </a>
          ))}
        </div>
      </nav>
      <article className="flex min-w-0 flex-col gap-4">
        <Link href="/notes" className="inline-flex w-fit items-center gap-1.5 rounded-full px-2 py-1 text-sm text-muted transition hover:bg-surface-2 hover:text-fg">
          <ArrowLeft className="size-4" aria-hidden />
          {t('backToNotes')}
        </Link>
        <header className="flex animate-rise flex-col gap-3">
          <h1 className="text-3xl font-extrabold leading-tight tracking-tight sm:text-[2.6rem]">{meta.title || t('editor.untitled')}</h1>
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted">
            <span className="flex items-center gap-2">
              <span className="grid size-8 place-items-center rounded-full text-sm font-bold text-white" style={{ background: `linear-gradient(135deg, ${accent.from}, ${accent.to})` }} aria-hidden>
                {meta.owner.displayName.charAt(0).toUpperCase()}
              </span>
              {t('reader.by', { name: meta.owner.displayName })}
            </span>
            {meta.publishedAt ? <span>· {t('reader.published', { date: new Date(meta.publishedAt).toLocaleDateString() })}</span> : null}
            {minutes ? (
              <span className="inline-flex items-center gap-1">
                · <Clock className="size-3.5" aria-hidden /> {t('editor.readingTime', { n: minutes })}
              </span>
            ) : null}
          </div>
          {meta.forkedFrom ? <ForkCredit credit={meta.forkedFrom} /> : null}
          <div className="flex flex-wrap items-center gap-2">
            <ReadAloudControls reader={reader} />
            {meta.viewerCan.fork ? <MakeCopyButton copy={copy} /> : null}
            <ReportButton entityType="NOTE" entityId={meta.id} className="ml-auto" />
          </div>
          {copy.copyError ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {copy.copyError}
            </p>
          ) : null}
        </header>
        <div className="flex flex-col gap-5 rounded-3xl border border-border bg-surface px-5 py-7 text-[1.0625rem] leading-relaxed shadow-sm sm:px-10">
          {cards.map((c) => (
            <CardView key={c.id} id={c.id} type={c.type} content={c.content} highlighted={reader.current === c.id} onAnchor={(anchor, cardId) => router.push(`/notes/${meta.id}/read/${anchor.fileId}?page=${anchor.page}&card=${cardId}`)} />
          ))}
        </div>
      </article>
    </div>
  )
}
