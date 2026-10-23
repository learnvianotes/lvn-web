'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { BookOpen, Globe, LoaderCircle, MessageCircleQuestion, NotebookPen, Sparkles, Trash2, Users, type LucideIcon } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useId, useState } from 'react'
import { Button } from '@/components/ui/button'
import { LimitNotice } from '@/components/ui/limit-notice'
import { limitMessageFromUserErrors, refusalMessage } from '@/lib/limit-error'
import { AiAnswerDocument, AiStateDocument, AskAiAboutDoubtDocument, AskAiDocument, DeleteAiAnswerDocument, MyAiAnswersDocument, type AiAnswerFieldsFragment, type AskAiScope } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { useLive } from '@/features/notifications/live'
import { Markdown } from '@/features/notes/render/Markdown'

/**
 * Ask AI (lvn-backend ADR-0060): a question over the notes the asker may read — one note, their notes, their groups'
 * and classes', public notes, or a workspace's from one of its doubts — answered with the sources it cites. Answers
 * grow while the model writes: the live channel says when (AI_ANSWER), and polling covers a closed socket.
 */

type Answer = AiAnswerFieldsFragment
const POLL_MS = 2000

/** What went wrong, in the server's words: refusals arrive as errors, invalid input and AI being off as userErrors. */
function problemOf(error: unknown, payload: { userErrors: { message: string }[] } | null | undefined, fallback: string) {
  if (CombinedGraphQLErrors.is(error)) return error.errors[0]?.message ?? fallback
  return error ? fallback : (payload?.userErrors[0]?.message ?? null)
}

/** Keeps a running answer fresh until it is READY or FAILED; updates reach every list through the cache. */
function Follow({ id }: { id: string }) {
  const { refetch } = useQuery(AiAnswerDocument, { variables: { id }, pollInterval: POLL_MS, fetchPolicy: 'network-only' })
  useLive((signal) => {
    if ((signal.kind === 'AI_ANSWER' && signal.id === id) || signal.kind === 'RECONNECTED') void refetch().catch(() => undefined)
  })
  return null
}

/** A question box; `onAsked` gets the queued answer. */
/** `offNotice` false: the surrounding panel already says AI is off. */
export function AskForm({ scope, noteId, doubtId, onAsked, compact, offNotice = true, initialQuestion = '' }: { scope: AskAiScope; noteId?: string; doubtId?: string; onAsked?: (answer: Answer) => void; compact?: boolean; offNotice?: boolean; initialQuestion?: string }) {
  const t = useTranslations('ai.ask')
  const inputId = useId()
  const state = useQuery(AiStateDocument, { fetchPolicy: 'cache-and-network' })
  const [askAi, asking] = useMutation(AskAiDocument, { refetchQueries: ['MyAiAnswers'] })
  const [askDoubt, askingDoubt] = useMutation(AskAiAboutDoubtDocument, { refetchQueries: ['MyAiAnswers'] })
  const [question, setQuestion] = useState(initialQuestion)
  const [error, setError] = useState<string | null>(null)
  const [limit, setLimit] = useState(false)
  const status = state.data?.aiStatus
  const off = status ? !status.available : false
  const busy = asking.loading || askingDoubt.loading

  const submit = async (event?: React.FormEvent) => {
    event?.preventDefault()
    setError(null)
    setLimit(false)
    try {
      const res = doubtId ? (await askDoubt({ variables: { doubtId } })).data?.askAiAboutDoubt : (await askAi({ variables: { input: { question: question.trim(), scope, noteId } } })).data?.askAi
      const hit = limitMessageFromUserErrors(res?.userErrors)
      setLimit(!!hit)
      setError(hit ?? problemOf(null, res, t('failed')))
      if (res?.answer) {
        setQuestion('')
        onAsked?.(res.answer)
      }
    } catch (e) {
      const hit = refusalMessage(e)
      setLimit(!!hit)
      setError(hit ?? problemOf(e, null, t('failed')))
    }
  }

  if (doubtId) {
    return (
      <div className="flex flex-col gap-2">
        <Button variant="secondary" size="sm" className="w-fit gap-1.5" disabled={off || busy} onClick={() => void submit()}>
          <Sparkles className="size-4 text-accent" aria-hidden />
          {t('aboutDoubt')}
        </Button>
        {off ? <p className="text-xs text-muted">{t(`off.${status?.reason ?? 'NOT_CONFIGURED'}`)}</p> : null}
        {error ? (
          limit ? <LimitNotice>{error}</LimitNotice> : (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          )
        ) : null}
      </div>
    )
  }
  return (
    <form onSubmit={(e) => void submit(e)} className="flex flex-col gap-2">
      <label htmlFor={inputId} className={cn('font-semibold', compact ? 'text-sm' : 'text-base')}>
        {t(scope === 'THIS_NOTE' ? 'aboutNote' : 'label')}
      </label>
      <div className="flex gap-2">
        <textarea
          id={inputId}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              if (question.trim().length >= 3) void submit()
            }
          }}
          rows={compact ? 2 : 3}
          maxLength={1000}
          placeholder={t(scope === 'THIS_NOTE' ? 'placeholderNote' : 'placeholder')}
          disabled={off}
          className="min-h-11 w-full resize-y rounded-xl border border-border bg-bg px-3 py-2 text-sm outline-none focus:border-accent"
        />
        <Button type="submit" size="sm" className="h-auto self-stretch" disabled={off || busy || question.trim().length < 3}>
          {busy ? <LoaderCircle className="size-4 animate-spin" aria-hidden /> : t('ask')}
        </Button>
      </div>
      {off && offNotice ? <p className="text-xs text-muted">{t(`off.${status?.reason ?? 'NOT_CONFIGURED'}`)}</p> : null}
      {error ? (
        limit ? <LimitNotice>{error}</LimitNotice> : (
          <p role="alert" className="text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        )
      ) : null}
    </form>
  )
}

/** One answer: the question, the text with its citations, and the sources they point to. */
export function AnswerCard({ answer: a, compact }: { answer: Answer; compact?: boolean }) {
  const t = useTranslations('ai.ask')
  const [remove, removing] = useMutation(DeleteAiAnswerDocument, { refetchQueries: ['MyAiAnswers'] })
  const pending = a.status === 'QUEUED' || a.status === 'RUNNING'
  const anchor = (n: number) => `source-${a.id}-${n}`
  const cited = new Set(a.sources.map((s) => s.n))
  return (
    <article aria-label={a.question} data-answer-status={a.status} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <header className="flex items-start gap-2">
        <MessageCircleQuestion className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden />
        <h3 className={cn('min-w-0 flex-1 font-semibold', compact ? 'text-sm' : 'text-base')}>{a.question}</h3>
        {pending ? null : (
          <Button variant="ghost" size="icon" aria-label={t('delete')} title={t('delete')} disabled={removing.loading} onClick={() => void remove({ variables: { id: a.id } }).catch(() => undefined)}>
            <Trash2 className="size-4" aria-hidden />
          </Button>
        )}
      </header>
      {pending ? (
        <>
          <Follow id={a.id} />
          <p role="status" className="flex items-center gap-2 text-sm text-muted">
            <LoaderCircle className="size-4 animate-spin" aria-hidden />
            {t(a.status === 'QUEUED' ? 'queued' : 'writing')}
          </p>
        </>
      ) : null}
      {a.text ? (
        <Markdown
          source={a.text}
          className="flex flex-col gap-2.5 text-sm leading-relaxed"
          cite={(n) =>
            cited.has(n) ? (
              <a href={`#${anchor(n)}`} className="mx-0.5 inline-flex min-w-5 items-center justify-center rounded-md bg-accent-soft px-1 align-super text-[0.7em] font-bold text-accent no-underline hover:bg-accent hover:text-accent-fg" aria-label={t('source', { n })}>
                {n}
              </a>
            ) : (
              <sup className="text-muted">[{n}]</sup>
            )
          }
        />
      ) : null}
      {a.status === 'FAILED' ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {a.error ?? t('failed')}
        </p>
      ) : null}
      {a.status === 'READY' && a.sources.length ? (
        <section aria-label={t('sources')} className="flex flex-col gap-2">
          <h4 className="text-xs font-bold uppercase tracking-wide text-muted">{t('sources')}</h4>
          <ol className="flex flex-col gap-2">
            {a.sources.map((s) => (
              <li key={s.n} id={anchor(s.n)} className="scroll-mt-24">
                <Link href={`/notes/${s.noteId}`} className="flex gap-3 rounded-xl border border-border bg-bg p-3 text-sm transition hover:border-accent">
                  <span className="grid size-6 shrink-0 place-items-center rounded-md bg-accent-soft text-xs font-bold text-accent">{s.n}</span>
                  <span className="min-w-0 flex-1">
                    <span className="flex items-center gap-1.5 font-semibold">
                      <BookOpen className="size-3.5 text-muted" aria-hidden />
                      <span className="truncate">{s.title || t('untitled')}</span>
                      {s.versionId ? null : <span className="rounded-full bg-surface-2 px-1.5 text-[0.65rem] font-medium text-muted">{t('draft')}</span>}
                    </span>
                    <span className="mt-0.5 line-clamp-2 text-muted">{s.snippet}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ol>
        </section>
      ) : null}
    </article>
  )
}

/** The asker's answers, newest first: about one note, one doubt, or everything. */
export function AnswerList({ noteId, doubtId, compact, emptyText }: { noteId?: string; doubtId?: string; compact?: boolean; emptyText?: string }) {
  const { data, loading } = useQuery(MyAiAnswersDocument, { variables: { first: 20, noteId: noteId ?? null, doubtId: doubtId ?? null }, fetchPolicy: 'cache-and-network' })
  const answers = data?.myAiAnswers ?? []
  if (loading && !data) return null
  if (!answers.length) return emptyText ? <p className="text-sm text-muted">{emptyText}</p> : null
  return (
    <div className="flex flex-col gap-3">
      {answers.map((a) => (
        <AnswerCard key={a.id} answer={a} compact={compact} />
      ))}
    </div>
  )
}

const SCOPES: { scope: AskAiScope; icon: LucideIcon }[] = [
  { scope: 'MY_NOTES', icon: NotebookPen },
  { scope: 'MY_PLACES', icon: Users },
  { scope: 'PUBLIC', icon: Globe },
]

/** /ask: questions over the asker's notes, their groups' and classes', or public notes. */
/** `question`: one brought from the search field ("…or ask AI"), filled in for the person to send. */
export function AskPage({ question }: { question?: string } = {}) {
  const t = useTranslations('ai.ask')
  const [scope, setScope] = useState<AskAiScope>('MY_NOTES')
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="flex items-center gap-2 text-2xl font-bold tracking-tight">
          <Sparkles className="size-6 text-accent" aria-hidden />
          {t('title')}
        </h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      <div role="radiogroup" aria-label={t('where')} className="flex flex-wrap gap-2">
        {SCOPES.map(({ scope: s, icon: Icon }) => (
          <button
            key={s}
            type="button"
            role="radio"
            aria-checked={scope === s}
            onClick={() => setScope(s)}
            className={cn('inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium transition', scope === s ? 'border-accent bg-accent-soft text-accent' : 'border-border text-muted hover:text-fg')}
          >
            <Icon className="size-4" aria-hidden />
            {t(`scope.${s}`)}
          </button>
        ))}
      </div>
      <p className="-mt-3 text-xs text-muted">{t(`scopeHint.${scope}`)}</p>
      <AskForm scope={scope} initialQuestion={question} />
      <section aria-label={t('history')} className="flex flex-col gap-3">
        <h2 className="text-sm font-bold uppercase tracking-wide text-muted">{t('history')}</h2>
        <AnswerList emptyText={t('none')} />
      </section>
    </div>
  )
}
