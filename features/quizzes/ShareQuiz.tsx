'use client'

import { useLazyQuery, useMutation } from '@apollo/client/react'
import { Check, Copy, Share2 } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { absoluteUrl, type QuizShareStats } from '@/features/beta/api'
import { Button } from '@/components/ui/button'
import { CreateSharedQuizDocument, SetSharedQuizVisibilityDocument, SharedQuizDocument, type SharedQuizQuery } from '@/graphql/generated/graphql'

type Owned = NonNullable<SharedQuizQuery['sharedQuiz']>

/** The owner shares a link. Anyone with it can take the quiz. Stats stay here. */
export function ShareQuiz({ title, questions }: { title: string; questions: unknown[] }) {
  const t = useTranslations('quizShare')
  const [createQuiz] = useMutation(CreateSharedQuizDocument)
  const [setVisibility] = useMutation(SetSharedQuizVisibilityDocument)
  const [loadQuiz] = useLazyQuery(SharedQuizDocument, { fetchPolicy: 'network-only' })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [link, setLink] = useState<string | null>(null)
  const [stats, setStats] = useState<QuizShareStats | null>(null)
  const [copied, setCopied] = useState(false)
  if (!questions.length) return null

  const share = async () => {
    setBusy(true)
    setError(null)
    try {
      const created = await createQuiz({
        variables: {
          input: {
            title: title.trim() || t('title'),
            questions: questions.slice(0, 50),
            visibility: 'UNLISTED',
          },
        },
      })
      const payload = created.data?.createSharedQuiz
      const problem = payload?.userErrors[0]?.message
      const id = payload?.quiz?.id
      if (problem || !id) {
        setError(problem ?? t('failed'))
        return
      }
      let quiz = (await loadQuiz({ variables: { id } })).data?.sharedQuiz ?? null
      if (quiz && !quiz.sharePath) {
        const visible = await setVisibility({ variables: { input: { quizId: id, visibility: 'UNLISTED' } } })
        const visProblem = visible.data?.setSharedQuizVisibility.userErrors[0]?.message
        if (visProblem) {
          setError(visProblem)
          return
        }
        quiz = (await loadQuiz({ variables: { id } })).data?.sharedQuiz ?? quiz
      }
      if (!quiz?.sharePath) {
        setError(t('failed'))
        return
      }
      setLink(absoluteUrl(quiz.sharePath, window.location.origin))
      setStats(statsOf(quiz))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const copy = async () => {
    if (!link) return
    try {
      await navigator.clipboard.writeText(link)
      setCopied(true)
      setTimeout(() => setCopied(false), 1600)
    } catch {
      window.prompt(t('copy'), link)
    }
  }

  return (
    <section aria-label={t('title')} className="flex flex-col gap-3 rounded-2xl border border-sky-700/30 bg-sky-50 p-4 dark:bg-sky-950/30">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-bold">{t('title')}</h3>
        <Button type="button" size="sm" variant="secondary" className="gap-1.5" disabled={busy} onClick={() => void share()}>
          <Share2 className="size-4" aria-hidden />
          {t('share')}
        </Button>
      </div>
      <p className="text-sm text-muted">{t('lead')}</p>
      {error ? <p role="alert" className="text-sm text-red-600 dark:text-red-400">{error}</p> : null}
      {link ? (
        <div className="flex flex-col gap-2">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('link')}</span>
            <input readOnly value={link} className="h-10 rounded-lg border border-border bg-surface px-2 text-xs" onFocus={(event) => event.currentTarget.select()} />
          </label>
          <Button type="button" size="sm" variant="secondary" className="w-fit gap-1.5" onClick={() => void copy()}>
            {copied ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}
            {copied ? t('copied') : t('copy')}
          </Button>
        </div>
      ) : null}
      {stats ? (
        <p className="text-sm font-medium" data-testid="quiz-stats">
          {t('stats', { attempts: stats.attempts, average: stats.averageScore, total: stats.total })}
        </p>
      ) : null}
    </section>
  )
}

/** averageScore is a fraction of the questions. Show it as a score out of questionCount. */
function statsOf(quiz: Owned): QuizShareStats | null {
  const stats = quiz.stats
  if (!stats || stats.averageScore == null) return null
  return {
    attempts: stats.scoredAttempts,
    averageScore: Math.round(stats.averageScore * quiz.questionCount),
    total: quiz.questionCount,
  }
}
