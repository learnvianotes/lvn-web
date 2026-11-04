'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { ListChecks } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { InlineText, RichDoc } from '@/features/notes/render/RichText'
import { SharedQuizByLinkDocument, SharedQuizDocument, SubmitSharedQuizAttemptDocument, type SharedQuizQuestionFieldsFragment } from '@/graphql/generated/graphql'
import { trackQuizStart } from '@/lib/analytics'
import type { Doc, Inline } from '@/lib/contracts/validation'

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

type TakeQuestion = SharedQuizQuestionFieldsFragment

type TakeQuiz = {
  id: string
  title: string
  owner: { displayName: string }
  questions: TakeQuestion[]
}

/** A quiz opened from a share link, or by id when the list has no sharePath. */
export function SharedQuizPage({ token }: { token: string }) {
  const t = useTranslations('quizShare')
  const byLink = useQuery(SharedQuizByLinkDocument, { variables: { token }, fetchPolicy: 'network-only' })
  const linkQuiz = byLink.data?.sharedQuizByLink ?? null
  const tryId = !byLink.loading && !linkQuiz && UUID.test(token)
  const byId = useQuery(SharedQuizDocument, { variables: { id: token }, skip: !tryId, fetchPolicy: 'network-only' })
  const quiz: TakeQuiz | null = linkQuiz ?? (tryId ? byId.data?.sharedQuiz ?? null : null)
  const loading = byLink.loading || (tryId && byId.loading)
  const [answers, setAnswers] = useState<Record<string, string[]>>({})
  const [score, setScore] = useState<{ score: number; total: number } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [submit] = useMutation(SubmitSharedQuizAttemptDocument)
  const op = useRef<string | null>(null)
  // The questions are on screen to answer: a quiz start (lvn-backend ADR-0107).
  const quizId = quiz?.id
  useEffect(() => {
    if (quizId) trackQuizStart('shared')
  }, [quizId])

  const send = async () => {
    if (!quiz) return
    setBusy(true)
    setError(null)
    op.current ??= crypto.randomUUID()
    try {
      const res = await submit({
        variables: {
          input: {
            quizId: quiz.id,
            clientOpId: op.current,
            answers: quiz.questions.map((question) => ({ questionId: question.id, choiceIds: answers[question.id] ?? [] })),
          },
        },
      })
      const payload = res.data?.submitSharedQuizAttempt
      const problem = payload?.userErrors[0]?.message
      if (problem || !payload?.attempt) {
        setError(problem ?? t('submitFailed'))
        return
      }
      setScore({ score: payload.attempt.score, total: payload.attempt.total })
    } catch {
      setError(t('submitFailed'))
    } finally {
      setBusy(false)
    }
  }

  if (loading && !quiz) return <p className="mx-auto max-w-xl py-16 text-center text-muted">{t('loading')}</p>
  if (!quiz) return <p className="mx-auto max-w-xl py-16 text-center text-muted">{t('missing')}</p>
  const questions = [...quiz.questions].sort((a, b) => a.position - b.position)
  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-5 px-4 py-8">
      <header className="flex flex-col gap-1 rounded-3xl border border-sky-700/25 bg-sky-50 px-4 py-4 dark:bg-sky-950/40">
        <p className="text-xs font-bold uppercase tracking-wider text-sky-800 dark:text-sky-200">{t('taking')}</p>
        <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight">
          <ListChecks className="size-6" aria-hidden />
          {quiz.title}
        </h1>
        <p className="text-sm text-muted">{t('by', { name: quiz.owner.displayName })}</p>
      </header>
      {score ? (
        <p role="status" className="rounded-2xl border border-emerald-600/30 bg-emerald-50 px-4 py-3 text-lg font-bold text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-100">
          {t('score', { score: score.score, total: score.total })}
        </p>
      ) : (
        <form
          className="flex flex-col gap-4"
          onSubmit={(event) => {
            event.preventDefault()
            void send()
          }}
        >
          {questions.map((question, index) => (
            <fieldset key={question.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
              <legend className="px-1 text-sm font-semibold">
                <span className="mr-1">{index + 1}.</span>
                <RichDoc doc={question.question as Doc} className="inline" />
              </legend>
              {question.choices.map((choice) => {
                const picked = answers[question.id] ?? []
                const on = picked.includes(choice.id)
                return (
                  <label key={choice.id} className="flex items-center gap-2 text-sm">
                    <input
                      type={question.multiple ? 'checkbox' : 'radio'}
                      name={question.id}
                      value={choice.id}
                      checked={on}
                      onChange={() => {
                        setAnswers((current) => {
                          const now = current[question.id] ?? []
                          const next = question.multiple ? (on ? now.filter((id) => id !== choice.id) : [...now, choice.id]) : [choice.id]
                          return { ...current, [question.id]: next }
                        })
                      }}
                    />
                    <InlineText content={choice.content as Inline} />
                  </label>
                )
              })}
            </fieldset>
          ))}
          {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
          <Button type="submit" disabled={busy}>{t('submit')}</Button>
        </form>
      )}
    </div>
  )
}
