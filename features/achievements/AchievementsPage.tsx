'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Award } from 'lucide-react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { QueryState } from '@/components/ui/query-state'
import { MyAchievementsDocument, MyPointsDocument, SetAchievementsShownDocument } from '@/graphql/generated/graphql'
import { AchievementBadges } from './AchievementBadges'

const LEVEL_FROM = { NEWCOMER: 0, CONTRIBUTOR: 50, TRUSTED: 250 } as const

/**
 * The person's achievements, level and points (lvn-backend ADR-0080): what they learned, and what others did with what
 * they made public. Private unless an adult shows them on their profile.
 */
export function AchievementsPage() {
  const t = useTranslations('achievements')
  const { data, loading, error, refetch } = useQuery(MyAchievementsDocument, { fetchPolicy: 'cache-and-network' })
  const viewer = data?.viewer
  const items = viewer?.achievements ?? []
  return (
    <div className="flex flex-col gap-8">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>

      {viewer?.contribution ? <Level contribution={viewer.contribution} /> : null}

      <section aria-labelledby="earned" className="flex flex-col gap-3">
        <h2 id="earned" className="text-lg font-bold">
          {t('earned')}
        </h2>
        {items.length ? (
          <AchievementBadges items={items} />
        ) : !data ? (
          <QueryState loading={loading} error={error} onRetry={refetch} />
        ) : (
          <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-sm text-muted">
            {t('none')}{' '}
            <Link href="/review" className="font-semibold text-accent hover:underline">
              {t('review')}
            </Link>
            {' · '}
            <Link href="/exams" className="font-semibold text-accent hover:underline">
              {t('exams')}
            </Link>
            {' · '}
            <Link href="/rhythm" className="font-semibold text-accent hover:underline">
              {t('rhythm')}
            </Link>
          </p>
        )}
      </section>

      {data ? <Visibility key={String(data.achievementSettings.showAchievements)} shown={data.achievementSettings.showAchievements} canShow={data.achievementSettings.canShow} /> : null}

      <History />
    </div>
  )
}

function Level({ contribution }: { contribution: { points: number; level: 'NEWCOMER' | 'CONTRIBUTOR' | 'TRUSTED'; nextLevelAt?: number | null } }) {
  const t = useTranslations('achievements')
  const { points, level, nextLevelAt } = contribution
  const from = LEVEL_FROM[level]
  const progress = nextLevelAt ? Math.round(((points - from) / (nextLevelAt - from)) * 100) : 100
  return (
    <section aria-labelledby="level" className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <span aria-hidden className="grid size-12 place-items-center rounded-full bg-accent-soft text-accent">
          <Award className="size-6" />
        </span>
        <div className="flex min-w-0 flex-1 flex-col">
          <h2 id="level" className="text-lg font-bold">
            {t(`level.${level}`)}
          </h2>
          <p className="text-sm text-muted">{t('points', { points })}</p>
        </div>
      </div>
      {nextLevelAt ? (
        <div className="flex flex-col gap-1">
          <div className="h-2 overflow-hidden rounded-full bg-surface-2" role="progressbar" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress} aria-label={t('toNext', { points: nextLevelAt - points })}>
            <div className="h-full rounded-full bg-accent transition-[width] duration-300" style={{ width: `${progress}%` }} />
          </div>
          <p className="text-xs text-muted">{t('toNext', { points: nextLevelAt - points })}</p>
        </div>
      ) : null}
      <p className="text-sm text-muted">{t('how')}</p>
    </section>
  )
}

function Visibility({ shown, canShow }: { shown: boolean; canShow: boolean }) {
  const t = useTranslations('achievements')
  const [on, setOn] = useState(shown)
  const [set, setting] = useMutation(SetAchievementsShownDocument, { refetchQueries: [MyAchievementsDocument] })
  if (!canShow) return <p className="text-sm text-muted">{t('privateUnder18')}</p>
  return (
    <label className="flex items-start gap-3 text-sm">
      <input
        type="checkbox"
        className="mt-1 size-4"
        checked={on}
        disabled={setting.loading}
        onChange={async (e) => {
          const next = e.target.checked
          setOn(next)
          const res = await set({ variables: { show: next } }).catch(() => null)
          if (!res?.data?.setAchievementsShown.settings) setOn(!next)
        }}
      />
      <span className="flex flex-col">
        <span className="font-medium">{t('show')}</span>
        <span className="text-muted">{t('showHelp')}</span>
      </span>
    </label>
  )
}

function History() {
  const t = useTranslations('achievements')
  const format = useFormatter()
  const { data, fetchMore, loading, error, refetch } = useQuery(MyPointsDocument, { variables: { first: 20 }, fetchPolicy: 'cache-and-network' })
  const entries = data?.myPoints.edges.map((e) => e.node) ?? []
  const page = data?.myPoints.pageInfo
  return (
    <section aria-labelledby="history" className="flex flex-col gap-3">
      <h2 id="history" className="text-lg font-bold">
        {t('history')}
      </h2>
      {!data ? <QueryState loading={loading} error={error} onRetry={refetch} /> : null}
      {data && !entries.length ? <p className="text-sm text-muted">{t('noPoints')}</p> : null}
      {entries.length ? (
      <ul className="flex flex-col divide-y divide-border rounded-2xl border border-border bg-surface">
        {entries.map((e) => (
          <li key={e.id} className="flex items-center gap-3 px-4 py-3 text-sm">
            <span className={`w-10 shrink-0 font-bold tabular-nums ${e.delta > 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-muted'}`}>{e.delta > 0 ? `+${e.delta}` : e.delta}</span>
            <Link href={e.sourceType === 'NOTE' ? `/notes/${e.sourceId}` : `/resources/${e.sourceId}`} className="min-w-0 flex-1 hover:underline">
              {t(`rule.${e.rule}${e.delta < 0 ? '_BACK' : ''}`)}
              {e.subjectTitle ? <span className="text-muted"> · {e.subjectTitle}</span> : null}
            </Link>
            <time dateTime={e.createdAt} className="shrink-0 text-xs text-muted">
              {format.dateTime(new Date(e.createdAt), { day: 'numeric', month: 'short' })}
            </time>
          </li>
        ))}
      </ul>
      ) : null}
      {page?.hasNextPage ? (
        <Button type="button" variant="secondary" size="sm" className="self-start" disabled={loading} onClick={() => void fetchMore({ variables: { after: page.endCursor }, updateQuery: (prev, { fetchMoreResult }) => ({ myPoints: { ...fetchMoreResult.myPoints, edges: [...prev.myPoints.edges, ...fetchMoreResult.myPoints.edges] } }) })}>
          {t('more')}
        </Button>
      ) : null}
    </section>
  )
}
