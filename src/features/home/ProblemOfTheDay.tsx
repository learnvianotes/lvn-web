/* ============================================================
   Problem of the day — one slim bar. The same Sheet 150 problem
   for everyone, changing at local midnight.
   ============================================================ */

import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, CalendarCheck, CheckCircle2 } from 'lucide-react'
import type { Catalog } from '@/features/catalog/types'
import { useUser } from '@/features/auth/auth'
import { dayKey, useProgress } from '@/features/progress/store'
import { Difficulty } from '@/features/study/problems/Difficulty'

function hash(s: string) {
  let h = 2166136261
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 16777619)
  return h >>> 0
}

function untilMidnight() {
  const now = new Date()
  const next = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1)
  const m = Math.round((next.getTime() - now.getTime()) / 60000)
  return m >= 60 ? `${Math.floor(m / 60)}h ${m % 60}m` : `${m}m`
}

export function ProblemOfTheDay({ catalog }: { catalog: Catalog }) {
  const user = useUser()
  const progress = useProgress()
  const [left, setLeft] = useState(untilMidnight)
  useEffect(() => {
    const id = window.setInterval(() => setLeft(untilMidnight()), 60_000)
    return () => window.clearInterval(id)
  }, [])

  const pick = useMemo(() => {
    const sheet = catalog.subjects.find((s) => s.kind === 'problems')
    const all = sheet?.topics.flatMap((t) => (t.problems ?? []).map((p) => ({ ...p, category: t }))) ?? []
    return sheet && all.length ? { sheet, problem: all[hash(dayKey()) % all.length] } : null
  }, [catalog])
  if (!pick) return null
  const { sheet, problem } = pick
  const solved = user && progress.problems[problem.id] === 'solved'

  return (
    <Link to={`/${sheet.id}/${problem.category.id}#${problem.id}`} className={`daily-bar ${solved ? 'is-solved' : ''}`}>
      <span className="daily-tag"><CalendarCheck size={14} aria-hidden /> Problem of the day</span>
      <span className="daily-name">{problem.title}</span>
      <Difficulty level={problem.difficulty} />
      <span className="daily-meta muted">LC {problem.lc} · {problem.category.title}</span>
      <span className="daily-end">
        <span className="muted small daily-left">New in {left}</span>
        {solved
          ? <span className="daily-solved"><CheckCircle2 size={15} aria-hidden /> Solved</span>
          : <span className="daily-cta">Solve <ArrowRight size={14} aria-hidden /></span>}
      </span>
    </Link>
  )
}
