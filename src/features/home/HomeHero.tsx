/* ============================================================
   HomeHero — signed-in learners only. One slim bar: greeting and
   streak, today's goal, continue where you left off, and the
   review queue. (Trending topics appear once the backend has
   produced them.)
   ============================================================ */

import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { Flame, PlayCircle, RotateCcw, TrendingUp } from 'lucide-react'
import type { TrendingDoc } from '@schema/firestore'
import type { AppUser } from '@/features/auth/auth'
import { dayKey, useProgress } from '@/features/progress/store'
import { daySeconds, formatDuration, lastVisit, useActivity } from '@/features/progress/activity'
import { activeDays, currentStreak, dueForReview } from '@/features/progress/stats'
import { usePrefs } from '@/features/progress/prefs'
import { userData } from '@/services/userdata/repository'

function greeting() {
  const h = new Date().getHours()
  return h < 5 ? 'Late night' : h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening'
}

function useTrending() {
  const [trending, setTrending] = useState<TrendingDoc | null>(null)
  useEffect(() => {
    let alive = true
    userData().then((r) => r.trending()).then((t) => { if (alive) setTrending(t) }, () => {})
    return () => { alive = false }
  }, [])
  return trending
}

export function HomeHero({ user }: { user: AppUser }) {
  const progress = useProgress()
  const activity = useActivity()
  const { dailyGoal } = usePrefs()
  const trending = useTrending()

  const streak = useMemo(() => currentStreak(activeDays(progress, activity)), [progress, activity])
  const today = activity[dayKey()]
  const todaySec = daySeconds(today) + (today?.focus ?? 0)
  const goal = Math.min(1, todaySec / (dailyGoal * 60))
  const last = useMemo(() => lastVisit(activity), [activity])
  const due = useMemo(() => dueForReview(progress, activity), [progress, activity])

  return (
    <section className="hero" aria-label="Your day">
      <div className="hero-hello">
        <span className={`hero-flame ${streak ? 'is-on' : ''}`} aria-hidden><Flame size={18} /></span>
        <div className="hero-hello-text">
          <h1>{greeting()}, {user.name.split(' ')[0]}</h1>
          <p className="muted small">
            {streak > 0 ? <>🔥 {streak}-day streak — keep it going</> : 'Study a minute today to start a streak'}
          </p>
        </div>
      </div>

      <div className="hero-goal" title={`Daily goal: ${dailyGoal} min`}>
        <svg viewBox="0 0 36 36" className="goal-ring" aria-hidden>
          <circle cx="18" cy="18" r="15" />
          <circle cx="18" cy="18" r="15" style={{ strokeDashoffset: 94.25 * (1 - goal) }} />
        </svg>
        <span><strong>{formatDuration(todaySec)}</strong><span className="muted small"> / {dailyGoal} min</span></span>
      </div>

      <div className="hero-actions">
        {due.length > 0 && (
          <Link className="btn btn-sm" to="/history"><RotateCcw size={14} aria-hidden /> Review {due.length}</Link>
        )}
        {last ? (
          <Link className="btn btn-sm btn-primary hero-continue" to={`/${last.key}`} title={last.title}>
            <PlayCircle size={15} aria-hidden /> <span>Continue: {last.title}</span>
          </Link>
        ) : (
          <a className="btn btn-sm btn-primary" href="#subjects">Pick a subject</a>
        )}
      </div>

      {trending && trending.topics.length > 0 && (
        <div className="hero-trending">
          <span className="muted small"><TrendingUp size={13} aria-hidden /> Trending:</span>
          {trending.topics.slice(0, 4).map((t) => <Link key={t.key} to={`/${t.key}`} className="chip-link">{t.title}</Link>)}
        </div>
      )}
    </section>
  )
}
