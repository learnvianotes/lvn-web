'use client'

import { useLazyQuery, useMutation, useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useFormatter, useTranslations } from 'next-intl'
import { useEffect, useId, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { CreateExamDocument, DeleteExamDocument, ExamDocument, ExamsDocument, ExamTopicOptionsDocument, UpdateExamDocument, WeakTopicsDocument, type ExamFieldsFragment } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { EXAM_LIMITS } from '@/lib/contracts/validation'

type Exam = ExamFieldsFragment
type PickedTopic = { id: string; title: string }

const pct = (v: number) => Math.round(v * 100)
const coreName = (key: string) => key.replace(/^core:/, '').replace('/', ' / ').replace(/-/g, ' ')
const localToday = () => {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

/**
 * Exams (lvn-backend ADR-0070): each exam with its Readiness against the target line, today's revision, and the plan;
 * adding one with its topics; the weak topics to revise first. A task left is never framed as a loss.
 */
export function Exams() {
  const t = useTranslations('exams')
  const { data, loading, error } = useQuery(ExamsDocument, { fetchPolicy: 'cache-and-network' })
  const [adding, setAdding] = useState(false)
  const exams = data?.exams
  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        <p className="text-sm text-muted">{t('lead')}</p>
      </header>
      {adding ? (
        <section aria-label={t('add')} className="rounded-2xl border border-border bg-surface p-5">
          <ExamForm onDone={() => setAdding(false)} />
        </section>
      ) : (
        <Button className="self-start" onClick={() => setAdding(true)}>
          {t('add')}
        </Button>
      )}
      {error && !exams ? <Alert tone="error">{t('failed')}</Alert> : null}
      {!exams && loading ? <p className="text-muted">{t('loading')}</p> : null}
      {exams && !exams.length ? <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('none')}</p> : null}
      <ul className="flex flex-col gap-3">
        {exams?.map((e) => (
          <li key={e.id}>
            <ExamCard exam={e} />
          </li>
        ))}
      </ul>
      <WeakTopics />
    </div>
  )
}

/** Readiness as a bar, with a mark where the target line is today. */
export function ReadinessBar({ readiness, targetToday }: { readiness: number; targetToday: number }) {
  const t = useTranslations('exams')
  return (
    <div role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={readiness} aria-label={t('readinessLabel', { value: readiness, target: targetToday })} className="relative h-2.5 w-full rounded-full bg-surface-2">
      <div className="h-full rounded-full bg-accent transition-[width] duration-700" style={{ width: `${readiness}%` }} />
      <div aria-hidden className="absolute -top-1 h-4.5 w-0.5 rounded bg-fg/60" style={{ left: `calc(${targetToday}% - 1px)` }} />
    </div>
  )
}

export function ExamCard({ exam }: { exam: Exam }) {
  const t = useTranslations('exams')
  const format = useFormatter()
  const today = exam.tasks.filter((x) => x.today)
  const behind = exam.targetToday - exam.readiness
  return (
    <article aria-label={exam.name} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-lg font-bold">
          <Link href={`/exams/${exam.id}`} className="hover:underline">
            {exam.name}
          </Link>
        </h2>
        <span className="text-sm text-muted">
          {format.dateTime(new Date(`${exam.date}T12:00:00Z`), { day: 'numeric', month: 'short', timeZone: 'UTC' })} · {exam.past ? t('past') : t('daysLeft', { days: exam.daysLeft })}
        </span>
      </div>
      <div className="flex items-center gap-3">
        <span className="w-32 shrink-0 text-sm font-semibold">{t('readiness', { value: exam.readiness })}</span>
        <ReadinessBar readiness={exam.readiness} targetToday={exam.targetToday} />
      </div>
      {!exam.past ? <p className="text-sm text-muted">{behind > 0 ? t('behind', { points: behind }) : t('onTrack')}</p> : null}
      {today.length ? (
        <p className={cn('text-sm', today.every((x) => x.done) ? 'text-accent' : '')}>
          {today.every((x) => x.done) ? t('todayDone') : t('todayTask', { topics: today.flatMap((x) => x.topics.map((tp) => tp.title)).join(', ') })}
        </p>
      ) : null}
    </article>
  )
}

/** One exam: Readiness, its topics' mastery, the plan; edit and delete. */
export function ExamDetail({ id }: { id: string }) {
  const t = useTranslations('exams')
  const format = useFormatter()
  const router = useRouter()
  const { data, loading } = useQuery(ExamDocument, { variables: { id }, fetchPolicy: 'cache-and-network' })
  const [remove, removing] = useMutation(DeleteExamDocument, { refetchQueries: [ExamsDocument] })
  const [editing, setEditing] = useState(false)
  const exam = data?.exam
  if (!exam) {
    return (
      <div className="flex flex-col gap-4">
        <Link href="/exams" className="text-sm text-accent hover:underline">
          ← {t('back')}
        </Link>
        {loading ? <p className="text-muted">{t('loading')}</p> : <Alert tone="error">{t('failed')}</Alert>}
      </div>
    )
  }
  const dayName = (day: string) => format.dateTime(new Date(`${day}T12:00:00Z`), { weekday: 'short', day: 'numeric', month: 'short', timeZone: 'UTC' })
  return (
    <div className="flex flex-col gap-6">
      <Link href="/exams" className="text-sm text-accent hover:underline">
        ← {t('back')}
      </Link>
      <header className="flex flex-col gap-3">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <h1 className="text-2xl font-extrabold tracking-tight">{exam.name}</h1>
          <span className="text-sm text-muted">
            {format.dateTime(new Date(`${exam.date}T12:00:00Z`), { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'UTC' })} · {exam.past ? t('past') : t('daysLeft', { days: exam.daysLeft })}
          </span>
        </div>
        <div className="flex items-center gap-3">
          <span className="w-32 shrink-0 text-sm font-semibold">{t('readiness', { value: exam.readiness })}</span>
          <ReadinessBar readiness={exam.readiness} targetToday={exam.targetToday} />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button variant="secondary" size="sm" onClick={() => setEditing((v) => !v)}>
            {t('edit')}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            disabled={removing.loading}
            onClick={async () => {
              if (!window.confirm(t('confirmDelete', { name: exam.name }))) return
              await remove({ variables: { input: { id: exam.id } } })
              router.push('/exams')
            }}
          >
            {t('delete')}
          </Button>
        </div>
      </header>
      {editing ? (
        <section aria-label={t('edit')} className="rounded-2xl border border-border bg-surface p-5">
          <ExamForm exam={exam} onDone={() => setEditing(false)} />
        </section>
      ) : null}
      <section aria-labelledby="exam-topics" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
        <h2 id="exam-topics" className="text-lg font-bold">
          {t('mastery')}
        </h2>
        <p className="text-sm text-muted">{t('masteryHelp')}</p>
        <ul className="flex flex-col gap-3">
          {exam.topics.map((tp) => (
            <li key={tp.key} className="flex flex-col gap-1">
              <div className="flex flex-wrap items-baseline justify-between gap-2 text-sm">
                <span className="font-medium">{tp.title}</span>
                <span className="text-muted">
                  {tp.recall === null && tp.accuracy === null
                    ? t('noData')
                    : [tp.recall !== null ? t('recall', { value: pct(tp.recall) }) : null, tp.accuracy !== null ? t('accuracy', { value: pct(tp.accuracy) }) : null].filter(Boolean).join(' · ')}
                </span>
              </div>
              <div aria-hidden className="h-1.5 rounded-full bg-surface-2">
                <div className="h-full rounded-full bg-accent/70" style={{ width: `${pct(tp.mastery)}%` }} />
              </div>
            </li>
          ))}
        </ul>
      </section>
      <section aria-labelledby="exam-plan" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
        <h2 id="exam-plan" className="text-lg font-bold">
          {t('plan')}
        </h2>
        <p className="text-sm text-muted">{t('planHelp')}</p>
        {!exam.tasks.length ? <p className="text-sm text-muted">{t('noPlan')}</p> : null}
        <ol className="flex flex-col gap-2">
          {exam.tasks.map((task) => {
            const status = task.done ? t('taskDone') : task.today ? t('taskToday') : task.day > localToday() ? t('taskAhead') : t('taskLeft')
            const topics = task.topics.map((x) => x.title).join(', ')
            return (
              <li key={task.id} aria-label={t('taskLabel', { day: dayName(task.day), topics, status })} className={cn('flex items-center gap-3 rounded-xl px-3 py-2 text-sm', task.today ? 'bg-accent-soft' : 'bg-surface-2')}>
                <span aria-hidden className={cn('flex size-6 shrink-0 items-center justify-center rounded-full text-xs', task.done ? 'bg-accent text-accent-fg' : 'border border-border')}>
                  {task.done ? '✓' : ''}
                </span>
                <span className="w-28 shrink-0 text-muted">{dayName(task.day)}</span>
                <span className="flex-1">{topics}</span>
              </li>
            )
          })}
        </ol>
      </section>
    </div>
  )
}

/** Add an exam, or change one: name, date and topics. */
function ExamForm({ exam, onDone }: { exam?: Exam; onDone: () => void }) {
  const t = useTranslations('exams')
  const [name, setName] = useState(exam?.name ?? '')
  const [date, setDate] = useState(exam?.date ?? '')
  const [topics, setTopics] = useState<PickedTopic[]>(exam?.topics.flatMap((x) => (x.key.startsWith('topic:') ? [{ id: x.key.slice(6), title: x.title }] : [])) ?? [])
  const [problem, setProblem] = useState<string | null>(null)
  const [create, creating] = useMutation(CreateExamDocument, { refetchQueries: [ExamsDocument, WeakTopicsDocument] })
  const [update, updating] = useMutation(UpdateExamDocument, { refetchQueries: [ExamsDocument, WeakTopicsDocument] })
  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={async (e) => {
        e.preventDefault()
        setProblem(null)
        const input = { name, date, topicIds: topics.map((x) => x.id) }
        const message = exam
          ? (await update({ variables: { input: { id: exam.id, ...input } } })).data?.updateExam.userErrors[0]?.message
          : (await create({ variables: { input } })).data?.createExam.userErrors[0]?.message
        if (message) setProblem(message)
        else onDone()
      }}
    >
      <div className="flex flex-wrap gap-3">
        <label className="flex min-w-56 flex-1 flex-col gap-1 text-sm">
          {t('name')}
          <input required maxLength={EXAM_LIMITS.name} value={name} placeholder={t('namePlaceholder')} onChange={(e) => setName(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          {t('date')}
          <input type="date" required min={localToday()} value={date} onChange={(e) => setDate(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
        </label>
      </div>
      <TopicPicker picked={topics} onChange={setTopics} />
      {problem ? <Alert tone="error">{problem}</Alert> : null}
      <div className="flex gap-2">
        <Button type="submit" size="sm" disabled={creating.loading || updating.loading || !topics.length}>
          {exam ? t('save') : t('create')}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={onDone}>
          {t('cancel')}
        </Button>
      </div>
    </form>
  )
}

function TopicPicker({ picked, onChange }: { picked: PickedTopic[]; onChange: (topics: PickedTopic[]) => void }) {
  const t = useTranslations('exams')
  const inputId = useId()
  const [query, setQuery] = useState('')
  const [find, found] = useLazyQuery(ExamTopicOptionsDocument)
  useEffect(() => {
    if (query.trim().length < 2) return
    const timer = setTimeout(() => void find({ variables: { query: query.trim() } }), 250)
    return () => clearTimeout(timer)
  }, [query, find])
  const options = query.trim().length >= 2 ? (found.data?.examTopicOptions ?? []).filter((o) => !picked.some((p) => p.id === o.id)) : []
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="text-sm">{t('topics')}</legend>
      {picked.length ? (
        <ul className="flex flex-wrap gap-2">
          {picked.map((p) => (
            <li key={p.id} className="flex items-center gap-1 rounded-full bg-accent-soft py-1 pl-3 pr-1 text-sm text-accent">
              {p.title}
              <button type="button" aria-label={t('removeTopic', { title: p.title })} className="rounded-full px-2 hover:bg-accent/10" onClick={() => onChange(picked.filter((x) => x.id !== p.id))}>
                ×
              </button>
            </li>
          ))}
        </ul>
      ) : null}
      {picked.length < EXAM_LIMITS.topics ? (
        <>
          <label htmlFor={inputId} className="sr-only">
            {t('findTopic')}
          </label>
          <input id={inputId} type="search" value={query} placeholder={t('findTopic')} onChange={(e) => setQuery(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3 text-sm" />
          <p className="text-xs text-muted">{t('findTopicHelp')}</p>
          {query.trim().length >= 2 && found.data && !options.length ? <p className="text-sm text-muted">{t('noTopicFound')}</p> : null}
          {options.length ? (
            <ul className="flex flex-col gap-1">
              {options.slice(0, 8).map((o) => (
                <li key={o.id}>
                  <button
                    type="button"
                    aria-label={t('addTopic', { title: o.title })}
                    className="flex w-full items-baseline justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm hover:bg-surface-2"
                    onClick={() => {
                      onChange([...picked, { id: o.id, title: o.title }])
                      setQuery('')
                    }}
                  >
                    <span>{o.title}</span>
                    <span className="text-xs text-muted">{o.subjectTitle}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : null}
        </>
      ) : null}
    </fieldset>
  )
}

/** Weak topics to revise first, each with why (lvn-backend ADR-0070). */
export function WeakTopics() {
  const t = useTranslations('exams')
  const { data } = useQuery(WeakTopicsDocument, { fetchPolicy: 'cache-and-network' })
  const weak = data?.weakTopics
  if (!weak) return null
  return (
    <section aria-labelledby="weak-topics" className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <h2 id="weak-topics" className="text-lg font-bold">
        {t('weak')}
      </h2>
      <p className="text-sm text-muted">{weak.length ? t('weakHelp') : t('noWeak')}</p>
      <ul className="flex flex-col gap-2">
        {weak.map((w) => (
          <li key={w.key} className="flex flex-col rounded-xl bg-surface-2 px-3 py-2 text-sm">
            <span className="font-medium">{w.title ?? (w.key.startsWith('core:') ? coreName(w.key) : t('aTopic'))}</span>
            <span className="text-muted">{w.reason === 'LOW_ACCURACY' ? t('reason.LOW_ACCURACY', { value: pct(w.accuracy ?? 0) }) : t('reason.NOT_REVISITED', { exam: w.examName ?? '' })}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
