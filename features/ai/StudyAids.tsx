'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { BookOpenCheck, CircleQuestionMark, Eye, EyeOff, Layers, Lightbulb, ListChecks, LoaderCircle, ScrollText, type LucideIcon } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { KeepAiCardsDocument, NoteInsightsDocument, SetAiInsightHiddenDocument, type AiTask } from '@/graphql/generated/graphql'
import type { CardType } from '@/lib/contracts/domain/enums'
import { cn } from '@/lib/cn'
import { useLive } from '@/features/notifications/live'
import { CardView } from '@/features/notes/render/CardView'
import { PracticeQuizProvider } from '@/features/notes/render/interactive'
import { Markdown } from '@/features/notes/render/Markdown'

/**
 * A public note's study aids (lvn-backend ADR-0061): a summary, key concepts, practice questions, a quiz and flashcards
 * made from its published version, the same for every reader. Readers try the quiz and flashcards and keep them; the
 * owner sees each aid being made and hides what they do not want.
 */

export interface Aid {
  id: string
  task: AiTask | string
  status: string
  markdown: string | null
  title: string | null
  cards: { type: string; content: unknown }[] | null
  hidden?: boolean
}

const ICON: Record<string, LucideIcon> = { SUMMARIZE: ScrollText, KEY_CONCEPTS: Lightbulb, PRACTICE_QUESTIONS: CircleQuestionMark, QUIZ: ListChecks, FLASHCARDS: Layers }
const POLL_MS = 3000

/** One aid's body: Markdown, or its cards to try. */
function AidBody({ aid }: { aid: Aid }) {
  if (aid.markdown != null) return <Markdown source={aid.markdown} className="flex flex-col gap-2.5 text-[0.95rem] leading-relaxed" />
  return (
    <PracticeQuizProvider>
      <div className="flex min-w-0 max-w-full flex-col gap-3">
        {(aid.cards ?? []).map((c, i) => (
          <div key={i} className="min-w-0 max-w-full rounded-2xl border border-border bg-bg p-4">
            <CardView id={`${aid.id}-${i}`} type={c.type as CardType} content={c.content} />
          </div>
        ))}
      </div>
    </PracticeQuizProvider>
  )
}

/**
 * The aids as tabs. `keep` saves an aid's cards as the viewer's own note (signed in); `keepHref` sends visitors of the
 * public page to the note in the app to do it. The owner's `onHidden` hides or shows an aid.
 */
export function StudyAidsView({ aids, keep, keepHref, owner, onHidden, busy }: { aids: Aid[]; keep?: (aid: Aid) => Promise<string | null>; keepHref?: string; owner?: boolean; onHidden?: (aid: Aid, hidden: boolean) => void; busy?: boolean }) {
  const t = useTranslations('ai.aids')
  const tTask = useTranslations('ai.task')
  const [current, setCurrent] = useState(0)
  const [saved, setSaved] = useState<{ aidId: string; noteId: string } | null>(null)
  const [error, setError] = useState<string | null>(null)
  if (!aids.length) return null
  const aid = aids[Math.min(current, aids.length - 1)]!
  const pending = aid.status === 'QUEUED' || aid.status === 'RUNNING'
  const save = async () => {
    setError(null)
    try {
      const noteId = await keep!(aid)
      if (noteId) setSaved({ aidId: aid.id, noteId })
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('keepFailed')) : (e as Error).message || t('keepFailed'))
    }
  }
  return (
    <section aria-labelledby="study-aids" className="flex min-w-0 max-w-full flex-col gap-4 rounded-3xl border border-accent/25 bg-surface p-5 sm:p-6">
      <header className="flex flex-col gap-1">
        <h2 id="study-aids" className="flex items-center gap-2 text-xl font-bold tracking-tight">
          <BookOpenCheck className="size-5 text-accent" aria-hidden />
          {t('title')}
        </h2>
        <p className="text-sm text-muted">{t(owner ? 'leadOwner' : 'lead')}</p>
      </header>
      {/* One aid needs no tabs of its own (a note's tab may hold just its quiz or flashcards, ADR-0076). */}
      {aids.length > 1 ? (
        <div role="tablist" aria-label={t('title')} className="-mx-1 flex gap-1.5 overflow-x-auto px-1 pb-1 [scrollbar-width:none]">
          {aids.map((a, i) => {
            const Icon = ICON[a.task] ?? ScrollText
            const selected = a.id === aid.id
            return (
              <button
                key={a.id}
                role="tab"
                type="button"
                aria-selected={selected}
                aria-controls={`aid-${a.id}`}
                onClick={() => setCurrent(i)}
                className={cn('inline-flex shrink-0 items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium transition', selected ? 'border-accent bg-accent text-accent-fg' : 'border-border text-muted hover:text-fg', a.hidden && 'opacity-60')}
              >
                {a.status === 'QUEUED' || a.status === 'RUNNING' ? <LoaderCircle className="size-4 animate-spin" aria-hidden /> : <Icon className="size-4" aria-hidden />}
                {tTask(a.task)}
              </button>
            )
          })}
        </div>
      ) : null}
      <div role={aids.length > 1 ? 'tabpanel' : 'group'} id={`aid-${aid.id}`} aria-label={tTask(aid.task)} className="flex flex-col gap-3">
        {owner ? (
          <div className="flex flex-wrap items-center gap-2 text-xs text-muted">
            <span>{t(`status.${aid.status}`)}</span>
            {aid.hidden ? <span className="rounded-full bg-surface-2 px-2 py-0.5 font-medium">{t('hiddenChip')}</span> : null}
            {onHidden && !pending ? (
              <Button variant="ghost" size="sm" className="ml-auto gap-1.5" disabled={busy} onClick={() => onHidden(aid, !aid.hidden)}>
                {aid.hidden ? <Eye className="size-4" aria-hidden /> : <EyeOff className="size-4" aria-hidden />}
                {t(aid.hidden ? 'show' : 'hide')}
              </Button>
            ) : null}
          </div>
        ) : null}
        {pending ? (
          <p role="status" className="flex items-center gap-2 text-sm text-muted">
            <LoaderCircle className="size-4 animate-spin" aria-hidden />
            {t('making')}
          </p>
        ) : aid.status === 'FAILED' ? (
          <p className="text-sm text-muted">{t('failed')}</p>
        ) : (
          <AidBody aid={aid} />
        )}
        {aid.status === 'READY' && aid.cards?.length ? (
          <div className="flex flex-wrap items-center gap-2">
            {keep ? (
              <Button size="sm" variant="secondary" onClick={() => void save()}>
                {t('keep')}
              </Button>
            ) : keepHref ? (
              <Link href={keepHref} className="text-sm font-medium text-accent hover:underline">
                {t('keepInApp')}
              </Link>
            ) : null}
            {saved?.aidId === aid.id ? (
              <p role="status" className="text-sm text-accent">
                {t('saved')}{' '}
                <Link href={`/notes/${saved.noteId}`} className="underline underline-offset-2">
                  {t('openNote')}
                </Link>
              </p>
            ) : null}
          </div>
        ) : null}
        {error ? (
          <p role="alert" className="text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        ) : null}
      </div>
    </section>
  )
}

/**
 * In the app: the aids of a note the viewer reads or owns, kept fresh while they are being made; `tasks` keeps only
 * those (the note view's AI Summary, Flashcards and Quiz tabs).
 */
export function StudyAids({ noteId, tasks }: { noteId: string; tasks?: readonly string[] }) {
  const { data, refetch } = useQuery(NoteInsightsDocument, { variables: { id: noteId }, fetchPolicy: 'cache-and-network' })
  const [keepCards] = useMutation(KeepAiCardsDocument)
  const [setHidden, hiding] = useMutation(SetAiInsightHiddenDocument)
  const note = data?.note
  const status = note?.noteProcessingStatus
  const making = !!status && !status.done
  useQuery(NoteInsightsDocument, { variables: { id: noteId }, pollInterval: POLL_MS, skip: !making, fetchPolicy: 'network-only' })
  useLive((signal) => {
    if ((signal.kind === 'NOTE_PROCESSING' && signal.id === noteId) || signal.kind === 'RECONNECTED') void refetch().catch(() => undefined)
  })
  const aids = (note?.aiInsights ?? []).filter((a) => !tasks || tasks.includes(a.task))
  if (!aids.length) return null
  const owner = !!status
  return (
    <StudyAidsView
      aids={aids}
      owner={owner}
      busy={hiding.loading}
      onHidden={owner ? (aid, hidden) => void setHidden({ variables: { id: aid.id, hidden } }).then(() => refetch()) : undefined}
      keep={async (aid) => {
        const res = await keepCards({ variables: { input: { artifactId: aid.id, cardIndexes: (aid.cards ?? []).map((_, i) => i), into: 'NEW_NOTE' } } })
        const payload = res.data?.keepAiCards
        if (payload?.userErrors.length) throw new Error(payload.userErrors[0]!.message)
        return payload?.noteId ?? null
      }}
    />
  )
}
