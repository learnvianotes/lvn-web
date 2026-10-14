'use client'

import { useQuery } from '@apollo/client/react'
import { Layers, ListChecks, Target } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { ContestsDocument, QuizzesHubDocument } from '@/graphql/generated/graphql'
import { ContestHero } from './ContestsPage'

/**
 * Quizzes (lvn-backend ADR-0082; board A's sidebar entry): this week's contest, the class quizzes not taken yet, ways
 * to practise, and recent results, gathered from what already exists.
 */
export function QuizzesPage() {
  const t = useTranslations('quizzes')
  const contests = useQuery(ContestsDocument, { fetchPolicy: 'cache-and-network' }).data?.contests ?? []
  const hub = useQuery(QuizzesHubDocument, { fetchPolicy: 'cache-and-network' })
  const open = contests.find((c) => c.state === 'OPEN')
  const waiting = (hub.data?.myClassrooms ?? []).flatMap((c) => (c.quizzes ?? []).filter((q) => !q.myAttempts.some((x) => x.submittedAt)).map((q) => ({ ...q, classroom: c })))
  const recent = [
    ...contests.filter((c) => c.viewerAttempt?.finished).map((c) => ({ key: c.id, href: `/contests/${c.id}`, title: c.title, score: c.viewerAttempt!.score ?? 0, total: c.viewerAttempt!.total })),
    ...(hub.data?.myClassrooms ?? []).flatMap((c) => (c.quizzes ?? []).flatMap((q) => q.myAttempts.filter((x) => x.submittedAt).slice(0, 1).map((x) => ({ key: x.id, href: `/classes/${c.id}/quizzes/${q.id}`, title: q.title, score: x.score ?? 0, total: x.total })))),
  ].slice(0, 8)
  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>

      {open ? (
        <ContestHero contest={open} />
      ) : (
        <p className="text-sm text-muted">
          {t('noContest')}{' '}
          <Link href="/contests" className="font-semibold text-accent hover:underline">
            {t('allContests')}
          </Link>
        </p>
      )}

      <section aria-labelledby="class-quizzes" className="flex flex-col gap-3">
        <h2 id="class-quizzes" className="text-lg font-bold">
          {t('fromClasses')}
        </h2>
        {hub.data && !waiting.length ? <p className="text-sm text-muted">{t('noneWaiting')}</p> : null}
        <ul className="flex flex-col gap-2">
          {waiting.map((q) => (
            <li key={q.id}>
              <Link href={`/classes/${q.classroom.id}/quizzes/${q.id}`} className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent">
                <ListChecks aria-hidden className="size-5 text-accent" />
                <span className="flex min-w-0 flex-1 flex-col">
                  <span className="font-semibold">{q.title}</span>
                  <span className="text-sm text-muted">{t('inClass', { classroom: q.classroom.name, count: q.questionCount })}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="practice" className="flex flex-col gap-3">
        <h2 id="practice" className="text-lg font-bold">
          {t('practice')}
        </h2>
        <div className="grid gap-3 sm:grid-cols-2">
          <Link href="/review" className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent">
            <Layers aria-hidden className="size-5 text-accent" />
            <span className="flex flex-col">
              <span className="font-semibold">{t('review')}</span>
              <span className="text-sm text-muted">{t('reviewHelp')}</span>
            </span>
          </Link>
          <Link href="/exams" className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent">
            <Target aria-hidden className="size-5 text-accent" />
            <span className="flex flex-col">
              <span className="font-semibold">{t('weak')}</span>
              <span className="text-sm text-muted">{t('weakHelp')}</span>
            </span>
          </Link>
        </div>
      </section>

      {recent.length ? (
        <section aria-labelledby="recent" className="flex flex-col gap-3">
          <h2 id="recent" className="text-lg font-bold">
            {t('recent')}
          </h2>
          <ul className="flex flex-col divide-y divide-border rounded-2xl border border-border bg-surface">
            {recent.map((r) => (
              <li key={r.key}>
                <Link href={r.href} className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-surface-2">
                  <span className="font-medium">{r.title}</span>
                  <span className="text-muted">{t('score', { score: r.score, total: r.total })}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  )
}
