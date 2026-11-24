'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { ListChecks, Plus, Trash } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { attempt } from '@/features/groups/shared'
import { ago } from '@/features/notes/look'
import { ClassroomQuizzesDocument, DeleteClassQuizDocument, type ClassQuizListFieldsFragment, type ClassroomDetailFragment } from '@/graphql/generated/graphql'
import { QuizBuilder } from './QuizBuilder'

/** A person's score on a quiz: their first attempt (ADR-0064); attempts come newest first. */
export const scoreOf = (q: Pick<ClassQuizListFieldsFragment, 'myAttempts'>) => q.myAttempts.at(-1) ?? null

/** The class's quizzes (lvn-backend ADR-0064): every member takes them; staff publish and remove them. */
export function ClassQuizzes({ classroom }: { classroom: ClassroomDetailFragment }) {
  const t = useTranslations('classes.quiz')
  const { data, loading, refetch } = useQuery(ClassroomQuizzesDocument, { variables: { id: classroom.id }, fetchPolicy: 'cache-and-network' })
  const [remove] = useMutation(DeleteClassQuizDocument)
  const [building, setBuilding] = useState(false)
  const [notice, setNotice] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const quizzes = data?.classroom?.quizzes ?? []
  const staff = classroom.viewerCan.publishQuiz

  return (
    <div className="flex flex-col gap-4">
      {staff ? (
        <div className="flex flex-wrap items-center gap-3">
          <Button className="gap-1.5" onClick={() => setBuilding(true)}>
            <Plus className="size-4" aria-hidden />
            {t('new')}
          </Button>
          <p className="text-xs text-muted">{t('newHint')}</p>
        </div>
      ) : null}
      {notice ? (
        <p role="status" className="text-sm font-medium text-accent">
          {notice}
        </p>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
      {loading && !data ? <p className="text-sm text-muted">{t('loading')}</p> : null}
      {data && !quizzes.length ? <p className="text-sm text-muted">{staff ? t('noneStaff') : t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {quizzes.map((q) => {
          const score = scoreOf(q)
          return (
            <li key={q.id} className="flex items-start gap-3 rounded-2xl border border-border bg-surface p-4">
              <ListChecks className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden />
              <div className="flex min-w-0 flex-1 flex-col gap-1">
                <Link href={`/classes/${classroom.id}/quizzes/${q.id}`} className="font-semibold hover:text-accent">
                  {q.title}
                </Link>
                <span className="text-xs text-muted">{t('meta', { n: q.questionCount, name: q.author.displayName, when: ago(q.publishedAt) })}</span>
                <span className="text-sm">
                  {score ? t('yourScore', { score: score.score, total: score.total }) : t('notTaken')}
                  {q.submittedCount != null ? <span className="text-muted"> · {t('submitted', { n: q.submittedCount })}</span> : null}
                </span>
              </div>
              <Link href={`/classes/${classroom.id}/quizzes/${q.id}`} className="shrink-0 rounded-full border border-border px-3 py-1.5 text-sm font-semibold hover:bg-surface-2">
                {score ? t('open') : t('take')}
              </Link>
              {q.viewerCanDelete ? (
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={t('delete', { title: q.title })}
                  title={t('delete', { title: q.title })}
                  onClick={() => {
                    if (!window.confirm(t('deleteConfirm', { title: q.title }))) return
                    void attempt(() => remove({ variables: { quizId: q.id } }), t('failed')).then((p) => {
                      setError(p)
                      void refetch()
                    })
                  }}
                >
                  <Trash className="size-4" aria-hidden />
                </Button>
              ) : null}
            </li>
          )
        })}
      </ul>
      {staff ? (
        <QuizBuilder
          classroomId={classroom.id}
          open={building}
          onClose={() => setBuilding(false)}
          onPublished={() => {
            setBuilding(false)
            setNotice(t('published'))
            void refetch()
          }}
        />
      ) : null}
    </div>
  )
}
