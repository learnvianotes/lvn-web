'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Check } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { LoadFailed } from '@/components/ui/query-state'
import { AddWeeklyTaskDocument, RemoveWeeklyTaskDocument, TaskSuggestionsDocument, UpdateWeeklyTaskDocument, WeeklyTasksDocument, type WeeklyTaskFieldsFragment, type WeeklyTaskKind } from '@/graphql/generated/graphql'
import { TopicChoice } from './Focus'

const KINDS: WeeklyTaskKind[] = ['REVIEWS', 'QUIZ_ANSWERS', 'TOPIC_MINUTES']
const RANGE: Record<WeeklyTaskKind, { min: number; max: number; start: number }> = {
  REVIEWS: { min: 5, max: 500, start: 50 },
  QUIZ_ANSWERS: { min: 5, max: 300, start: 20 },
  TOPIC_MINUTES: { min: 10, max: 600, start: 60 },
}
const refetchQueries = [WeeklyTasksDocument, TaskSuggestionsDocument]

/**
 * This week's tasks (lvn-backend ADR-0081): up to three goals the person picks, often from suggestions, each with how
 * far it has come and, if they wrote one, when and where they mean to do it. An unfinished task just ends with the
 * week: nothing here is ever "failed" or "lost".
 */
export function WeeklyTasks() {
  const t = useTranslations('tasks')
  const { data, error, refetch } = useQuery(WeeklyTasksDocument, { fetchPolicy: 'cache-and-network' })
  const week = data?.weeklyTasks
  const [adding, setAdding] = useState(false)
  // Nothing while it loads (the page around it is there); a failure says so in one line where the tasks would be.
  if (!week) return error && !data ? <LoadFailed message={t('loadFailed')} onRetry={refetch} /> : null
  const room = week.tasks.length < week.max
  const done = week.tasks.filter((x) => x.done).length
  return (
    <section id="tasks" aria-labelledby="tasks-title" className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-5 shadow-sm">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 id="tasks-title" className="text-lg font-semibold">
          {t('title')}
        </h2>
        {week.tasks.length ? <span className="text-sm text-muted">{t('doneCount', { done, total: week.tasks.length })}</span> : null}
      </div>
      {!week.tasks.length ? <p className="text-sm text-muted">{t('lead')}</p> : null}
      <ul className="flex flex-col gap-2">
        {week.tasks.map((task) => (
          <TaskRow key={task.id} task={task} />
        ))}
      </ul>
      {room ? adding ? <AddTask onClose={() => setAdding(false)} /> : (
        <Button type="button" variant="secondary" size="sm" className="self-start" onClick={() => setAdding(true)}>
          {t('add')}
        </Button>
      ) : <p className="text-xs text-muted">{t('full', { max: week.max })}</p>}
    </section>
  )
}

export function taskLabel(t: ReturnType<typeof useTranslations>, task: { kind: WeeklyTaskKind; target: number; topicTitle?: string | null }) {
  return t(`label.${task.kind}`, { target: task.target, topic: task.topicTitle ?? '__none' })
}

function TaskRow({ task }: { task: WeeklyTaskFieldsFragment }) {
  const t = useTranslations('tasks')
  const [editing, setEditing] = useState(false)
  const [target, setTarget] = useState(task.target)
  const [plan, setPlan] = useState(task.plan ?? '')
  const [problem, setProblem] = useState<string | null>(null)
  const [update, updating] = useMutation(UpdateWeeklyTaskDocument, { refetchQueries })
  const [remove, removing] = useMutation(RemoveWeeklyTaskDocument, { refetchQueries })
  const share = Math.min(task.progress / task.target, 1)
  const label = taskLabel(t, task)
  return (
    <li className="flex flex-col gap-2 rounded-2xl bg-surface-2 px-4 py-3">
      <div className="flex items-center gap-3">
        {task.done ? (
          <span aria-hidden className="grid size-6 shrink-0 place-items-center rounded-full bg-accent text-accent-fg">
            <Check className="size-4" />
          </span>
        ) : null}
        <span className="min-w-0 flex-1 font-semibold">{label}</span>
        <span className="shrink-0 text-sm tabular-nums text-muted">{t('progress', { progress: Math.min(task.progress, task.target), target: task.target })}</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-surface" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={task.target} aria-valuenow={Math.min(task.progress, task.target)}>
        <div className="h-full rounded-[4px] bg-accent transition-[width] duration-300" style={{ width: `${Math.round(share * 100)}%` }} />
      </div>
      {task.plan && !editing ? <p className="text-sm text-muted">{t('planShown', { plan: task.plan })}</p> : null}
      {editing ? (
        <form
          className="flex flex-col gap-2"
          onSubmit={async (e) => {
            e.preventDefault()
            const res = await update({ variables: { input: { id: task.id, target, plan } } }).catch(() => null)
            const why = res?.data?.updateWeeklyTask.userErrors[0]?.message ?? (res ? null : t('failed'))
            setProblem(why)
            if (!why) setEditing(false)
          }}
        >
          <label className="flex flex-col gap-1 text-sm">
            {t('target')}
            <input type="number" min={RANGE[task.kind].min} max={RANGE[task.kind].max} value={target} onChange={(e) => setTarget(Number(e.target.value))} className="h-10 w-32 rounded-xl border border-border bg-surface px-3" />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            {t('plan')}
            <input type="text" maxLength={140} value={plan} placeholder={t('planPlaceholder')} onChange={(e) => setPlan(e.target.value)} className="h-10 rounded-xl border border-border bg-surface px-3" />
          </label>
          {problem ? <Alert tone="error">{problem}</Alert> : null}
          <div className="flex gap-2">
            <Button type="submit" size="sm" disabled={updating.loading}>
              {t('save')}
            </Button>
            <Button type="button" variant="ghost" size="sm" onClick={() => setEditing(false)}>
              {t('cancel')}
            </Button>
          </div>
        </form>
      ) : (
        <div className="flex gap-3 text-sm">
          <button type="button" className="font-medium text-accent hover:underline" onClick={() => setEditing(true)}>
            {t('edit')}
          </button>
          <button type="button" className="font-medium text-muted hover:underline" disabled={removing.loading} aria-label={t('removeLabel', { task: label })} onClick={() => void remove({ variables: { id: task.id } })}>
            {t('remove')}
          </button>
        </div>
      )}
    </li>
  )
}

function AddTask({ onClose }: { onClose: () => void }) {
  const t = useTranslations('tasks')
  const suggestions = useQuery(TaskSuggestionsDocument, { fetchPolicy: 'cache-and-network' }).data?.taskSuggestions ?? []
  const [kind, setKind] = useState<WeeklyTaskKind>('REVIEWS')
  const [target, setTarget] = useState(RANGE.REVIEWS.start)
  const [topic, setTopic] = useState<{ key: string; title: string } | null>(null)
  const [plan, setPlan] = useState('')
  const [problem, setProblem] = useState<string | null>(null)
  const [add, adding] = useMutation(AddWeeklyTaskDocument, { refetchQueries })
  const submit = async (input: { kind: WeeklyTaskKind; target: number; topicId: string | null; plan: string }) => {
    const res = await add({ variables: { input: { ...input, plan: input.plan || null } } }).catch(() => null)
    const why = res?.data?.addWeeklyTask.userErrors[0]?.message ?? (res ? null : t('failed'))
    setProblem(why)
    if (!why) onClose()
  }
  return (
    <div className="flex flex-col gap-4 rounded-2xl border border-border p-4">
      {suggestions.length ? (
        <div className="flex flex-col gap-2">
          <h3 className="text-sm font-semibold">{t('suggested')}</h3>
          <ul className="flex flex-col gap-2">
            {suggestions.map((s) => (
              <li key={`${s.kind}:${s.topicId ?? ''}`} className="flex flex-wrap items-center gap-3 rounded-xl bg-surface-2 px-3 py-2">
                <span className="flex min-w-0 flex-1 flex-col text-sm">
                  <span className="font-semibold">{taskLabel(t, s)}</span>
                  <span className="text-muted">{s.why}</span>
                </span>
                <Button type="button" size="sm" disabled={adding.loading} aria-label={t('addSuggested', { task: taskLabel(t, s) })} onClick={() => void submit({ kind: s.kind, target: s.target, topicId: s.topicId ?? null, plan })}>
                  {t('addThis')}
                </Button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      <form
        className="flex flex-col gap-3"
        onSubmit={(e) => {
          e.preventDefault()
          void submit({ kind, target, topicId: topic?.key.startsWith('topic:') ? topic.key.slice(6) : null, plan })
        }}
      >
        <h3 className="text-sm font-semibold">{suggestions.length ? t('somethingElse') : t('newTask')}</h3>
        <div className="flex flex-wrap gap-3">
          <label className="flex flex-col gap-1 text-sm">
            {t('kind')}
            <select
              value={kind}
              onChange={(e) => {
                const k = e.target.value as WeeklyTaskKind
                setKind(k)
                setTarget(RANGE[k].start)
              }}
              className="h-10 rounded-xl border border-border bg-surface px-3"
            >
              {KINDS.map((k) => (
                <option key={k} value={k}>
                  {t(`kinds.${k}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            {t('target')}
            <input type="number" min={RANGE[kind].min} max={RANGE[kind].max} value={target} onChange={(e) => setTarget(Number(e.target.value))} className="h-10 w-32 rounded-xl border border-border bg-surface px-3" />
          </label>
        </div>
        {kind !== 'REVIEWS' ? <TopicChoice value={topic} onChange={setTopic} /> : null}
        <label className="flex flex-col gap-1 text-sm">
          {t('plan')}
          <input type="text" maxLength={140} value={plan} placeholder={t('planPlaceholder')} onChange={(e) => setPlan(e.target.value)} className="h-10 rounded-xl border border-border bg-surface px-3" />
        </label>
        {problem ? <Alert tone="error">{problem}</Alert> : null}
        <div className="flex gap-2">
          <Button type="submit" size="sm" disabled={adding.loading}>
            {t('addIt')}
          </Button>
          <Button type="button" variant="ghost" size="sm" onClick={onClose}>
            {t('cancel')}
          </Button>
        </div>
      </form>
    </div>
  )
}
