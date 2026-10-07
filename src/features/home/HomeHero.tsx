/* ============================================================
   HomeHero — the top of the landing page.

     Signed in   greeting + streak, today's goal ring, one big
                 "Continue where you left off" button, the review
                 queue and (once the backend produces them)
                 trending topics.
     Guests      what the site is, three numbers that prove it,
                 "Start learning" and a sign-in nudge.

   One row on laptops; on phones the pieces stack so the continue
   button is a full-width thumb target.
   ============================================================ */

import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Flame, PlayCircle, RotateCcw, Sparkles, TrendingUp } from 'lucide-react'
import type { TrendingDoc } from '@schema/firestore'
import { useAuth, type AppUser } from '@/features/auth/auth'
import type { Catalog } from '@/features/catalog/types'
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
  const goalMet = goal >= 1
  const last = useMemo(() => lastVisit(activity), [activity])
  const due = useMemo(() => dueForReview(progress, activity), [progress, activity])
  const lastSubject = last?.key.split('/')[0]

  return (
    <section className="hero" aria-label="Your day">
      <div className="hero-row">
        <div className="hero-hello">
          <span className={`hero-flame ${streak ? 'is-on' : ''}`} aria-hidden><Flame size={20} /></span>
          <div className="hero-hello-text">
            <h1>{greeting()}, {user.name.split(' ')[0]}</h1>
            <p className="muted">
              {streak > 0
                ? <><strong className="hero-streak">{streak}-day streak</strong> · keep it going</>
                : 'Study a minute today to start a streak'}
            </p>
          </div>
        </div>

        <div className={`hero-goal ${goalMet ? 'is-met' : ''}`} title={`Daily goal: ${dailyGoal} min`}>
          <svg viewBox="0 0 36 36" className="goal-ring" aria-hidden>
            <circle cx="18" cy="18" r="15" />
            <circle cx="18" cy="18" r="15" style={{ strokeDashoffset: 94.25 * (1 - goal) }} />
          </svg>
          <span className="hero-goal-text">
            <strong>{formatDuration(todaySec)}</strong>
            <span className="muted small">{goalMet ? 'goal done 🎉' : `of ${dailyGoal} min today`}</span>
          </span>
        </div>
      </div>

      <div className="hero-actions">
        {last ? (
          <Link className="hero-continue" to={`/${last.key}`} title={last.title} data-cat-of={lastSubject}>
            <PlayCircle size={20} aria-hidden />
            <span className="hero-continue-text">
              <span className="hero-continue-label">Continue where you left off</span>
              <strong>{last.title}</strong>
            </span>
            <ArrowRight size={16} aria-hidden className="hero-continue-arrow" />
          </Link>
        ) : (
          <a className="hero-continue" href="#subjects">
            <Sparkles size={20} aria-hidden />
            <span className="hero-continue-text">
              <span className="hero-continue-label">Nothing started yet</span>
              <strong>Pick a subject below</strong>
            </span>
            <ArrowRight size={16} aria-hidden className="hero-continue-arrow" />
          </a>
        )}
        {due.length > 0 && (
          <Link className="btn hero-review" to="/history"><RotateCcw size={15} aria-hidden /> Review {due.length}</Link>
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

/** Landing hero for visitors who aren't signed in. */
export function GuestHero({ catalog }: { catalog: Catalog }) {
  const auth = useAuth()
  const stats = useMemo(() => {
    let topics = 0
    let problems = 0
    for (const s of catalog.subjects) {
      if (s.kind === 'problems') problems += s.itemCount
      else topics += s.itemCount
    }
    return { subjects: catalog.subjects.length, topics, problems }
  }, [catalog])

  return (
    <section className="hero hero-guest" aria-label="Welcome">
      <div className="hero-guest-text">
        <h1>Interview-ready CS, one note at a time.</h1>
        <p>
          Focused notes and curated problems across DSA, core CS, engineering, AI and programming.
          Free to read — sign in to keep your streak.
        </p>
      </div>
      <ul className="hero-stats" aria-label="What's inside">
        <li><strong>{stats.subjects}</strong><span>subjects</span></li>
        <li><strong>{stats.topics}</strong><span>topics</span></li>
        <li><strong>{stats.problems}</strong><span>problems</span></li>
      </ul>
      <div className="hero-actions">
        <a className="btn btn-primary hero-cta" href="#subjects">Start learning <ArrowRight size={15} aria-hidden /></a>
        {auth.status !== 'unavailable' && (
          <Link className="btn hero-cta" to="/login?next=%2F"><Flame size={15} aria-hidden /> Track my progress</Link>
        )}
      </div>
    </section>
  )
}
