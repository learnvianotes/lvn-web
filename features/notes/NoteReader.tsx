'use client'

import { Clock } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useState } from 'react'
import { cardPlainText } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import type { NoteMeta } from './api'
import { accentOf, readingMinutes } from './look'
import { ReadAloudControls } from './ReadAloudControls'
import { ReportButton } from '@/features/moderation/ReportDialog'
import { CopyLinkButton, ForkCredit, MakeCopyButton, useMakeCopy } from './ShareDialog'
import type { StoredCard } from './model/doc'
import { useReadAloud } from './readAloud'
import { CardView } from './render/CardView'
import { QuizTopicsProvider } from './render/interactive'
import { Discussion } from '@/features/discussion/Discussion'
import { NoteCredits } from '@/features/workspaces/Credits'
import { AiDock } from '@/features/ai/AiDock'
import { AiButton, AiPanel } from '@/features/ai/AiPanel'
import { Breadcrumb } from './view/Breadcrumb'
import { CardRail } from './view/CardRail'
import { NoteTabPanel, NoteTabs, type NoteTab } from './view/NoteTabs'
import { CardsTab, SummaryTab, type NoteStudy } from './view/StudyTabs'

/**
 * A note the viewer can read but not edit, as board A draws it (lvn-backend ADR-0076): the breadcrumb, Fork and Share,
 * read aloud, and tabs — its cards with their rail, its AI summary, flashcards and quiz, and its discussion — with Ask
 * AI docked beside it on wide screens.
 */
export function NoteReader({ meta, cards, study, offered, tab, onTab, wide }: { meta: NoteMeta; cards: StoredCard[]; study: NoteStudy; offered: readonly NoteTab[]; tab: NoteTab; onTab: (tab: NoteTab) => void; wide: boolean }) {
  const t = useTranslations('notes')
  const router = useRouter()
  const spoken = useCallback(() => cards.map((c) => ({ id: c.id, text: cardPlainText(c.type, c.content) })), [cards])
  const reader = useReadAloud(spoken)
  const copy = useMakeCopy(meta.id)
  const headings = cards.filter((c) => c.type === 'heading')
  const minutes = readingMinutes(cards.map((c) => cardPlainText(c.type, c.content)).join(' '))
  const accent = accentOf(meta.id)
  const [progress, setProgress] = useState(0)
  const [aiOpen, setAiOpen] = useState(false)
  const idBase = `note-${meta.id}`
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
    <div className={cn('grid gap-6', wide && 'xl:grid-cols-[minmax(0,1fr)_19rem]')}>
      <div aria-hidden className="fixed inset-x-0 top-0 z-50 h-1 origin-left bg-accent transition-transform duration-150" style={{ transform: `scaleX(${progress})` }} />
      <article className="flex min-w-0 flex-col gap-4">
        <Breadcrumb meta={meta} own={false} />
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
          {meta.kind === 'PROJECT' ? <NoteCredits noteId={meta.id} /> : null}
          <div className="flex flex-wrap items-center gap-2">
            <ReadAloudControls reader={reader} />
            {meta.viewerCan.fork ? <MakeCopyButton copy={copy} /> : null}
            <CopyLinkButton note={meta} />
            <AiButton onClick={() => setAiOpen(true)} />
            <ReportButton entityType="NOTE" entityId={meta.id} className="ml-auto" />
          </div>
          {copy.copyError ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {copy.copyError}
            </p>
          ) : null}
        </header>
        <NoteTabs tabs={offered} current={tab} onChange={onTab} idBase={idBase} />
        <NoteTabPanel idBase={idBase} tab="content" current={tab} keepMounted>
          <CardRail sections={headings.map((h) => ({ key: h.id, text: cardPlainText('heading', h.content) }))} onGo={(i) => document.getElementById(`card-${headings[i]?.id}`)?.scrollIntoView({ block: 'center', behavior: 'smooth' })} />
          <QuizTopicsProvider topicKeys={(meta.topics ?? []).map((x) => `topic:${x.id}`)}>
            <div className="flex flex-col gap-5 rounded-3xl border border-border bg-surface px-5 py-7 text-[1.0625rem] leading-relaxed shadow-sm sm:px-10">
              {cards.map((c) => (
                <CardView key={c.id} id={c.id} type={c.type} content={c.content} highlighted={reader.current === c.id} onAnchor={(anchor, cardId) => router.push(`/notes/${meta.id}/read/${anchor.fileId}?page=${anchor.page}&card=${cardId}`)} />
              ))}
            </div>
          </QuizTopicsProvider>
        </NoteTabPanel>
        {tab === 'summary' ? (
          <NoteTabPanel idBase={idBase} tab="summary" current={tab}>
            <SummaryTab noteId={meta.id} study={study} canEdit={false} />
          </NoteTabPanel>
        ) : null}
        {tab === 'flashcards' || tab === 'quiz' ? (
          <NoteTabPanel idBase={idBase} tab={tab} current={tab}>
            <QuizTopicsProvider topicKeys={(meta.topics ?? []).map((x) => `topic:${x.id}`)}>
              <CardsTab kind={tab} noteId={meta.id} cards={cards} study={study} canEdit={false} reader />
            </QuizTopicsProvider>
          </NoteTabPanel>
        ) : null}
        {tab === 'discussions' ? (
          <NoteTabPanel idBase={idBase} tab="discussions" current={tab}>
            <Discussion target={{ type: 'NOTE', id: meta.id }} />
          </NoteTabPanel>
        ) : null}
      </article>
      {wide && !aiOpen ? <AiDock noteId={meta.id} study={study} canEdit={false} canFork={meta.viewerCan.fork} hasCode={cards.some((c) => c.type === 'code')} /> : null}
      <AiPanel noteId={meta.id} open={aiOpen} onClose={() => setAiOpen(false)} canEdit={false} canFork={meta.viewerCan.fork} hasCode={cards.some((c) => c.type === 'code')} />
    </div>
  )
}
