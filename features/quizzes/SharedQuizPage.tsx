'use client'

import { useApolloClient } from '@apollo/client/react'
import { ListChecks } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { loadSharedQuiz, submitSharedQuiz, type SharedQuiz } from '@/features/beta/api'
import { Button } from '@/components/ui/button'

/** A quiz opened from a share link. The questions have no answers until it is submitted. */
export function SharedQuizPage({ token }: { token: string }) {
  const t = useTranslations('quizShare')
  const client = useApolloClient()
  const [quiz, setQuiz] = useState<SharedQuiz | null>(null)
  const [missing, setMissing] = useState(false)
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [score, setScore] = useState<{ score: number; total: number } | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let cancel = false
    void loadSharedQuiz(client, token)
      .then((loaded) => {
        if (cancel) return
        if (!loaded) setMissing(true)
        else setQuiz(loaded)
      })
      .catch(() => {
        if (!cancel) setMissing(true)
      })
    return () => {
      cancel = true
    }
  }, [client, token])

  const send = async () => {
    if (!quiz) return
    setBusy(true)
    setError(null)
    try {
      const payload = await submitSharedQuiz(
        client,
        token,
        quiz.questions.map((question) => ({ questionId: question.id, choiceId: answers[question.id] ?? '' })),
      )
      const problem = payload.userErrors?.[0]?.message
      if (problem || payload.score == null || payload.total == null) {
        setError(problem ?? t('submitFailed'))
        return
      }
      setScore({ score: payload.score, total: payload.total })
    } catch {
      setError(t('submitFailed'))
    } finally {
      setBusy(false)
    }
  }

  if (missing) return <p className="mx-auto max-w-xl py-16 text-center text-muted">{t('missing')}</p>
  if (!quiz) return <p className="mx-auto max-w-xl py-16 text-center text-muted">{t('loading')}</p>
  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-5 px-4 py-8">
      <header className="flex flex-col gap-1 rounded-3xl border border-sky-700/25 bg-sky-50 px-4 py-4 dark:bg-sky-950/40">
        <p className="text-xs font-bold uppercase tracking-wider text-sky-800 dark:text-sky-200">{t('taking')}</p>
        <h1 className="flex items-center gap-2 text-2xl font-extrabold tracking-tight">
          <ListChecks className="size-6" aria-hidden />
          {quiz.title}
        </h1>
        <p className="text-sm text-muted">{t('by', { name: quiz.ownerName })}</p>
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
          {quiz.questions.map((question, index) => (
            <fieldset key={question.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
              <legend className="px-1 text-sm font-semibold">{t('question', { n: index + 1, prompt: question.prompt })}</legend>
              {question.choices.map((choice) => (
                <label key={choice.id} className="flex items-center gap-2 text-sm">
                  <input type="radio" name={question.id} value={choice.id} checked={answers[question.id] === choice.id} onChange={() => setAnswers((current) => ({ ...current, [question.id]: choice.id }))} />
                  {choice.text}
                </label>
              ))}
            </fieldset>
          ))}
          {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
          <Button type="submit" disabled={busy}>{t('submit')}</Button>
        </form>
      )}
    </div>
  )
}
