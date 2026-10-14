'use client'

import { useQuery } from '@apollo/client/react'
import { Trophy } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { QueryState } from '@/components/ui/query-state'
import { ContestsDocument, type ContestsQuery } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

type Item = ContestsQuery['contests'][number]

/**
 * Weekly contests (lvn-backend ADR-0082): the open one as board A draws it, then upcoming and recent ones. A contest
 * is a timed quiz with explanations after it; there is no table of names, only each person's own score.
 */
export function ContestsPage() {
  const t = useTranslations('contests')
  const { data, loading, error, refetch } = useQuery(ContestsDocument, { fetchPolicy: 'cache-and-network' })
  const list = data?.contests ?? []
  const open = list.filter((c) => c.state === 'OPEN')
  const rest = list.filter((c) => c.state !== 'OPEN')
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {open.map((c) => (
        <ContestHero key={c.id} contest={c} />
      ))}
      {data && !list.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-sm text-muted">{t('none')}</p> : null}
      {!data ? <QueryState loading={loading} error={error} onRetry={refetch} /> : null}
      {rest.length ? (
        <ul className="flex flex-col gap-2">
          {rest.map((c) => (
            <ContestRow key={c.id} contest={c} />
          ))}
        </ul>
      ) : null}
    </div>
  )
}

/** The open contest, as board A draws its "Weekly Contest" card. */
export function ContestHero({ contest: c }: { contest: Item }) {
  const t = useTranslations('contests')
  const done = c.viewerAttempt?.finished
  return (
    <section aria-label={c.title} className="flex flex-col gap-4 overflow-hidden rounded-3xl bg-gradient-to-br from-[#1C1A3A] to-[#2B2560] p-6 text-white shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <p className="text-xs font-semibold uppercase tracking-wide text-white/70">{t('weekly')}</p>
          <h2 className="text-2xl font-extrabold">{c.title}</h2>
          <p className="text-sm text-white/80">{c.subjectTitle ? t('testOn', { subject: c.subjectTitle }) : t('testYourself')}</p>
        </div>
        <Trophy aria-hidden className="size-14 shrink-0 text-amber-300" />
      </div>
      <p className="flex flex-wrap gap-x-5 gap-y-1 text-sm text-white/90">
        <span>{t('questions', { count: c.questionCount })}</span>
        <span>{t('minutes', { count: c.minutes })}</span>
        {c.participantsMilestone ? <span>{t('participants', { count: c.participantsMilestone })}</span> : null}
      </p>
      <Link href={`/contests/${c.id}`} className="inline-flex h-11 items-center justify-center rounded-xl bg-accent px-5 font-semibold text-accent-fg hover:opacity-90">
        {done ? t('seeAnswers') : c.viewerAttempt ? t('continue') : t('join')}
      </Link>
    </section>
  )
}

function ContestRow({ contest: c }: { contest: Item }) {
  const t = useTranslations('contests')
  const format = useFormatter()
  const when = c.state === 'UPCOMING' ? t('opens', { at: format.dateTime(new Date(c.opensAt), { weekday: 'short', day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }) }) : t('closed', { at: format.dateTime(new Date(c.closesAt), { day: 'numeric', month: 'short' }) })
  return (
    <li>
      <Link href={`/contests/${c.id}`} className="flex flex-wrap items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent">
        <span className="flex min-w-0 flex-1 flex-col">
          <span className="font-semibold">{c.title}</span>
          <span className="text-sm text-muted">{when}</span>
        </span>
        {c.viewerAttempt?.finished ? <span className="text-sm font-semibold">{t('score', { score: c.viewerAttempt.score ?? 0, total: c.viewerAttempt.total })}</span> : null}
        <span className={cn('rounded-full px-2.5 py-0.5 text-xs font-semibold', c.state === 'UPCOMING' ? 'bg-accent-soft text-accent' : 'bg-surface-2 text-muted')}>{t(`state.${c.state}`)}</span>
      </Link>
    </li>
  )
}
