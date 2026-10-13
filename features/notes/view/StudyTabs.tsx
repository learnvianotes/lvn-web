'use client'

import { useQuery } from '@apollo/client/react'
import { GraduationCap, Layers, ListChecks, Plus, ScrollText, Sparkles } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { AiResult, useRunAiTask } from '@/features/ai/AiPanel'
import { StudyAids } from '@/features/ai/StudyAids'
import { StudyCardsButton } from '@/features/learning/StudyCardsButton'
import { useLive } from '@/features/notifications/live'
import { NoteAiArtifactsDocument, NoteInsightsDocument, type AiTask } from '@/graphql/generated/graphql'
import type { CardType } from '@/lib/contracts/domain/enums'
import { CardView } from '../render/CardView'
import { TAB_CARDS, TAB_TASKS } from './offered'

type Ai = ReturnType<typeof useRunAiTask>

/** What the study tabs read: the note's public aids, the viewer's AI results, and AI to make more (ADR-0059, ADR-0061). */
export function useNoteStudy(noteId: string) {
  const insights = useQuery(NoteInsightsDocument, { variables: { id: noteId }, fetchPolicy: 'cache-and-network' })
  // Aids being made arrive live (ADR-0061), whichever tab is open: the tabs read the same cache.
  useLive((signal) => {
    if ((signal.kind === 'NOTE_PROCESSING' && signal.id === noteId) || signal.kind === 'RECONNECTED') void insights.refetch().catch(() => undefined)
  })
  const results = useQuery(NoteAiArtifactsDocument, { variables: { noteId }, fetchPolicy: 'cache-and-network' })
  const ai = useRunAiTask(noteId)
  const aids = insights.data?.note?.aiInsights ?? []
  const artifacts = results.data?.note?.aiArtifacts ?? []
  return { ai, aids, artifacts, tasks: [...aids.map((a) => a.task as string), ...artifacts.map((a) => a.task as string)] }
}
export type NoteStudy = ReturnType<typeof useNoteStudy>

/** The viewer's own results for a tab, each with its keep or apply actions (ADR-0059). */
function Results({ noteId, study, tab, canEdit, onAddedToNote }: { noteId: string; study: NoteStudy; tab: keyof typeof TAB_TASKS; canEdit: boolean; onAddedToNote?: () => void }) {
  const t = useTranslations('notes.view')
  const mine = study.artifacts.filter((a) => TAB_TASKS[tab].includes(a.task))
  if (!mine.length) return null
  return (
    <section aria-label={t('yourResults')} className="flex flex-col gap-3">
      <h3 className="text-sm font-bold uppercase tracking-wide text-muted">{t('yourResults')}</h3>
      {mine.map((a) => (
        <AiResult key={a.id} noteId={noteId} artifact={a} canEdit={canEdit} onRetry={() => void study.ai.run(a.task, a.language)} onAddedToNote={onAddedToNote} />
      ))}
    </section>
  )
}

function Make({ ai, task, label, icon: Icon }: { ai: Ai; task: AiTask; label: string; icon: typeof Sparkles }) {
  if (!ai.available) return null
  return (
    <Button size="sm" className="gap-1.5" disabled={ai.spent || ai.running} onClick={() => void ai.run(task)}>
      <Icon className="size-4" aria-hidden />
      {label}
    </Button>
  )
}

function Problem({ ai }: { ai: Ai }) {
  return ai.error ? (
    <p role="alert" className="text-sm text-red-600 dark:text-red-400">
      {ai.error}
    </p>
  ) : null
}

/** AI Summary: the note's public summary, key concepts and practice questions, the viewer's own, and Summarise. */
export function SummaryTab({ noteId, study, canEdit, onAddedToNote }: { noteId: string; study: NoteStudy; canEdit: boolean; onAddedToNote?: () => void }) {
  const t = useTranslations('notes.view')
  const any = study.tasks.some((task) => TAB_TASKS.summary.includes(task))
  return (
    <>
      <StudyAids noteId={noteId} tasks={['SUMMARIZE', 'KEY_CONCEPTS', 'PRACTICE_QUESTIONS']} />
      <Results noteId={noteId} study={study} tab="summary" canEdit={canEdit} onAddedToNote={onAddedToNote} />
      {!any ? <p className="text-sm text-muted">{t('summary.none')}</p> : null}
      <div className="flex flex-wrap gap-2">
        <Make ai={study.ai} task="SUMMARIZE" label={t('summary.make')} icon={ScrollText} />
      </div>
      <Problem ai={study.ai} />
    </>
  )
}

/**
 * Flashcards or Quiz: the note's own cards of that kind, its public aid, the viewer's AI results, and the ways to get
 * more — AI, or a card added to the note for its editors; flashcards are studied from here too (ADR-0068).
 */
export function CardsTab({ kind, noteId, cards, study, canEdit, reader, onAdd, onAddedToNote }: { kind: 'flashcards' | 'quiz'; noteId: string; cards: { id: string; type: string; content: unknown }[]; study: NoteStudy; canEdit: boolean; reader: boolean; onAdd?: (type: CardType) => void; onAddedToNote?: () => void }) {
  const t = useTranslations(`notes.view.${kind}`)
  const own = cards.filter((c) => TAB_CARDS[kind].includes(c.type))
  const any = own.length > 0 || study.tasks.some((task) => TAB_TASKS[kind].includes(task))
  const task: AiTask = kind === 'flashcards' ? 'FLASHCARDS' : 'QUIZ'
  return (
    <>
      {own.length ? (
        <section aria-label={t('inNote')} className="flex flex-col gap-3">
          <h3 className="text-sm font-bold uppercase tracking-wide text-muted">{t('inNote')}</h3>
          {own.map((c) => (
            <div key={c.id} className="rounded-2xl border border-border bg-surface p-4">
              <CardView id={`tab-${c.id}`} type={c.type as CardType} content={c.content} />
            </div>
          ))}
        </section>
      ) : null}
      <StudyAids noteId={noteId} tasks={[task]} />
      <Results noteId={noteId} study={study} tab={kind} canEdit={canEdit} onAddedToNote={onAddedToNote} />
      {!any ? <p className="text-sm text-muted">{t('none')}</p> : null}
      <div className="flex flex-wrap items-center gap-2">
        <Make ai={study.ai} task={task} label={t('make')} icon={kind === 'flashcards' ? Layers : ListChecks} />
        {canEdit && onAdd ? (
          <Button size="sm" variant="secondary" className="gap-1.5" onClick={() => onAdd(kind === 'flashcards' ? 'flashcard' : 'quiz')}>
            <Plus className="size-4" aria-hidden />
            {t('add')}
          </Button>
        ) : null}
        {kind === 'flashcards' && own.length ? (
          reader ? (
            <StudyCardsButton noteId={noteId} />
          ) : (
            <Link href="/review" className="inline-flex items-center gap-1.5 text-sm font-semibold text-accent hover:underline">
              <GraduationCap className="size-4" aria-hidden />
              {t('review')}
            </Link>
          )
        ) : null}
      </div>
      <Problem ai={study.ai} />
    </>
  )
}
