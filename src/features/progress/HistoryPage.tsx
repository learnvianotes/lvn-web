/* ============================================================
   /history — the learner's study log (signed-in only):
   streak summary, what was studied on each day, for
   how long, whether it was a revisit, and the review queue.
   ============================================================ */

import './history.css'
import { useEffect, useMemo } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { ArrowLeft, Clock, Flame, RotateCcw, Timer, Trophy } from 'lucide-react'
import { useAuth } from '@/features/auth/auth'
import { SignInBanner } from '@/features/auth/SignInBanner'
import { dayKey, useProgress } from '@/features/progress/store'
import { daySeconds, firstSeen, formatDuration, useActivity } from '@/features/progress/activity'
import { activeDays, currentStreak, dueForReview, longestStreak } from '@/features/progress/stats'
import { Loading } from '@/shared/ui/Status'

function formatDay(day: string) {
  const [y, m, d] = day.split('-').map(Number)
  const date = new Date(y, m - 1, d)
  const today = dayKey()
  const yesterday = new Date()
  yesterday.setDate(yesterday.getDate() - 1)
  if (day === today) return 'Today'
  if (day === dayKey(yesterday)) return 'Yesterday'
  return date.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'long', year: date.getFullYear() === new Date().getFullYear() ? undefined : 'numeric' })
}

export function HistoryPage() {
  const auth = useAuth()
  if (auth.status === 'loading') return <Loading />
  if (auth.status !== 'signed-in') {
    return (
      <div className="page page-narrow">
        <Link to="/" className="back-link"><ArrowLeft size={14} aria-hidden /> All subjects</Link>
        <h1 className="page-title history-title">Study history</h1>
        <SignInBanner />
      </div>
    )
  }
  return <History />
}

function History() {
  const progress = useProgress()
  const activity = useActivity()
  const location = useLocation()
  const days = useMemo(() => activeDays(progress, activity), [progress, activity])
  const first = useMemo(() => firstSeen(activity), [activity])
  const due = useMemo(() => dueForReview(progress, activity), [progress, activity])
  const logDays = Object.keys(activity).filter((d) => Object.keys(activity[d].topics).length || activity[d].focus).sort().reverse()

  const weekAgo = new Date()
  weekAgo.setDate(weekAgo.getDate() - 6)
  const weekKey = dayKey(weekAgo)
  const weekSeconds = logDays.filter((d) => d >= weekKey).reduce((n, d) => n + daySeconds(activity[d]) + activity[d].focus, 0)
  const totalSeconds = logDays.reduce((n, d) => n + daySeconds(activity[d]) + activity[d].focus, 0)

  useEffect(() => {
    const id = location.hash.slice(1)
    if (id) document.getElementById(id)?.scrollIntoView({ block: 'start', behavior: 'smooth' })
  }, [location.hash])

  return (
    <div className="page history">
      <div className="page-head">
        <Link to="/" className="back-link"><ArrowLeft size={14} aria-hidden /> All subjects</Link>
        <h1 className="page-title">Study history</h1>
        <p className="page-desc">Every topic you opened, how long you spent, and what’s worth revisiting.</p>
      </div>

      <div className="stat-row">
        <div className="stat"><Flame size={18} aria-hidden className="stat-icon is-fire" /><strong>{currentStreak(days)}</strong><span>day streak</span></div>
        <div className="stat"><Trophy size={18} aria-hidden className="stat-icon" /><strong>{longestStreak(days)}</strong><span>best streak</span></div>
        <div className="stat"><Clock size={18} aria-hidden className="stat-icon" /><strong>{formatDuration(weekSeconds)}</strong><span>last 7 days</span></div>
        <div className="stat"><Timer size={18} aria-hidden className="stat-icon" /><strong>{formatDuration(totalSeconds)}</strong><span>all time</span></div>
      </div>

      <div className="history-grid">
        <div className="history-log">
          <h2 className="section-title">Day by day</h2>
          {logDays.length === 0 && (
            <div className="empty-card">
              <p>No study sessions yet. Open any topic — your time is logged automatically while you read.</p>
              <Link className="btn btn-primary btn-sm" to="/">Start studying</Link>
            </div>
          )}
          {logDays.map((day) => {
            const log = activity[day]
            const entries = Object.entries(log.topics).sort((a, b) => b[1].last - a[1].last)
            return (
              <section key={day} id={day} className="day-card">
                <header className="day-card-head">
                  <h3>{formatDay(day)}</h3>
                  <span className="muted small">
                    {formatDuration(daySeconds(log))} studied{log.focus ? ` · ${formatDuration(log.focus)} focus` : ''}
                  </span>
                </header>
                <ul className="day-list">
                  {entries.map(([key, v]) => {
                    const revisit = (first.get(key) ?? day) < day
                    const [subjectId, topicId] = key.split('/')
                    return (
                      <li key={key}>
                        <Link to={`/${subjectId}/${topicId}`} className="day-item">
                          <span className="day-item-main">
                            <span className="day-item-title">{v.title}</span>
                            <span className="muted small">{v.subject} · {new Date(v.last).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })}</span>
                          </span>
                          {revisit && <span className="tag tag--revisit"><RotateCcw size={11} aria-hidden /> Revisit</span>}
                          {progress.topics[key] && <span className="tag tag--done">Completed</span>}
                          <span className="day-item-time">{formatDuration(v.sec)}</span>
                        </Link>
                      </li>
                    )
                  })}
                  {!entries.length && <li className="muted small">Focus session only</li>}
                </ul>
              </section>
            )
          })}
        </div>

        <aside className="history-side">
          <section className="panel">
            <h2 className="panel-title">Due for review</h2>
            {due.length === 0 ? (
              <p className="muted small">Nothing due. Topics you complete come back here after 1, 3, 7, 14 and 30 days so they stick.</p>
            ) : (
              <ul className="review-list">
                {due.slice(0, 12).map((t) => {
                  const [s, id] = t.key.split('/')
                  return (
                    <li key={t.key}>
                      <Link to={`/${s}/${id}`}>
                        <span>{t.title}</span>
                        <span className="muted small">{t.flagged ? 'Marked to revisit' : `${t.daysAgo} days ago`} · {t.subject}</span>
                      </Link>
                    </li>
                  )
                })}
              </ul>
            )}
          </section>
        </aside>
      </div>
    </div>
  )
}
