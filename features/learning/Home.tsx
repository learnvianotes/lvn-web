'use client'

import { useQuery } from '@apollo/client/react'
import { ArrowRight, BookOpen, CalendarCheck, CalendarClock, GraduationCap, Library, ListChecks, Play, RotateCcw, TrendingUp, Users } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { ExamsDocument, MyClassroomsDocument, MyGroupsDocument, RecommendationsDocument, RhythmDocument, ViewerDocument, type RecommendationKind, type RecommendationsQuery } from '@/graphql/generated/graphql'
import { Today, Week } from './Rhythm'

type Rec = RecommendationsQuery['recommendations'][number]

/** A picture for each kind of recommendation (board A's illustrated cards): a gradient and the kind's sign. */
const ART: Record<RecommendationKind, { icon: typeof BookOpen; from: string; to: string }> = {
  EXAM_TOPIC: { icon: CalendarClock, from: '#EA580C', to: '#DB2777' },
  REVISE_TOPIC: { icon: RotateCcw, from: '#4F46E5', to: '#7C3AED' },
  CONTINUE_NOTE: { icon: BookOpen, from: '#0284C7', to: '#4F46E5' },
  QUIZ_ON_TOPIC: { icon: ListChecks, from: '#059669', to: '#0284C7' },
  POPULAR_NOTE: { icon: TrendingUp, from: '#7C3AED', to: '#DB2777' },
  RESOURCE: { icon: Library, from: '#0D9488', to: '#4F46E5' },
}
const coreName = (key: string) => key.replace(/^core:/, '').replace('/', ' / ').replace(/-/g, ' ')
const hrefOf = (r: Rec) => (r.note ? `/notes/${r.note.id}` : r.resource ? `/resources/${r.resource.id}` : r.topic ? `/search?topic=${r.topic.id}&topicTitle=${encodeURIComponent(r.topicTitle ?? '')}` : `/search?q=${encodeURIComponent(r.topicTitle ?? coreName(r.topicKey ?? ''))}`)
const partOfDay = (hour: number) => (hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening')

/**
 * Home as board A draws it (lvn-backend ADR-0076, on P6h): the greeting, the note to continue, the next exam and the
 * week's goal as cards, today's ring, recommendations as pictures, and the person's rooms (groups and classes).
 */
export function Home() {
  const t = useTranslations('homeDashboard')
  const viewer = useQuery(ViewerDocument).data?.viewer
  const rhythm = useQuery(RhythmDocument, { fetchPolicy: 'cache-and-network' }).data?.rhythm
  const exams = useQuery(ExamsDocument, { fetchPolicy: 'cache-and-network' }).data?.exams
  const recs = useQuery(RecommendationsDocument, { variables: { limit: 8 }, fetchPolicy: 'cache-and-network' }).data?.recommendations
  const groups = useQuery(MyGroupsDocument, { fetchPolicy: 'cache-and-network' }).data?.myGroups
  const classes = useQuery(MyClassroomsDocument, { fetchPolicy: 'cache-and-network' }).data?.myClassrooms
  const firstName = viewer?.displayName.trim().split(/\s+/)[0]
  const next = exams?.find((e) => !e.past)
  const continueNote = recs?.find((r) => r.kind === 'CONTINUE_NOTE' && r.note)
  const pictures = (recs ?? []).filter((r) => r !== continueNote).slice(0, 4)
  const rooms = [...(groups ?? []).map((g) => ({ id: g.id, name: g.name, href: `/groups/${g.id}`, members: g.memberCount, kind: 'group' as const })), ...(classes ?? []).map((c) => ({ id: c.id, name: c.name, href: `/classes/${c.id}`, members: c.memberCount, kind: 'class' as const }))].slice(0, 4)
  const when = partOfDay(new Date().getHours())
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div className="flex flex-col gap-1">
          <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{firstName ? t(`greeting.${when}`, { name: firstName }) : t('greetingAnon')}</h1>
          <p className="text-sm text-muted">{t('lead')}</p>
        </div>
        {rhythm ? (
          <Link href="/rhythm" className="flex items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-2.5 hover:border-accent">
            <span aria-hidden className="text-2xl">🔥</span>
            <span className="flex flex-col leading-tight">
              <span className="text-lg font-extrabold">{rhythm.countedDaysAllTime}</span>
              <span className="text-xs text-muted">{t('daysLearned')}</span>
            </span>
          </Link>
        ) : null}
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <section aria-labelledby="continue" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
          <h2 id="continue" className="flex items-center gap-2 text-sm font-semibold text-muted">
            <BookOpen aria-hidden className="size-4 text-accent" />
            {t('continue')}
          </h2>
          {continueNote?.note ? (
            <Link href={`/notes/${continueNote.note.id}`} className="flex items-center gap-3 hover:text-accent">
              <span className="flex min-w-0 flex-1 flex-col">
                <span className="truncate font-bold">{continueNote.noteTitle || t('untitled')}</span>
                <span className="text-xs text-muted">{continueNote.reason}</span>
              </span>
              <span aria-hidden className="grid size-10 shrink-0 place-items-center rounded-full bg-accent text-accent-fg">
                <Play className="size-4" />
              </span>
            </Link>
          ) : (
            <Link href="/notes" className="text-sm text-muted hover:text-accent">
              {t('nothingToContinue')}
            </Link>
          )}
        </section>
        <section aria-labelledby="next-exam" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
          <h2 id="next-exam" className="flex items-center gap-2 text-sm font-semibold text-muted">
            <CalendarCheck aria-hidden className="size-4 text-orange-500" />
            {t('nextExam')}
          </h2>
          {next ? (
            <div className="flex flex-col gap-2">
              <span className="truncate font-bold">{next.name}</span>
              <span className="text-sm font-semibold text-red-600 dark:text-red-400">{t('inDays', { count: next.daysLeft ?? 0 })}</span>
              <Link href={`/exams/${next.id}`} className="inline-flex w-fit items-center gap-1 rounded-full border border-border px-3 py-1 text-sm font-semibold text-accent hover:border-accent">
                {t('viewPlan')}
              </Link>
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              <p className="text-sm text-muted">{t('noExam')}</p>
              <Link href="/exams" className="inline-flex w-fit items-center gap-1 rounded-full border border-border px-3 py-1 text-sm font-semibold text-accent hover:border-accent">
                {t('addExam')}
              </Link>
            </div>
          )}
        </section>
        <section aria-labelledby="weekly-goal" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
          <h2 id="weekly-goal" className="flex items-center gap-2 text-sm font-semibold text-muted">
            <span aria-hidden className="size-2 rounded-full bg-emerald-500" />
            {t('weeklyGoal')}
          </h2>
          {rhythm ? (
            <div className="flex items-center gap-4">
              <GoalRing done={rhythm.countedDays} target={rhythm.target} />
              <span className="flex flex-col">
                <span className="text-xl font-extrabold">{t('ofDays', { done: rhythm.countedDays, target: rhythm.target })}</span>
                <span className="text-xs text-emerald-600 dark:text-emerald-400">{rhythm.met ? t('goalMet') : t('keepGoing')}</span>
              </span>
            </div>
          ) : null}
        </section>
      </div>

      {rhythm ? (
        // Today and This week are regions of their own (Rhythm's): this is only their column.
        <div className="flex flex-col gap-4">
          <Today r={rhythm} />
          <Week r={rhythm} />
          <Link href="/rhythm" className="-mt-2 inline-flex items-center gap-1 self-end text-sm font-semibold text-accent hover:underline">
            {t('openRhythm')} <ArrowRight aria-hidden className="size-4" />
          </Link>
        </div>
      ) : null}

      <section aria-labelledby="recommended" className="flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <h2 id="recommended" className="text-lg font-bold">
            {t('recommended')}
          </h2>
          <Link href="/rhythm" className="text-sm font-semibold text-accent hover:underline">
            {t('seeAll')}
          </Link>
        </div>
        {recs && !pictures.length ? <p className="rounded-2xl border border-dashed border-border px-4 py-6 text-center text-sm text-muted">{t('noRecommendations')}</p> : null}
        <ul className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {pictures.map((r) => {
            const art = ART[r.kind]
            const Icon = art.icon
            const title = r.resource?.title || r.noteTitle || r.topicTitle || (r.topicKey ? coreName(r.topicKey) : t('untitled'))
            return (
              <li key={`${r.kind}:${r.resource?.id ?? r.note?.id ?? r.topicKey}`}>
                <Link href={hrefOf(r)} className="flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-surface hover:border-accent">
                  <span aria-hidden className="grid h-24 place-items-center" style={{ backgroundImage: `linear-gradient(135deg, ${art.from}, ${art.to})` }}>
                    <Icon className="size-9 text-white" />
                  </span>
                  <span className="flex flex-1 flex-col gap-1 p-3">
                    <span className="line-clamp-2 text-sm font-semibold">{title}</span>
                    <span className="text-xs text-accent">{r.reason}</span>
                  </span>
                </Link>
              </li>
            )
          })}
        </ul>
      </section>

      <section aria-labelledby="rooms" className="flex flex-col gap-3">
        <div className="flex items-baseline justify-between">
          <h2 id="rooms" className="text-lg font-bold">
            {t('rooms')}
          </h2>
          {/* Groups when the person has any; a person only in classes sees their classes. */}
          <Link href={!groups?.length && classes?.length ? '/classes' : '/groups'} className="text-sm font-semibold text-accent hover:underline">
            {t('seeAll')}
          </Link>
        </div>
        {groups && classes && !rooms.length ? (
          <p className="rounded-2xl border border-dashed border-border px-4 py-6 text-center text-sm text-muted">
            {t('noRooms')}{' '}
            <Link href="/groups" className="font-semibold text-accent hover:underline">
              {t('findGroups')}
            </Link>
          </p>
        ) : null}
        <ul className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {rooms.map((room) => (
            <li key={`${room.kind}:${room.id}`}>
              <Link href={room.href} className="flex h-full items-center gap-3 rounded-2xl border border-border bg-surface p-3 hover:border-accent">
                <span aria-hidden className="grid size-10 shrink-0 place-items-center rounded-xl bg-accent-soft text-accent">
                  {room.kind === 'group' ? <Users className="size-5" /> : <GraduationCap className="size-5" />}
                </span>
                <span className="flex min-w-0 flex-col">
                  <span className="truncate text-sm font-semibold">{room.name}</span>
                  <span className="text-xs text-muted">{t('members', { count: room.members })}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

/** This week's days against the goal, as a ring. */
function GoalRing({ done, target }: { done: number; target: number }) {
  const r = 20
  const c = 2 * Math.PI * r
  const share = target ? Math.min(done / target, 1) : 0
  return (
    <svg viewBox="0 0 48 48" className="size-14 shrink-0 -rotate-90" aria-hidden>
      <circle cx="24" cy="24" r={r} fill="none" className="stroke-surface-2" strokeWidth="6" />
      <circle cx="24" cy="24" r={r} fill="none" stroke="#16A34A" strokeWidth="6" strokeLinecap="round" strokeDasharray={`${c * share} ${c}`} />
    </svg>
  )
}
