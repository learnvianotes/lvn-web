/* ============================================================
   StreakCalendar — month view. A day is marked once something was
   completed or at least a minute was studied (see stats.ts).
   Intensity follows the time spent; days link to their history.
   ============================================================ */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft, ChevronRight, Flame } from 'lucide-react'
import { dayKey, type ProgressState } from '@/features/progress/store'
import { daySeconds, formatDuration, type Activity } from '@/features/progress/activity'
import { activeDays, currentStreak, longestStreak } from '@/features/progress/stats'

const WEEKDAYS = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

function level(seconds: number) {
  if (seconds >= 60 * 60) return 3
  if (seconds >= 20 * 60) return 2
  return 1
}

/** `preview`: static, non-interactive rendering (blurred teaser for guests). */
export function StreakCalendar({ progress, activity, preview = false }: { progress: ProgressState; activity: Activity; preview?: boolean }) {
  const navigate = useNavigate()
  const today = new Date()
  const [month, setMonth] = useState(() => new Date(today.getFullYear(), today.getMonth(), 1))
  const days = activeDays(progress, activity)
  const streak = currentStreak(days)
  const best = longestStreak(days)

  const first = month.getDay() === 0 ? 6 : month.getDay() - 1 // Monday-first
  const count = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()
  const cells: (Date | null)[] = [
    ...Array.from({ length: first }, () => null),
    ...Array.from({ length: count }, (_, i) => new Date(month.getFullYear(), month.getMonth(), i + 1)),
  ]
  const todayKey = dayKey(today)
  const isCurrentMonth = month.getFullYear() === today.getFullYear() && month.getMonth() === today.getMonth()
  const shift = (n: number) => setMonth(new Date(month.getFullYear(), month.getMonth() + n, 1))

  return (
    <div className="calendar">
      <div className="streak">
        <Flame size={18} className={streak ? 'streak-on' : 'streak-off'} aria-hidden />
        <strong>{streak} day{streak === 1 ? '' : 's'}</strong>
        <span className="muted">streak · best {best}</span>
      </div>
      <div className="calendar-head">
        <button className="icon-btn sm" onClick={() => shift(-1)} disabled={preview} tabIndex={preview ? -1 : undefined} aria-label="Previous month"><ChevronLeft size={16} /></button>
        <span>{month.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}</span>
        <button className="icon-btn sm" onClick={() => shift(1)} disabled={preview || isCurrentMonth} tabIndex={preview ? -1 : undefined} aria-label="Next month"><ChevronRight size={16} /></button>
      </div>
      <div className="calendar-grid" role="grid">
        {WEEKDAYS.map((d, i) => <span key={i} className="calendar-wd" aria-hidden>{d}</span>)}
        {cells.map((d, i) => {
          if (!d) return <span key={i} />
          const key = dayKey(d)
          const active = days.has(key)
          const log = activity[key]
          const seconds = daySeconds(log) + (log?.focus ?? 0)
          const topics = log ? Object.keys(log.topics).length : 0
          const label = active ? `${formatDuration(seconds)} · ${topics} topic${topics === 1 ? '' : 's'}` : undefined
          return (
            <button
              key={i}
              role="gridcell"
              className={`calendar-day ${active ? `is-active lvl-${level(seconds)}` : ''} ${key === todayKey ? 'is-today' : ''}`}
              title={label}
              aria-label={`${d.toDateString()}${label ? `, ${label}` : ''}`}
              disabled={preview || !log}
              tabIndex={preview ? -1 : undefined}
              onClick={() => navigate(`/history#${key}`)}
            >
              {d.getDate()}
            </button>
          )
        })}
      </div>
    </div>
  )
}
