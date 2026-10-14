'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { ClassroomPerformanceDocument, ClassroomRhythmRingDocument, SetClassGoalDocument, type ClassroomRhythmRingQuery } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

/**
 * A class's Rhythm this week (lvn-backend ADR-0072): totals for every member to see, and the names of the students who
 * chose to share (a child account by first name).
 */
export function ClassRhythm({ classroomId, staff = false }: { classroomId: string; staff?: boolean }) {
  const t = useTranslations('classRhythm')
  const { data } = useQuery(ClassroomRhythmRingDocument, { variables: { id: classroomId }, fetchPolicy: 'cache-and-network' })
  const ring = data?.classroom?.rhythmRing
  if (!ring) return null
  const share = ring.targetDays ? Math.min(ring.countedDays / ring.targetDays, 1) : 0
  return (
    <section aria-label={t('title')} className="flex flex-col gap-4">
      <div className="flex items-center gap-4">
        <div role="img" aria-label={`${Math.round(share * 100)}%`} className="relative size-20 shrink-0 rounded-full" style={{ background: `conic-gradient(var(--accent) ${share * 360}deg, var(--surface-2) 0deg)` }}>
          <div className="absolute inset-2 rounded-full bg-bg" />
        </div>
        <p className="text-sm">{t('summary', { met: ring.metCount, students: ring.students, counted: ring.countedDays, target: ring.targetDays })}</p>
      </div>
      {ring.goal || staff ? <ClassGoal classroomId={classroomId} goal={ring.goal ?? null} staff={staff} /> : null}
      <h3 className="font-semibold">{t('people')}</h3>
      {!ring.people.length ? <p className="text-sm text-muted">{t('nobody')}</p> : null}
      <ul className="flex flex-col gap-1">
        {ring.people.map((p) => (
          <li key={p.user.id} className="flex items-center justify-between rounded-xl bg-surface-2 px-3 py-2 text-sm">
            <span className="font-medium">{p.name}</span>
            <span className={cn(p.met ? 'text-accent' : 'text-muted')}>{t('person', { counted: p.countedDays, target: p.target })}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}

/** For staff: each student's first quiz scores and the topics the class finds hard (lvn-backend ADR-0072). */
export function ClassPerformance({ classroomId }: { classroomId: string }) {
  const t = useTranslations('classPerformance')
  const { data } = useQuery(ClassroomPerformanceDocument, { variables: { id: classroomId }, fetchPolicy: 'cache-and-network' })
  const p = data?.classroom?.performance
  if (!p) return null
  return (
    <section aria-label={t('title')} className="flex flex-col gap-4">
      <p className="text-sm text-muted">{t('lead')}</p>
      {!p.quizzes ? <p className="text-sm text-muted">{t('noQuizzes')}</p> : null}
      {p.quizzes ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-muted">
                <th className="py-2 pr-3 font-medium">{t('student')}</th>
                <th className="py-2 pr-3 font-medium">{t('submitted')}</th>
                <th className="py-2 font-medium">{t('average')}</th>
              </tr>
            </thead>
            <tbody>
              {p.students.map((s) => (
                <tr key={s.user.id} className="border-b border-border/60">
                  <td className="py-2 pr-3">{s.name}</td>
                  <td className="py-2 pr-3">
                    {s.submitted} / {p.quizzes}
                  </td>
                  <td className="py-2">{s.average === null ? t('noAverage') : t('averageValue', { value: Math.round(s.average * 100) })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
      <h3 className="font-semibold">{t('topics')}</h3>
      {!p.topics.length ? <p className="text-sm text-muted">{t('noTopics')}</p> : null}
      <ul className="flex flex-col gap-1">
        {p.topics.map((tp) => (
          <li key={tp.key} className="flex flex-wrap items-center justify-between gap-2 rounded-xl bg-surface-2 px-3 py-2 text-sm">
            <span className="font-medium">
              {tp.title}
              {tp.hard ? <span className="ml-2 rounded-full bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">{t('hard')}</span> : null}
            </span>
            <span className="text-muted">{t('topicLine', { value: Math.round(tp.accuracy * 100), answers: tp.answers })}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}

type Goal = NonNullable<NonNullable<NonNullable<ClassroomRhythmRingQuery['classroom']>['rhythmRing']>['goal']>

/**
 * The class's goal this week (lvn-backend ADR-0081): counted days across the class against a target, each student
 * counting up to a share. Everyone sees the total; teachers also see each student's part, and turn the goal on, set
 * its target or let it size itself, or turn it off. A goal not reached only shows how far it got.
 */
function ClassGoal({ classroomId, goal, staff }: { classroomId: string; goal: Goal | null; staff: boolean }) {
  const t = useTranslations('classGoal')
  const [target, setTarget] = useState(goal && !goal.automatic ? String(goal.target) : '')
  const [problem, setProblem] = useState<string | null>(null)
  const [set, setting] = useMutation(SetClassGoalDocument, { refetchQueries: [ClassroomRhythmRingDocument] })
  const save = async (on: boolean) => {
    const value = target.trim() ? Number(target) : null
    const res = await set({ variables: { input: { classroomId, on, target: on ? value : null } } }).catch(() => null)
    setProblem(res?.data?.setClassGoal.userErrors[0]?.message ?? (res ? null : t('failed')))
  }
  return (
    <section aria-labelledby="class-goal" className="flex flex-col gap-3 rounded-2xl border border-border p-4">
      <h3 id="class-goal" className="font-semibold">
        {t('title')}
      </h3>
      {goal ? (
        <>
          <div className="h-2 overflow-hidden rounded-full bg-surface-2" role="progressbar" aria-label={t('title')} aria-valuemin={0} aria-valuemax={goal.target} aria-valuenow={Math.min(goal.progress, goal.target)}>
            <div className="h-full rounded-full bg-accent transition-[width] duration-300" style={{ width: `${Math.round(Math.min(goal.progress / goal.target, 1) * 100)}%` }} />
          </div>
          <p className="text-sm">{goal.reached ? t('reached', { progress: goal.progress, target: goal.target }) : t('progress', { progress: goal.progress, target: goal.target })}</p>
          <p className="text-xs text-muted">{t('share', { share: goal.sharePerStudent })}</p>
          {goal.parts ? (
            <details className="text-sm">
              <summary className="cursor-pointer font-medium">{t('parts')}</summary>
              <ul className="mt-2 flex flex-col gap-1">
                {goal.parts.map((p) => (
                  <li key={p.user.id} className="flex justify-between rounded-lg bg-surface-2 px-3 py-1.5">
                    <span>{p.user.displayName}</span>
                    <span className="text-muted">{t('days', { days: p.countedDays })}</span>
                  </li>
                ))}
              </ul>
            </details>
          ) : null}
        </>
      ) : (
        <p className="text-sm text-muted">{t('off')}</p>
      )}
      {staff ? (
        <form
          className="flex flex-wrap items-end gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            void save(true)
          }}
        >
          <label className="flex flex-col gap-1 text-sm">
            {t('target')}
            <input type="number" min={1} value={target} placeholder={t('automatic')} onChange={(e) => setTarget(e.target.value)} className="h-10 w-40 rounded-xl border border-border bg-surface px-3" />
          </label>
          <Button type="submit" size="sm" disabled={setting.loading}>
            {goal ? t('update') : t('turnOn')}
          </Button>
          {goal ? (
            <Button type="button" variant="ghost" size="sm" disabled={setting.loading} onClick={() => void save(false)}>
              {t('turnOff')}
            </Button>
          ) : null}
        </form>
      ) : null}
      {problem ? <Alert tone="error">{problem}</Alert> : null}
    </section>
  )
}
