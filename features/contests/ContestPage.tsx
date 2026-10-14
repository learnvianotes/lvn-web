'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Check, X } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { AnswerContestQuestionDocument, ContestDocument, SetContestBandsDocument, StartContestDocument, SubmitContestDocument, type ContestAttemptFieldsFragment } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { isNotThere } from '@/lib/query'

/**
 * A weekly contest (lvn-backend ADR-0082): its details and Start while it is open; then the attempt, timed by the
 * server (the time left shows here, and answers can change until it ends or is submitted); then the score, the
 * person's best, every question with the right answer and why, and, for an adult who asked, their band among adults.
 */
export function ContestPage({ id }: { id: string }) {
  const t = useTranslations('contests')
  const format = useFormatter()
  const { data, loading, error, refetch } = useQuery(ContestDocument, { variables: { id }, fetchPolicy: 'cache-and-network' })
  const [start, starting] = useMutation(StartContestDocument)
  const [problem, setProblem] = useState<string | null>(null)
  const c = data?.contest
  if (!c) {
    if (loading) return <Loading label={t('loading')} />
    // Not there only when the API said so; a contest that could not be asked for is offered again.
    return error && !isNotThere(error) ? <LoadFailed onRetry={refetch} /> : <p className="text-muted">{t('notFound')}</p>
  }
  const a = c.viewerAttempt
  return (
    <div className="flex flex-col gap-6">
      <nav>
        <Link href="/contests" className="text-sm text-accent hover:underline">
          ← {t('title')}
        </Link>
      </nav>
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-extrabold tracking-tight">{c.title}</h1>
        <p className="text-sm text-muted">
          {[c.subjectTitle, t('questions', { count: c.questionCount }), t('minutes', { count: c.minutes }), c.participantsMilestone ? t('participants', { count: c.participantsMilestone }) : null].filter(Boolean).join(' · ')}
        </p>
      </header>
      {!a ? (
        <section className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-5">
          {c.state === 'OPEN' ? (
            <>
              <p className="text-sm">{t('rules', { minutes: c.minutes, closes: format.dateTime(new Date(c.closesAt), { weekday: 'long', hour: 'numeric', minute: '2-digit' }) })}</p>
              <Button
                type="button"
                className="self-start"
                disabled={starting.loading}
                onClick={async () => {
                  const res = await start({ variables: { contestId: c.id } }).catch(() => null)
                  setProblem(res?.data?.startContest.userErrors[0]?.message ?? (res ? null : t('failed')))
                  await refetch()
                }}
              >
                {t('start')}
              </Button>
            </>
          ) : (
            <p className="text-sm text-muted">{c.state === 'UPCOMING' ? t('opens', { at: format.dateTime(new Date(c.opensAt), { weekday: 'long', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }) }) : t('missed')}</p>
          )}
          {problem ? <Alert tone="error">{problem}</Alert> : null}
        </section>
      ) : a.finished ? (
        <Results attempt={a} subject={c.subjectTitle ?? null} settings={data.contestSettings} />
      ) : (
        <Attempt attempt={a} onOver={() => void refetch()} />
      )}
    </div>
  )
}

function Attempt({ attempt: a, onOver }: { attempt: ContestAttemptFieldsFragment; onOver: () => void }) {
  const t = useTranslations('contests')
  const [now, setNow] = useState(() => Date.now())
  const [chosen, setChosen] = useState<Record<string, string>>(() => Object.fromEntries(a.questions.flatMap((q) => (q.myChoiceId ? [[q.id, q.myChoiceId]] : []))))
  const [problem, setProblem] = useState<string | null>(null)
  const [answer] = useMutation(AnswerContestQuestionDocument)
  const [submit, submitting] = useMutation(SubmitContestDocument, { refetchQueries: [ContestDocument] })
  const left = Math.max(0, Math.ceil((new Date(a.deadline).getTime() - now) / 1000))
  useEffect(() => {
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [])
  // The server marks the attempt at its deadline; reading it again (once) shows the results.
  const over = useRef(false)
  useEffect(() => {
    if (left === 0 && !over.current) {
      over.current = true
      onOver()
    }
  }, [left, onOver])
  const answered = Object.keys(chosen).length
  return (
    <section aria-label={t('attempt')} className="flex flex-col gap-4">
      <div className="sticky top-16 z-10 flex items-center justify-between rounded-2xl border border-border bg-surface px-4 py-3 shadow-sm">
        <span className="text-sm text-muted">{t('answered', { answered, total: a.questions.length })}</span>
        <span role="timer" aria-live="off" aria-label={t('timeLeft')} className={cn('font-mono text-lg font-bold tabular-nums', left < 60 && 'text-red-600 dark:text-red-400')}>
          {Math.floor(left / 60)}:{String(left % 60).padStart(2, '0')}
        </span>
      </div>
      <ol className="flex flex-col gap-4">
        {a.questions.map((q, i) => (
          <li key={q.id} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
            <p className="font-semibold">
              {i + 1}. {q.prompt}
            </p>
            <div role="radiogroup" aria-label={q.prompt} className="flex flex-col gap-2">
              {q.choices.map((choice) => (
                <button
                  key={choice.id}
                  type="button"
                  role="radio"
                  aria-checked={chosen[q.id] === choice.id}
                  onClick={async () => {
                    setChosen((x) => ({ ...x, [q.id]: choice.id }))
                    const res = await answer({ variables: { input: { attemptId: a.id, questionId: q.id, choiceId: choice.id } } }).catch(() => null)
                    setProblem(res?.data?.answerContestQuestion.userErrors[0]?.message ?? (res ? null : t('failed')))
                  }}
                  className={cn('rounded-xl border px-4 py-2.5 text-left text-sm', chosen[q.id] === choice.id ? 'border-accent bg-accent-soft font-semibold text-accent' : 'border-border hover:border-accent')}
                >
                  {choice.text}
                </button>
              ))}
            </div>
          </li>
        ))}
      </ol>
      {problem ? <Alert tone="error">{problem}</Alert> : null}
      <Button type="button" className="self-start" disabled={submitting.loading} onClick={() => void submit({ variables: { attemptId: a.id } })}>
        {t('submit')}
      </Button>
    </section>
  )
}

function Results({ attempt: a, subject, settings }: { attempt: ContestAttemptFieldsFragment; subject: string | null; settings: { showBands: boolean; canShowBands: boolean } }) {
  const t = useTranslations('contests')
  const [setBands, bands] = useMutation(SetContestBandsDocument, { refetchQueries: [ContestDocument] })
  const [compare, setCompare] = useState(settings.showBands)
  return (
    <div className="flex flex-col gap-6">
      <section aria-label={t('results')} className="flex flex-col gap-2 rounded-3xl border border-border bg-surface p-5">
        <p className="text-3xl font-extrabold">{t('score', { score: a.score ?? 0, total: a.total })}</p>
        {a.personalBest !== null && a.personalBest !== undefined ? <p className="text-sm text-muted">{subject ? t('bestOn', { best: a.personalBest, subject }) : t('best', { best: a.personalBest })}</p> : null}
        {a.band ? <p className="text-sm font-semibold text-accent">{t(`band.${a.band}`)}</p> : null}
        {settings.canShowBands ? (
          <label className="mt-2 flex items-start gap-3 text-sm">
            <input
              type="checkbox"
              className="mt-1 size-4"
              checked={compare}
              disabled={bands.loading}
              onChange={async (e) => {
                const next = e.target.checked
                setCompare(next)
                const res = await setBands({ variables: { show: next } }).catch(() => null)
                if (!res?.data?.setContestBands.settings) setCompare(!next)
              }}
            />
            <span className="flex flex-col">
              <span className="font-medium">{t('compare')}</span>
              <span className="text-muted">{t('compareHelp')}</span>
            </span>
          </label>
        ) : null}
      </section>
      <ol className="flex flex-col gap-4">
        {a.questions.map((q, i) => (
          <li key={q.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
            <p className="font-semibold">
              {i + 1}. {q.prompt}
            </p>
            <ul className="flex flex-col gap-1.5">
              {q.choices.map((choice) => {
                const right = choice.id === q.correctChoiceId
                const mine = choice.id === q.myChoiceId
                return (
                  <li key={choice.id} className={cn('flex items-center gap-2 rounded-xl px-3 py-2 text-sm', right ? 'bg-emerald-50 text-emerald-800 dark:bg-emerald-500/10 dark:text-emerald-300' : mine ? 'bg-surface-2' : '')}>
                    {right ? <Check aria-hidden className="size-4" /> : mine ? <X aria-hidden className="size-4" /> : <span aria-hidden className="size-4" />}
                    <span className="flex-1">{choice.text}</span>
                    {mine ? <span className="text-xs font-semibold">{t('yours')}</span> : null}
                    {right ? <span className="sr-only">{t('right')}</span> : null}
                  </li>
                )
              })}
            </ul>
            {!q.myChoiceId ? <p className="text-xs text-muted">{t('unanswered')}</p> : null}
            {q.explanation ? <p className="text-sm text-muted">{q.explanation}</p> : null}
          </li>
        ))}
      </ol>
    </div>
  )
}
