'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { MyQuizzesDocument, PublicQuizzesDocument } from '@/graphql/generated/graphql'

type QuizLink = { id: string; title: string; sharePath: string | null }

/** Owned and public quizzes. A public row without sharePath opens by id. */
export function QuizLists() {
  const t = useTranslations('quizShare')
  const mine = useQuery(MyQuizzesDocument, { variables: { first: 20 }, fetchPolicy: 'cache-and-network' })
  const open = useQuery(PublicQuizzesDocument, { variables: { first: 20 }, fetchPolicy: 'cache-and-network' })
  const mineItems = mine.data?.myQuizzes ?? []
  const openItems = open.data?.publicQuizzes ?? []
  if (!mineItems.length && !openItems.length) return null
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      <QuizColumn title={t('mine')} items={mineItems} />
      <QuizColumn title={t('public')} items={openItems} />
    </div>
  )
}

function QuizColumn({ title, items }: { title: string; items: QuizLink[] }) {
  if (!items.length) return null
  return (
    <section className="flex flex-col gap-2">
      <h2 className="text-sm font-bold uppercase tracking-wide text-muted">{title}</h2>
      <ul className="flex flex-col gap-2">
        {items.map((quiz) => (
          <li key={quiz.id}>
            <Link href={quiz.sharePath || `/q/${quiz.id}`} className="block rounded-xl border border-border bg-surface px-3 py-2 text-sm font-semibold hover:border-sky-600">
              {quiz.title}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
