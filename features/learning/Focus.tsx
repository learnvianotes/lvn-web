'use client'

import { useLazyQuery, useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { useLive } from '@/features/notifications/live'
import {
  AnswerRhythmBuddyDocument,
  EndFocusSessionDocument,
  ExamTopicOptionsDocument,
  FocusSessionDocument,
  InviteRhythmBuddyDocument,
  RemoveRhythmBuddyDocument,
  RhythmBuddiesDocument,
  RhythmDocument,
  SetRhythmSharingDocument,
  StartFocusSessionDocument,
  type FocusSessionFieldsFragment,
} from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

const clock = (seconds: number) => `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`

/** Where a session is now: working, resting, or done, and the seconds left of that part. */
export function phaseOf(s: Pick<FocusSessionFieldsFragment, 'startedAt' | 'plannedMinutes' | 'breakMinutes'>, now: number): { phase: 'FOCUS' | 'BREAK' | 'DONE'; left: number } {
  const gone = Math.max(Math.floor((now - Date.parse(s.startedAt)) / 1000), 0)
  const work = s.plannedMinutes * 60
  if (gone < work) return { phase: 'FOCUS', left: work - gone }
  const rest = s.breakMinutes * 60
  if (gone < work + rest) return { phase: 'BREAK', left: work + rest - gone }
  return { phase: 'DONE', left: 0 }
}

/**
 * Focus mode (lvn-backend ADR-0072): Pomodoro work and rest, on a topic if the person likes, with a Meet link their
 * buddies can join. The server counts the time between start and end, at most the plan; the timer here only shows it.
 */
export function FocusMode() {
  const t = useTranslations('focus')
  const { data } = useQuery(FocusSessionDocument, { fetchPolicy: 'cache-and-network' })
  const refresh = { refetchQueries: [FocusSessionDocument, RhythmDocument], awaitRefetchQueries: true }
  const [start, starting] = useMutation(StartFocusSessionDocument, refresh)
  const [end, ending] = useMutation(EndFocusSessionDocument, refresh)
  const [minutes, setMinutes] = useState(25)
  const [breakMinutes, setBreakMinutes] = useState(5)
  const [meetUrl, setMeetUrl] = useState('')
  const [topic, setTopic] = useState<{ key: string; title: string } | null>(null)
  const [problem, setProblem] = useState<string | null>(null)
  const [counted, setCounted] = useState<number | null>(null)
  const [now, setNow] = useState(() => Date.now())
  const session = data?.focusSession
  useEffect(() => {
    if (!session) return
    const timer = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(timer)
  }, [session])
  const phase = session ? phaseOf(session, now) : null

  return (
    <section aria-labelledby="focus-mode" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <h2 id="focus-mode" className="text-lg font-bold">
        {t('title')}
      </h2>
      {session && phase ? (
        <div className="flex flex-col gap-3">
          <p role="timer" aria-live="off" className="text-4xl font-extrabold tabular-nums">
            {clock(phase.left)}
          </p>
          <p className="text-sm text-muted">{phase.phase === 'FOCUS' ? t('focusing', { minutes: session.plannedMinutes }) : phase.phase === 'BREAK' ? t('resting') : t('done')}</p>
          {session.meetUrl ? (
            <a href={session.meetUrl} target="_blank" rel="noreferrer" className="text-sm font-medium text-accent hover:underline">
              {t('openMeet')}
            </a>
          ) : null}
          <Button
            className="self-start"
            disabled={ending.loading}
            onClick={async () => {
              const res = await end({ variables: { input: { id: session.id } } })
              setCounted(res.data?.endFocusSession.session?.focusedSeconds ?? null)
            }}
          >
            {t('end')}
          </Button>
        </div>
      ) : (
        <form
          className="flex flex-col gap-3"
          onSubmit={async (e) => {
            e.preventDefault()
            setProblem(null)
            setCounted(null)
            const res = await start({ variables: { input: { minutes, breakMinutes, topicKey: topic?.key ?? null, meetUrl: meetUrl.trim() || null } } })
            const message = res.data?.startFocusSession.userErrors[0]?.message
            if (message) setProblem(message)
          }}
        >
          <p className="text-sm text-muted">{t('lead')}</p>
          {counted !== null ? (
            <p role="status" className="text-sm font-medium text-accent">
              {t('counted', { minutes: Math.round(counted / 60) })}
            </p>
          ) : null}
          <div className="flex flex-wrap gap-3">
            <label className="flex flex-col gap-1 text-sm">
              {t('minutes')}
              <select value={minutes} onChange={(e) => setMinutes(Number(e.target.value))} className="h-11 rounded-xl border border-border bg-surface px-3">
                {[15, 25, 45, 60].map((m) => (
                  <option key={m} value={m}>
                    {t('minutesOption', { minutes: m })}
                  </option>
                ))}
              </select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              {t('breakMinutes')}
              <select value={breakMinutes} onChange={(e) => setBreakMinutes(Number(e.target.value))} className="h-11 rounded-xl border border-border bg-surface px-3">
                {[0, 5, 10, 15].map((m) => (
                  <option key={m} value={m}>
                    {t('minutesOption', { minutes: m })}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <TopicChoice value={topic} onChange={setTopic} />
          <label className="flex flex-col gap-1 text-sm">
            {t('meet')}
            <input type="url" value={meetUrl} placeholder="https://meet.google.com/abc-defg-hij" onChange={(e) => setMeetUrl(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
          </label>
          {problem ? <Alert tone="error">{problem}</Alert> : null}
          <Button type="submit" className="self-start" disabled={starting.loading}>
            {t('start')}
          </Button>
        </form>
      )}
    </section>
  )
}

function TopicChoice({ value, onChange }: { value: { key: string; title: string } | null; onChange: (v: { key: string; title: string } | null) => void }) {
  const t = useTranslations('focus')
  const [query, setQuery] = useState('')
  const [find, found] = useLazyQuery(ExamTopicOptionsDocument)
  useEffect(() => {
    if (query.trim().length < 2) return
    const timer = setTimeout(() => void find({ variables: { query: query.trim() } }), 250)
    return () => clearTimeout(timer)
  }, [query, find])
  if (value) {
    return (
      <p className="flex items-center gap-2 text-sm">
        {t('onTopic', { title: value.title })}
        <button type="button" className="text-accent hover:underline" onClick={() => onChange(null)}>
          {t('noTopic')}
        </button>
      </p>
    )
  }
  const options = query.trim().length >= 2 ? (found.data?.examTopicOptions ?? []) : []
  return (
    <div className="flex flex-col gap-1">
      <label className="flex flex-col gap-1 text-sm">
        {t('topic')}
        <input type="search" value={query} placeholder={t('topicPlaceholder')} onChange={(e) => setQuery(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
      </label>
      {options.slice(0, 6).map((o) => (
        <button key={o.id} type="button" aria-label={t('pickTopic', { title: o.title })} className="flex items-baseline justify-between rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2" onClick={() => (onChange({ key: o.key, title: o.title }), setQuery(''))}>
          <span>{o.title}</span>
          <span className="text-xs text-muted">{o.subjectTitle}</span>
        </button>
      ))}
    </div>
  )
}

/**
 * Rhythm buddies (lvn-backend ADR-0072): up to five, by mutual consent; each sees whether the other is studying now
 * (and their Meet link then) and their week. The list follows the live channel.
 */
export function Buddies() {
  const t = useTranslations('buddies')
  const { data, refetch } = useQuery(RhythmBuddiesDocument, { fetchPolicy: 'cache-and-network' })
  useLive((signal) => {
    if (signal.kind === 'BUDDY_PRESENCE' || signal.kind === 'RECONNECTED') void refetch().catch(() => undefined)
  })
  const refresh = { refetchQueries: [RhythmBuddiesDocument], awaitRefetchQueries: true }
  const [invite, inviting] = useMutation(InviteRhythmBuddyDocument, refresh)
  const [answer] = useMutation(AnswerRhythmBuddyDocument, refresh)
  const [remove] = useMutation(RemoveRhythmBuddyDocument, refresh)
  const [handle, setHandle] = useState('')
  const [problem, setProblem] = useState<string | null>(null)
  const list = data?.rhythmBuddies
  if (!list) return null
  return (
    <section aria-labelledby="rhythm-buddies" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <h2 id="rhythm-buddies" className="text-lg font-bold">
        {t('title')}
      </h2>
      <p className="text-sm text-muted">{t('lead')}</p>
      {list.invites.map((i) => (
        <div key={i.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-accent-soft px-3 py-2 text-sm">
          <span>{t('invited', { name: i.user.displayName })}</span>
          <span className="flex gap-2">
            <Button size="sm" onClick={() => void answer({ variables: { input: { id: i.id, accept: true } } })}>
              {t('accept')}
            </Button>
            <Button size="sm" variant="ghost" onClick={() => void answer({ variables: { input: { id: i.id, accept: false } } })}>
              {t('decline')}
            </Button>
          </span>
        </div>
      ))}
      {!list.buddies.length ? <p className="text-sm text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-2">
        {list.buddies.map((b) => (
          <li key={b.id} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-surface-2 px-3 py-2 text-sm">
            <span className="flex flex-col">
              <span className="font-medium">
                {b.user.displayName}
                {b.studyingNow ? <span className="ml-2 rounded-full bg-accent px-2 py-0.5 text-xs font-semibold text-accent-fg">{t('studyingNow')}</span> : null}
              </span>
              <span className="text-muted">
                {b.studyingNow && b.topicTitle ? `${t('onTopic', { title: b.topicTitle })} · ` : ''}
                {t('week', { counted: b.countedDays, target: b.target })}
              </span>
            </span>
            <span className="flex items-center gap-2">
              {b.studyingNow && b.meetUrl ? (
                <a href={b.meetUrl} target="_blank" rel="noreferrer" className="font-medium text-accent hover:underline">
                  {t('join')}
                </a>
              ) : null}
              <button type="button" aria-label={t('remove', { name: b.user.displayName })} className={cn('rounded-full px-2 py-1 text-muted hover:bg-surface hover:text-fg')} onClick={() => void remove({ variables: { input: { id: b.id } } })}>
                ×
              </button>
            </span>
          </li>
        ))}
      </ul>
      {list.sent.map((s) => (
        <p key={s.id} className="flex items-center justify-between text-sm text-muted">
          {t('waiting', { name: s.user.displayName })}
          <button type="button" className="text-accent hover:underline" onClick={() => void remove({ variables: { input: { id: s.id } } })}>
            {t('takeBack')}
          </button>
        </p>
      ))}
      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={async (e) => {
          e.preventDefault()
          setProblem(null)
          const res = await invite({ variables: { input: { handle: handle.trim() } } })
          const message = res.data?.inviteRhythmBuddy.userErrors[0]?.message
          if (message) setProblem(message)
          else setHandle('')
        }}
      >
        <label className="flex flex-1 flex-col gap-1 text-sm">
          {t('handle')}
          <input required value={handle} placeholder="@handle" onChange={(e) => setHandle(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
        </label>
        <Button type="submit" size="sm" disabled={inviting.loading}>
          {t('invite')}
        </Button>
      </form>
      {problem ? <Alert tone="error">{problem}</Alert> : null}
    </section>
  )
}

/** Whether the person's name and counted days show on their classes' Rhythm ring; off until they say so. */
export function ShareRhythm({ shared }: { shared: boolean }) {
  const t = useTranslations('buddies')
  const [set, setting] = useMutation(SetRhythmSharingDocument, { refetchQueries: [RhythmDocument] })
  return (
    <label className="flex items-start gap-3 text-sm">
      <input type="checkbox" className="mt-1 size-4" checked={shared} disabled={setting.loading} onChange={(e) => void set({ variables: { input: { share: e.target.checked } } })} />
      <span className="flex flex-col">
        <span className="font-medium">{t('share')}</span>
        <span className="text-muted">{t('shareHelp')}</span>
      </span>
    </label>
  )
}
