'use client'

import { useApolloClient } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { loadMyQuizzes, loadPublicQuizzes, type QuizListItem } from '@/features/beta/api'

/** Owned and public quizzes from contracts 0.74.0. Empty when the API does not answer yet. */
export function QuizLists() {
  const t = useTranslations('quizShare')
  const client = useApolloClient()
  const [mine, setMine] = useState<QuizListItem[]>([])
  const [open, setOpen] = useState<QuizListItem[]>([])
  useEffect(() => {
    let cancel = false
    void loadMyQuizzes(client)
      .then((list) => {
        if (!cancel) setMine(list)
      })
      .catch(() => undefined)
    void loadPublicQuizzes(client)
      .then((list) => {
        if (!cancel) setOpen(list)
      })
      .catch(() => undefined)
    return () => {
      cancel = true
    }
  }, [client])
  if (!mine.length && !open.length) return null
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <QuizColumn title={t('mine')} items={mine} />
      <QuizColumn title={t('public')} items={open} />
    </div>
  )
}

function QuizColumn({ title, items }: { title: string; items: QuizListItem[] }) {
  if (!items.length) return null
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-sm font-bold uppercase tracking-wide text-muted">{title}</h2>
      <ul className="flex flex-col gap-2">
        {items.map((quiz) => (
          <li key={quiz.id}>
            <Link href={quiz.path || `/q/${quiz.token}`} className="block rounded-xl border border-border bg-surface px-3 py-2 text-sm font-semibold hover:border-sky-600">
              {quiz.title}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
