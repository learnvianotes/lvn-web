'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { ArrowLeft, Check, ChevronLeft, ChevronRight, RotateCcw, X } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { InlineText, RichDoc } from '@/features/notes/render/RichText'
import { ClassQuizDocument, SubmitQuizAttemptDocument, type ClassQuizFieldsFragment } from '@/graphql/generated/graphql'
import type { Doc, Inline } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { isNotThere } from '@/lib/query'
import { scoreOf } from './ClassQuizzes'

type Quiz = ClassQuizFieldsFragment
type Answers = Record<string, string[]>

/**
 * Taking a class quiz (lvn-backend ADR-0064): the questions without their answers, one at a time (lvn-backend ADR-0076),
 * submitted once for a score by the server, then each question's result, the correct choices and the explanation. Later
 * tries are practice.
 */
export function QuizPage({ classroomId, quizId }: { classroomId: string; quizId: string }) {
  const t = useTranslations('classes.quiz')
  const { data, loading, error, refetch } = useQuery(ClassQuizDocument, { variables: { id: quizId }, fetchPolicy: 'cache-and-network' })
  const quiz = data?.classQuiz
  const [retaking, setRetaking] = useState(false)
  if (!quiz) {
    if (loading) return <Loading label={t('loading')} />
    // Not there only when the API said so; a quiz that could not be asked for is offered again.
    return error && !isNotThere(error) ? <LoadFailed onRetry={refetch} /> : <p className="text-muted">{t('notFound')}</p>
  }
  const latest = quiz.myAttempts[0] ?? null
  const first = scoreOf(quiz)
  const answering = !latest || retaking
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Link href={`/classes/${classroomId}`} className="inline-flex items-center gap-1.5 self-start text-sm text-muted hover:text-fg">
        <ArrowLeft className="size-4" aria-hidden />
        {t('back')}
      </Link>
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{quiz.title}</h1>
        <p className="text-sm text-muted">{t('meta', { n: quiz.questionCount, name: quiz.author.displayName, when: new Date(quiz.publishedAt).toLocaleDateString() })}</p>
        {quiz.submittedCount != null ? <p className="text-sm">{t('submitted', { n: quiz.submittedCount })}</p> : null}
      </header>
      {answering ? (
        <TakeQuiz quiz={quiz} practice={!!latest} onDone={() => setRetaking(false)} />
      ) : (
        <>
          <div role="status" className="flex flex-wrap items-center gap-3 rounded-2xl border border-accent/40 bg-accent-soft p-4">
            <span className="text-lg font-bold">{t('result', { score: latest.score, total: latest.total })}</span>
            {first && first.id !== latest.id ? <span className="text-sm text-muted">{t('firstScore', { score: first.score, total: first.total })}</span> : null}
            <span className="flex-1" />
            <Button variant="secondary" size="sm" className="gap-1.5" onClick={() => setRetaking(true)}>
              <RotateCcw className="size-4" aria-hidden />
              {t('again')}
            </Button>
          </div>
          <Review quiz={quiz} answers={Object.fromEntries((quiz.myAttempts[0]?.answers ?? []).map((a) => [a.questionId, a.choiceIds]))} />
        </>
      )}
    </div>
  )
}

function TakeQuiz({ quiz, practice, onDone }: { quiz: Quiz; practice: boolean; onDone: () => void }) {
  const t = useTranslations('classes.quiz')
  const [submit, submitting] = useMutation(SubmitQuizAttemptDocument)
  const [answers, setAnswers] = useState<Answers>({})
  const [error, setError] = useState<string | null>(null)
  // One id per submission, kept until it is answered: a retry is the same attempt (ADR-0064).
  const op = useRef<string | null>(null)
  // One question at a time; moving on takes the reader to the new question.
  const [at, setAt] = useState(0)
  const shown = useRef<HTMLFieldSetElement>(null)
  const moved = useRef(false)
  useEffect(() => {
    if (moved.current) shown.current?.focus()
  }, [at])
  const go = (i: number) => {
    moved.current = true
    setAt(i)
  }
  const total = quiz.questions.length
  const q = quiz.questions[Math.min(at, total - 1)]
  const last = at >= total - 1
  const left = quiz.questions.filter((x) => !answers[x.id]?.length).length
  const pick = (questionId: string, choiceId: string, multiple: boolean) =>
    setAnswers((a) => {
      const now = a[questionId] ?? []
      return { ...a, [questionId]: multiple ? (now.includes(choiceId) ? now.filter((x) => x !== choiceId) : [...now, choiceId]) : [choiceId] }
    })
  const send = async () => {
    setError(null)
    op.current ??= crypto.randomUUID()
    try {
      const res = await submit({ variables: { input: { quizId: quiz.id, clientOpId: op.current, answers: quiz.questions.map((q) => ({ questionId: q.id, choiceIds: answers[q.id] ?? [] })) } } })
      const payload = res.data?.submitQuizAttempt
      if (!payload?.attempt) return setError(payload?.userErrors[0]?.message ?? t('submitFailed'))
      op.current = null
      onDone()
    } catch {
      setError(t('submitFailed'))
    }
  }
  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={(e) => {
        e.preventDefault()
        void send()
      }}
    >
      {practice ? <p className="text-sm text-muted">{t('practice')}</p> : null}
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-3 text-sm">
          <span className="font-semibold" aria-hidden>
            {t('progress', { n: at + 1, total })}
          </span>
          <span className="text-muted">{t('answeredCount', { n: total - left, total })}</span>
        </div>
        <div className="h-1.5 overflow-hidden rounded-full bg-surface-2" role="progressbar" aria-label={t('progressLabel', { n: at + 1, total })} aria-valuemin={1} aria-valuemax={total} aria-valuenow={at + 1}>
          <div className="h-full rounded-full bg-accent transition-[width]" style={{ width: `${((at + 1) / total) * 100}%` }} />
        </div>
      </div>
      {q ? (
        <fieldset ref={shown} tabIndex={-1} key={q.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4 outline-none">
          <legend className="sr-only">{t('progressLabel', { n: at + 1, total })}</legend>
          <div className="flex gap-2">
            <span className="font-bold text-muted">{at + 1}.</span>
            <RichDoc doc={q.question as Doc} className="flex flex-col gap-2 font-medium" />
          </div>
          {q.multiple ? <p className="text-xs text-muted">{t('pickAll')}</p> : null}
          <ul className="flex flex-col gap-1.5">
            {q.choices.map((c) => {
              const on = (answers[q.id] ?? []).includes(c.id)
              return (
                <li key={c.id}>
                  <button
                    type="button"
                    role={q.multiple ? 'checkbox' : 'radio'}
                    aria-checked={on}
                    onClick={() => pick(q.id, c.id, q.multiple)}
                    className={cn('w-full rounded-lg border px-3 py-2 text-left text-sm transition-colors', on ? 'border-accent bg-accent-soft' : 'border-border hover:bg-surface-2')}
                  >
                    <InlineText content={c.content as Inline} />
                  </button>
                </li>
              )
            })}
          </ul>
        </fieldset>
      ) : null}
      <nav aria-label={t('questions')} className="flex flex-wrap gap-1.5">
        {quiz.questions.map((x, i) => {
          const answered = !!answers[x.id]?.length
          return (
            <button
              key={x.id}
              type="button"
              aria-current={i === at ? 'step' : undefined}
              aria-label={answered ? t('goToAnswered', { n: i + 1 }) : t('goTo', { n: i + 1 })}
              onClick={() => go(i)}
              className={cn('size-8 rounded-full border text-xs font-semibold', i === at ? 'border-accent bg-accent text-white' : answered ? 'border-accent/50 bg-accent-soft text-accent' : 'border-border text-muted hover:bg-surface-2')}
            >
              {i + 1}
            </button>
          )
        })}
      </nav>
      {left ? <p className="text-sm text-muted">{t('unanswered', { n: left })}</p> : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <div className="flex flex-wrap items-center gap-2">
        {at > 0 ? (
          <Button type="button" variant="secondary" className="gap-1" onClick={() => go(at - 1)}>
            <ChevronLeft className="size-4" aria-hidden />
            {t('previous')}
          </Button>
        ) : null}
        <span className="flex-1" />
        {practice ? (
          <Button type="button" variant="secondary" onClick={onDone}>
            {t('cancel')}
          </Button>
        ) : null}
        {/* Keys keep Next and Submit apart: one element turned into the other mid-click would submit the quiz. */}
        {last ? (
          <Button key="submit" type="submit" disabled={submitting.loading}>
            {submitting.loading ? t('submitting') : t('submit')}
          </Button>
        ) : (
          <Button key="next" type="button" className="gap-1" onClick={() => go(at + 1)}>
            {t('next')}
            <ChevronRight className="size-4" aria-hidden />
          </Button>
        )}
      </div>
    </form>
  )
}

/** The questions with the viewer's answers, the correct choices and the explanations. */
function Review({ quiz, answers }: { quiz: Quiz; answers: Answers }) {
  const t = useTranslations('classes.quiz')
  return (
    <ol className="flex flex-col gap-4">
      {quiz.questions.map((q, i) => {
        const chosen = answers[q.id] ?? []
        const right = !!q.correct && chosen.length === q.correct.length && chosen.every((c) => q.correct!.includes(c))
        return (
          <li key={q.id} aria-label={t('questionN', { n: i + 1 })} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
            <div className="flex gap-2">
              <span className="font-bold text-muted">{i + 1}.</span>
              <RichDoc doc={q.question as Doc} className="flex flex-1 flex-col gap-2 font-medium" />
              <span className={cn('inline-flex shrink-0 items-center gap-1 self-start rounded-full px-2 py-0.5 text-xs font-semibold', right ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' : 'bg-red-500/10 text-red-700 dark:text-red-400')}>
                {right ? <Check className="size-3" aria-hidden /> : <X className="size-3" aria-hidden />}
                {right ? t('right') : t('wrong')}
              </span>
            </div>
            <ul className="flex flex-col gap-1.5">
              {q.choices.map((c) => {
                const isCorrect = !!q.correct?.includes(c.id)
                const isChosen = chosen.includes(c.id)
                return (
                  <li
                    key={c.id}
                    className={cn('flex items-center gap-2 rounded-lg border px-3 py-2 text-sm', isCorrect ? 'border-emerald-500 bg-emerald-500/10' : isChosen ? 'border-red-500 bg-red-500/10' : 'border-border opacity-70')}
                  >
                    <InlineText content={c.content as Inline} />
                    <span className="flex-1" />
                    {isChosen ? <span className="text-xs font-semibold">{t('yourAnswer')}</span> : null}
                    {isCorrect ? <span className="sr-only">{t('correctAnswer')}</span> : null}
                  </li>
                )
              })}
            </ul>
            {q.explanation ? <RichDoc doc={q.explanation as Doc} className="flex flex-col gap-1 text-sm text-muted" /> : null}
          </li>
        )
      })}
    </ol>
  )
}
