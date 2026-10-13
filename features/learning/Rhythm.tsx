'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useFormatter, useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { EndRhythmPauseDocument, PauseRhythmDocument, RhythmDocument, SetRhythmPlanDocument, type RhythmPauseReason, type RhythmQuery } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { Buddies, FocusMode, ShareRhythm } from './Focus'
import { Recommendations } from './Recommendations'

type R = RhythmQuery['rhythm']

const WEEKDAYS = [1, 2, 3, 4, 5, 6, 7]
const REASONS: RhythmPauseReason[] = ['EXAMS', 'ILLNESS', 'FESTIVAL', 'TRAVEL', 'OTHER']
/** The bar a day counts at (lvn-backend ADR-0030): 10 learning minutes or 10 reviews. */
const BAR_SECONDS = 600
const BAR_REVIEWS = 10
const addDays = (day: string, n: number) => new Date(Date.parse(`${day}T00:00:00Z`) + n * 86_400_000).toISOString().slice(0, 10)

/**
 * Rhythm (lvn-backend ADR-0030, ADR-0069): today's ring and how far today is from counting, this week from Monday to
 * Sunday, the counters that never reset, the planned days and pauses. Never red, never "lost": a missed planned day is
 * only "not counted", and the day after it is a comeback.
 */
export function Rhythm() {
  const t = useTranslations('rhythm')
  const { data, loading, error } = useQuery(RhythmDocument, { fetchPolicy: 'cache-and-network' })
  const r = data?.rhythm
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {error && !r ? <Alert tone="error">{t('failed')}</Alert> : null}
      {!r && loading ? <p className="text-muted">{t('loading')}</p> : null}
      {r ? (
        <>
          <Today r={r} />
          {r.suggestion ? (
            <p role="note" className="rounded-2xl border border-accent/30 bg-accent-soft px-4 py-3 text-sm">
              {t('suggestion', { exam: r.suggestion.examName, days: r.suggestion.daysLeft, planned: r.suggestion.plannedDays })}{' '}
              <a href="#rhythm-plan" className="font-semibold text-accent hover:underline">
                {t('suggestionAction')}
              </a>
            </p>
          ) : null}
          <Week r={r} />
          <Counters r={r} />
          <FocusMode />
          <Recommendations />
          <Buddies />
          <Plan r={r} />
          <Pauses r={r} />
          <ShareRhythm shared={r.shareRhythm} />
          <p className="text-xs text-muted">{t('zone', { zone: r.timeZone })}</p>
        </>
      ) : null}
    </div>
  )
}

/** The ring fills towards a counted day: learning minutes or reviews, whichever is further along. */
export function ringShare(today: Pick<R['today'], 'learningSeconds' | 'reviews' | 'counted'>): number {
  if (today.counted) return 1
  return Math.min(Math.max(today.learningSeconds / BAR_SECONDS, today.reviews / BAR_REVIEWS), 1)
}

function Ring({ share, comeback }: { share: number; comeback: boolean }) {
  const t = useTranslations('rhythm')
  const radius = 42
  const length = 2 * Math.PI * radius
  return (
    <svg viewBox="0 0 100 100" className="size-28 shrink-0 -rotate-90" role="img" aria-label={t('ring', { percent: Math.round(share * 100) })}>
      <circle cx="50" cy="50" r={radius} fill="none" strokeWidth="10" className="stroke-surface-2" />
      <circle
        cx="50"
        cy="50"
        r={radius}
        fill="none"
        strokeWidth={comeback ? 14 : 10}
        strokeLinecap="round"
        strokeDasharray={length}
        strokeDashoffset={length * (1 - share)}
        className="stroke-accent transition-[stroke-dashoffset] duration-700"
      />
    </svg>
  )
}

function Today({ r }: { r: R }) {
  const t = useTranslations('rhythm')
  const today = r.today
  const minutesLeft = Math.max(Math.ceil((BAR_SECONDS - today.learningSeconds) / 60), 0)
  const reviewsLeft = Math.max(BAR_REVIEWS - today.reviews, 0)
  return (
    <section aria-labelledby="rhythm-today" className="flex flex-col gap-4 rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between gap-2">
        <h2 id="rhythm-today" className="text-lg font-bold">
          {t('today')}
        </h2>
        {today.counted ? <span className="rounded-full bg-accent-soft px-3 py-1 text-xs font-semibold text-accent">{t('counted')}</span> : null}
      </div>
      <div className="flex items-center gap-5">
        <Ring share={ringShare(today)} comeback={today.comeback} />
        <div className="flex flex-col gap-2 text-sm">
          {today.cameBack ? <p className="font-semibold text-accent">{t('cameBack')}</p> : null}
          {today.comeback ? <p className="font-semibold text-accent">{t('comeback')}</p> : null}
          {!today.counted ? <p className="text-muted">{t('toGo', { minutes: minutesLeft, reviews: reviewsLeft })}</p> : null}
          <ul className="flex flex-col gap-1">
            {today.items.map((item) => (
              <li key={item.kind} className="flex flex-wrap items-center gap-2">
                <span aria-hidden className={cn('size-2 rounded-full', item.total && item.done >= item.total ? 'bg-accent' : 'bg-border')} />
                {item.kind === 'REVIEWS'
                  ? t('item.REVIEWS', { done: item.done, total: item.total })
                  : item.kind === 'PLAN_TASK'
                    ? t('item.PLAN_TASK', { title: item.title ?? '', done: item.done, total: item.total })
                    : item.kind === 'WEAK_TOPIC'
                      ? t('item.WEAK_TOPIC', { title: item.title ?? item.topicKey ?? '' })
                      : item.kind}
                {item.kind === 'REVIEWS' && item.done < item.total ? (
                  <Link href="/review" className="font-medium text-accent hover:underline">
                    {t('reviewNow')}
                  </Link>
                ) : null}
                {item.kind === 'PLAN_TASK' && item.done < item.total ? (
                  <Link href="/exams" className="font-medium text-accent hover:underline">
                    {t('examsLink')}
                  </Link>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}

function Week({ r }: { r: R }) {
  const t = useTranslations('rhythm')
  const format = useFormatter()
  return (
    <section aria-labelledby="rhythm-week" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <div className="flex items-center justify-between gap-2">
        <h2 id="rhythm-week" className="text-lg font-bold">
          {t('week')}
        </h2>
        {r.met ? <span className="rounded-full bg-accent-soft px-3 py-1 text-xs font-semibold text-accent">{t('met')}</span> : null}
      </div>
      <ol className="grid grid-cols-7 gap-1">
        {r.week.map((d) => {
          const date = new Date(`${d.day}T12:00:00Z`)
          const name = format.dateTime(date, { weekday: 'long', timeZone: 'UTC' })
          const status = d.status === 'AHEAD' && !d.planned ? t('status.REST') : t(`status.${d.status}`)
          return (
            <li key={d.day} aria-label={t('dayLabel', { day: name, status: d.planned && d.status !== 'MISSED' ? `${status}, ${t('plannedTag')}` : status })} className="flex flex-col items-center gap-1.5">
              <span aria-hidden className={cn('text-xs', d.status === 'TODAY' || (d.status === 'COUNTED' && d.day === r.today.day) ? 'font-bold text-accent' : 'text-muted')}>
                {format.dateTime(date, { weekday: 'narrow', timeZone: 'UTC' })}
              </span>
              <span
                aria-hidden
                className={cn(
                  'flex size-9 items-center justify-center rounded-full text-sm',
                  d.counted && 'bg-accent text-accent-fg',
                  !d.counted && d.planned && d.status !== 'PAUSED' && 'border-2 border-accent/60',
                  !d.counted && d.status === 'MISSED' && 'border-dashed',
                  !d.counted && !d.planned && 'bg-surface-2',
                  d.status === 'PAUSED' && 'bg-surface-2 text-muted',
                  d.status === 'TODAY' && 'ring-2 ring-accent ring-offset-2 ring-offset-surface',
                )}
              >
                {d.counted ? '✓' : d.status === 'PAUSED' ? '‖' : ''}
              </span>
            </li>
          )
        })}
      </ol>
      <p className="text-sm text-muted">{t('weekSummary', { counted: r.countedDays, target: r.target })}</p>
    </section>
  )
}

function Counters({ r }: { r: R }) {
  const t = useTranslations('rhythm')
  const items = [
    [t('weeksThisTerm'), r.weeksThisTerm],
    [t('weeksAllTime'), r.weeksAllTime],
    [t('daysAllTime'), r.countedDaysAllTime],
  ] as const
  return (
    <section aria-label={t('counters')} className="grid grid-cols-3 gap-2">
      {items.map(([label, n]) => (
        <div key={label} className="flex flex-col gap-1 rounded-2xl border border-border bg-surface p-3">
          <span className="text-2xl font-extrabold">{n}</span>
          <span className="text-xs text-muted">{label}</span>
        </div>
      ))}
    </section>
  )
}

function Plan({ r }: { r: R }) {
  const t = useTranslations('rhythm')
  const format = useFormatter()
  const [days, setDays] = useState<number[]>(r.plannedDays)
  const [problem, setProblem] = useState<string | null>(null)
  const [saved, setSaved] = useState(false)
  const [save, saving] = useMutation(SetRhythmPlanDocument, { refetchQueries: [RhythmDocument], awaitRefetchQueries: true })
  const changed = days.join() !== r.plannedDays.join()
  const valid = days.length >= 3 && days.length <= 6
  // 5 Jan 2026 is a Monday: its week gives the weekday names.
  const name = (weekday: number) => format.dateTime(new Date(Date.UTC(2026, 0, 4 + weekday, 12)), { weekday: 'long', timeZone: 'UTC' })
  return (
    <section aria-labelledby="rhythm-plan" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <h2 id="rhythm-plan" className="text-lg font-bold">
        {t('plan')}
      </h2>
      <p className="text-sm text-muted">{t('planHelp')}</p>
      <div className="flex flex-wrap gap-2">
        {WEEKDAYS.map((d) => {
          const on = days.includes(d)
          return (
            <button
              key={d}
              type="button"
              aria-pressed={on}
              onClick={() => {
                setSaved(false)
                setDays((prev) => (on ? prev.filter((x) => x !== d) : [...prev, d].sort((a, b) => a - b)))
              }}
              className={cn('h-10 rounded-full border px-4 text-sm font-medium', on ? 'border-accent bg-accent text-accent-fg' : 'border-border bg-surface hover:bg-surface-2')}
            >
              {name(d)}
            </button>
          )
        })}
      </div>
      <div className="flex flex-wrap items-center gap-3">
        <Button
          size="sm"
          disabled={!changed || !valid || saving.loading}
          onClick={async () => {
            setProblem(null)
            const res = await save({ variables: { input: { plannedDays: days } } })
            const message = res.data?.setRhythmPlan.userErrors[0]?.message
            if (message) setProblem(message)
            else setSaved(true)
          }}
        >
          {t('savePlan')}
        </Button>
        {saved && !changed ? (
          <p role="status" className="text-sm text-muted">
            {t('planSaved', { target: r.target })}
          </p>
        ) : null}
      </div>
      {problem ? <Alert tone="error">{problem}</Alert> : null}
    </section>
  )
}

function Pauses({ r }: { r: R }) {
  const t = useTranslations('rhythm')
  const format = useFormatter()
  const [open, setOpen] = useState(false)
  const [from, setFrom] = useState(r.today.day)
  const [to, setTo] = useState(addDays(r.today.day, 2))
  const [reason, setReason] = useState<RhythmPauseReason>('EXAMS')
  const [problem, setProblem] = useState<string | null>(null)
  const [pause, pausing] = useMutation(PauseRhythmDocument, { refetchQueries: [RhythmDocument], awaitRefetchQueries: true })
  const [end, ending] = useMutation(EndRhythmPauseDocument, { refetchQueries: [RhythmDocument], awaitRefetchQueries: true })
  const show = (day: string) => format.dateTime(new Date(`${day}T12:00:00Z`), { day: 'numeric', month: 'short', timeZone: 'UTC' })
  return (
    <section aria-labelledby="rhythm-pauses" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <h2 id="rhythm-pauses" className="text-lg font-bold">
        {t('pauses')}
      </h2>
      <p className="text-sm text-muted">{t('pauseHelp', { left: r.pauseDaysLeft })}</p>
      {r.pauses.length ? (
        <ul className="flex flex-col gap-2">
          {r.pauses.map((p) => (
            <li key={p.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-surface-2 px-3 py-2 text-sm">
              <span className="flex flex-wrap items-center gap-2">
                <span>{t('pauseRange', { reason: t(`reasons.${p.reason}`), from: show(p.from), to: show(p.to) })}</span>
                {p.active ? <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-medium text-accent">{t('pausedNow')}</span> : null}
              </span>
              <Button variant="ghost" size="sm" disabled={ending.loading} onClick={() => void end({ variables: { input: { id: p.id } } })}>
                {p.active && p.from < r.today.day ? t('endPause') : t('dropPause')}
              </Button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted">{t('noPauses')}</p>
      )}
      {open ? (
        <form
          className="flex flex-col gap-3"
          onSubmit={async (e) => {
            e.preventDefault()
            setProblem(null)
            const res = await pause({ variables: { input: { from, to, reason } } })
            const message = res.data?.pauseRhythm.userErrors[0]?.message
            if (message) setProblem(message)
            else setOpen(false)
          }}
        >
          <div className="flex flex-wrap gap-3">
            <label className="flex flex-col gap-1 text-sm">
              {t('from')}
              <input type="date" required min={r.today.day} value={from} onChange={(e) => setFrom(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              {t('to')}
              <input type="date" required min={from} value={to} onChange={(e) => setTo(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              {t('reason')}
              <select value={reason} onChange={(e) => setReason(e.target.value as RhythmPauseReason)} className="h-11 rounded-xl border border-border bg-surface px-3">
                {REASONS.map((x) => (
                  <option key={x} value={x}>
                    {t(`reasons.${x}`)}
                  </option>
                ))}
              </select>
            </label>
          </div>
          {problem ? <Alert tone="error">{problem}</Alert> : null}
          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={pausing.loading}>
              {t('startPause')}
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
              {t('cancel')}
            </Button>
          </div>
        </form>
      ) : (
        <Button variant="secondary" size="sm" className="self-start" disabled={r.pauseDaysLeft === 0} onClick={() => setOpen(true)}>
          {t('pause')}
        </Button>
      )}
    </section>
  )
}
