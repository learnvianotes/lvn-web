'use client'

import { useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { ClassroomPerformanceDocument, ClassroomRhythmRingDocument } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

/**
 * A class's Rhythm this week (lvn-backend ADR-0072): totals for every member to see, and the names of the students who
 * chose to share (a child account by first name).
 */
export function ClassRhythm({ classroomId }: { classroomId: string }) {
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
