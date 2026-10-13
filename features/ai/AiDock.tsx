'use client'

import { Sparkles } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import type { AiTask } from '@/graphql/generated/graphql'
import type { NoteStudy } from '@/features/notes/view/StudyTabs'
import { AiResult } from './AiPanel'
import { AnswerList, AskForm } from './AskAi'

/** From 1280 px the note view docks Ask AI on its right (lvn-backend ADR-0076); below, the AI tasks sheet is the way. */
export function useWide(query = '(min-width: 1280px)') {
  const [wide, setWide] = useState(false)
  useEffect(() => {
    const list = window.matchMedia(query)
    const update = () => setWide(list.matches)
    update()
    list.addEventListener('change', update)
    return () => list.removeEventListener('change', update)
  }, [query])
  return wide
}

/**
 * Board A's Ask-AI panel beside a note: its suggestions are one tap each, every one an existing AI task (ADR-0059–0063);
 * a question about the note; and the viewer's results. Only what AI can do now is offered: with AI off, the reason.
 */
export function AiDock({ noteId, study, canEdit, canFork, hasCode, onAddedToNote }: { noteId: string; study: NoteStudy; canEdit: boolean; canFork: boolean; hasCode: boolean; onAddedToNote?: () => void }) {
  const t = useTranslations('notes.view.dock')
  const tAi = useTranslations('ai')
  const { ai } = study
  // Tidy into notes works on the person's own words; someone who may only copy the note makes notes from it instead.
  const quick: AiTask | null = canEdit ? 'QUICK_NOTE' : canFork ? 'CREATE_NOTES' : null
  const chips: AiTask[] = ['EXPLAIN_SIMPLY', 'PRACTICE_QUESTIONS', 'FLASHCARDS', 'FIND_MISTAKES', 'SUMMARIZE', 'QUIZ', ...(quick ? [quick] : []), ...(hasCode ? (['EXPLAIN_CODE'] as AiTask[]) : [])]
  const results = study.artifacts.slice(0, 6)
  return (
    <aside aria-labelledby={`dock-${noteId}`} className="sticky top-20 flex max-h-[calc(100dvh-6rem)] flex-col gap-4 overflow-y-auto rounded-3xl border border-border bg-surface p-4">
      <header className="flex flex-col gap-1">
        <h2 id={`dock-${noteId}`} className="flex items-center gap-2 text-base font-bold">
          <Sparkles className="size-4 text-accent" aria-hidden />
          {t('title')}
        </h2>
        <p className="text-xs text-muted">{t('lead')}</p>
      </header>
      {ai.status && !ai.status.available ? (
        <p role="note" className="rounded-xl border border-amber-500/40 bg-amber-50 px-3 py-2 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">
          {tAi(`unavailable.${ai.status.reason ?? 'NOT_CONFIGURED'}`)}
        </p>
      ) : null}
      {ai.available ? (
        <>
          <ul className="flex flex-col gap-1.5">
            {chips.map((task) => (
              <li key={task}>
                <button
                  type="button"
                  disabled={ai.spent || ai.running}
                  onClick={() => void ai.run(task)}
                  className="w-full rounded-xl border border-border bg-bg px-3 py-2 text-left text-sm font-medium transition hover:border-accent hover:bg-accent-soft disabled:pointer-events-none disabled:opacity-50"
                >
                  {t(`chips.${task}`)}
                </button>
              </li>
            ))}
          </ul>
          {ai.error ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {ai.error}
            </p>
          ) : null}
          <AskForm scope="THIS_NOTE" noteId={noteId} compact offNotice={false} />
          <AnswerList noteId={noteId} compact />
        </>
      ) : null}
      {results.length ? (
        <section aria-label={t('results')} className="flex flex-col gap-3">
          <h3 className="text-xs font-bold uppercase tracking-wide text-muted">{t('results')}</h3>
          {results.map((a) => (
            <AiResult key={a.id} noteId={noteId} artifact={a} canEdit={canEdit} onRetry={() => void ai.run(a.task, a.language)} onAddedToNote={onAddedToNote} />
          ))}
        </section>
      ) : null}
    </aside>
  )
}
