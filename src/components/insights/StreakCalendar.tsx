/* ============================================================
   StreakCalendar — month view; a day is marked once at least a
   minute was spent reading that day.
   ============================================================ */

import { useState } from 'react'
import { ChevronLeft, ChevronRight, Flame } from 'lucide-react'
import { dayKey, type ProgressState } from '@/progress/store'
import { currentStreak, isActiveDay, longestStreak } from '@/progress/stats'

const WEEKDAYS = ['M', 'T', 'W', 'T', 'F', 'S', 'S']

export function StreakCalendar({ progress }: { progress: ProgressState }) {
  const today = new Date()
  const [month, setMonth] = useState(() => new Date(today.getFullYear(), today.getMonth(), 1))
  const streak = currentStreak(progress)
  const best = longestStreak(progress)

  const first = month.getDay() === 0 ? 6 : month.getDay() - 1 // Monday-first
  const days = new Date(month.getFullYear(), month.getMonth() + 1, 0).getDate()
  const cells: (Date | null)[] = [
    ...Array.from({ length: first }, () => null),
    ...Array.from({ length: days }, (_, i) => new Date(month.getFullYear(), month.getMonth(), i + 1)),
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
        <button className="icon-btn sm" onClick={() => shift(-1)} aria-label="Previous month"><ChevronLeft size={16} /></button>
        <span>{month.toLocaleDateString(undefined, { month: 'long', year: 'numeric' })}</span>
        <button className="icon-btn sm" onClick={() => shift(1)} disabled={isCurrentMonth} aria-label="Next month"><ChevronRight size={16} /></button>
      </div>
      <div className="calendar-grid" role="grid">
        {WEEKDAYS.map((d, i) => <span key={i} className="calendar-wd" aria-hidden>{d}</span>)}
        {cells.map((d, i) => {
          if (!d) return <span key={i} />
          const key = dayKey(d)
          const active = isActiveDay(progress, key)
          const count = progress.studied[key] ?? 0
          return (
            <span
              key={i}
              role="gridcell"
              className={`calendar-day ${active ? 'is-active' : ''} ${key === todayKey ? 'is-today' : ''}`}
              title={count ? `${count} completed` : undefined}
              aria-label={`${d.toDateString()}${active ? ', studied' : ''}`}
            >
              {d.getDate()}
            </span>
          )
        })}
      </div>
    </div>
  )
}
