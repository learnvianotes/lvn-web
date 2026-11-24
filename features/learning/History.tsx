'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { LoadFailed } from '@/components/ui/query-state'
import { LearningHistoryDocument, SetLearningTimeZoneDocument, type LearningHistoryQuery } from '@/graphql/generated/graphql'

type Day = LearningHistoryQuery['learningHistory']['days'][number]

const minutes = (seconds: number) => Math.round(seconds / 60)
/** A /core topic's key, readable: "dsa-basics / arrays". */
const coreName = (key: string) => key.replace(/^core:/, '').replace('/', ' / ').replace(/-/g, ' ')

/**
 * Learning history (lvn-backend ADR-0067): the person's days, newest first, in their time zone. A day shows the time
 * they learned and read, reviews and quiz answers, the topics with the most time, and the notes they opened that they
 * can still read. Days that count for Rhythm (ADR-0030) say so; the others are just days, never "missed".
 */
export function History() {
  const t = useTranslations('history')
  const { data, loading, error, refetch, fetchMore } = useQuery(LearningHistoryDocument, { variables: { days: 14 }, fetchPolicy: 'cache-and-network' })
  const history = data?.learningHistory
  const more = async () => {
    if (!history?.nextBefore) return
    const before = history.nextBefore
    await fetchMore({
      variables: { before, days: 14 },
      updateQuery: (prev, { fetchMoreResult }) => ({ learningHistory: { ...fetchMoreResult.learningHistory, days: [...prev.learningHistory.days, ...fetchMoreResult.learningHistory.days] } }),
    })
  }

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {history ? <TimeZone zone={history.timeZone} /> : null}
      {error && !history && !loading ? <LoadFailed message={t('failed')} onRetry={refetch} /> : null}
      {!history && loading ? <p className="text-muted">{t('loading')}</p> : null}
      {history && !history.days.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('empty')}</p> : null}
      <ol className="flex flex-col gap-3">
        {history?.days.map((d) => (
          <li key={d.day}>
            <DayCard day={d} />
          </li>
        ))}
      </ol>
      {history?.nextBefore ? (
        <Button variant="secondary" onClick={() => void more()} disabled={loading}>
          {t('older')}
        </Button>
      ) : null}
    </div>
  )
}

function DayCard({ day: d }: { day: Day }) {
  const t = useTranslations('history')
  const format = useFormatter()
  const date = new Date(`${d.day}T12:00:00Z`)
  const stats = [
    d.learningSeconds >= 60 ? t('learning', { minutes: minutes(d.learningSeconds) }) : null,
    d.readingSeconds >= 60 ? t('reading', { minutes: minutes(d.readingSeconds) }) : null,
    d.reviews ? t('reviews', { count: d.reviews }) : null,
    d.quizAnswers ? t('quizAnswers', { count: d.quizAnswers }) : null,
  ].filter(Boolean)
  const notes = d.notes.filter((n): n is NonNullable<typeof n> => !!n)
  return (
    <article aria-label={format.dateTime(date, { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'UTC' })} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-2">
        <h2 className="font-semibold">{format.dateTime(date, { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'UTC' })}</h2>
        {d.counted ? <span className="rounded-[10px] bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent">{t('counted')}</span> : null}
      </div>
      {stats.length ? <p className="text-sm text-muted">{stats.join(' · ')}</p> : <p className="text-sm text-muted">{t('activity')}</p>}
      {d.topics.length ? (
        <ul aria-label={t('topics')} className="flex flex-wrap gap-2">
          {d.topics.slice(0, 8).map((topic) => (
            <li key={topic.key} className="rounded-full bg-surface-2 px-3 py-1 text-xs">
              {topic.topic?.title ?? (topic.key.startsWith('core:') ? coreName(topic.key) : t('aTopic'))}
              {topic.seconds >= 60 ? ` · ${t('minutesShort', { minutes: minutes(topic.seconds) })}` : ''}
            </li>
          ))}
        </ul>
      ) : null}
      {notes.length ? (
        <ul aria-label={t('notes')} className="flex flex-col gap-1">
          {notes.map((n) => (
            <li key={n.id}>
              <Link href={`/notes/${n.id}`} className="text-sm text-accent hover:underline">
                {n.title || t('untitled')}
              </Link>
            </li>
          ))}
        </ul>
      ) : null}
    </article>
  )
}

/** Days are counted in this zone; the apps send the device's, and the person can set another. */
function TimeZone({ zone }: { zone: string }) {
  const t = useTranslations('history')
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(zone)
  const [problem, setProblem] = useState<string | null>(null)
  const [save, saving] = useMutation(SetLearningTimeZoneDocument, { refetchQueries: [LearningHistoryDocument] })
  const zones = typeof Intl.supportedValuesOf === 'function' ? Intl.supportedValuesOf('timeZone') : [zone]
  if (!editing) {
    return (
      <p className="text-sm text-muted">
        {t('zone', { zone })}{' '}
        <button type="button" className="text-accent hover:underline" onClick={() => setEditing(true)}>
          {t('changeZone')}
        </button>
      </p>
    )
  }
  return (
    <form
      className="flex flex-wrap items-end gap-2"
      onSubmit={async (e) => {
        e.preventDefault()
        const res = await save({ variables: { input: { timeZone: value } } })
        const message = res.data?.setLearningTimeZone.userErrors[0]?.message
        if (message) setProblem(message)
        else setEditing(false)
      }}
    >
      <label className="flex flex-col gap-1 text-sm">
        {t('zoneLabel')}
        <select className="h-11 rounded-xl border border-border bg-surface px-3" value={value} onChange={(e) => setValue(e.target.value)}>
          {zones.map((z) => (
            <option key={z} value={z}>{z}</option>
          ))}
        </select>
      </label>
      <Button type="submit" size="sm" disabled={saving.loading}>
        {t('saveZone')}
      </Button>
      {problem ? <Alert tone="error">{problem}</Alert> : null}
    </form>
  )
}
