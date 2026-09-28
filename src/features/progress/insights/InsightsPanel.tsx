/* ============================================================
   InsightsPanel — the right-hand progress panel.
     Signed in:  progress wheel, today's summary, streak calendar
     Guests:     sign-in banner over a preview of the calendar
                 (tracking is a signed-in feature)
   ============================================================ */

import './insights.css'
import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Clock, Flame, History, Target } from 'lucide-react'
import { useCatalog } from '@/features/catalog/hooks'
import { dayKey, useProgress } from '@/features/progress/store'
import { daySeconds, formatDuration, useActivity } from '@/features/progress/activity'
import { activeDays, currentStreak, subjectProgress } from '@/features/progress/stats'
import { useAuth } from '@/features/auth/auth'
import { SignInBanner } from '@/features/auth/SignInBanner'
import { ProgressBreakdown, ProgressWheel } from './ProgressWheel'
import { StreakCalendar } from './StreakCalendar'
import { ADSENSE_CLIENT } from '@/config'

interface Props {
  selectedId?: string
  onSelectSubject: (subjectId: string) => void
}

export function InsightsPanel(props: Props) {
  const auth = useAuth()
  return (
    <div className="insights">
      {auth.status === 'signed-in' ? <SignedIn {...props} /> : auth.status === 'loading' ? <Skeleton /> : <Guest />}
      <AdSlot />
    </div>
  )
}

function SignedIn({ selectedId, onSelectSubject }: Props) {
  const { data: catalog } = useCatalog()
  const progress = useProgress()
  const activity = useActivity()
  const items = useMemo(
    () => (catalog ? catalog.subjects.map((s) => subjectProgress(s, progress)) : []),
    [catalog, progress],
  )
  const today = activity[dayKey()]
  const todaySec = daySeconds(today) + (today?.focus ?? 0)
  const streak = currentStreak(activeDays(progress, activity))

  return (
    <>
      <section className="panel">
        <h2 className="panel-title">Progress</h2>
        {items.length > 0 && (
          <>
            <ProgressWheel items={items} selectedId={selectedId} onSelect={onSelectSubject} />
            <details className="breakdown-toggle">
              <summary>By subject</summary>
              <ProgressBreakdown items={items} selectedId={selectedId} onSelect={onSelectSubject} />
            </details>
          </>
        )}
      </section>
      <section className="panel today-panel" aria-label="Today">
        <div className="today-stat"><Flame size={16} aria-hidden className={streak ? 'streak-on' : 'streak-off'} /><strong>{streak}</strong><span>day streak</span></div>
        <div className="today-stat"><Clock size={16} aria-hidden /><strong>{formatDuration(todaySec)}</strong><span>today</span></div>
        <div className="today-stat"><Target size={16} aria-hidden /><strong>{Object.keys(today?.topics ?? {}).length}</strong><span>topics</span></div>
      </section>
      <section className="panel">
        <h2 className="panel-title">Study streak</h2>
        <StreakCalendar progress={progress} activity={activity} />
        <Link to="/history" className="panel-link"><History size={14} aria-hidden /> Study history <ArrowRight size={13} aria-hidden /></Link>
      </section>
    </>
  )
}

function Guest() {
  return (
    <section className="panel guest-panel">
      <div className="guest-preview" aria-hidden>
        <StreakCalendar progress={{ problems: {}, topics: {}, revisitTopics: {}, studied: demoStudied() }} activity={{}} preview />
      </div>
      <SignInBanner overlay />
    </section>
  )
}

/** A believable-looking month for the blurred preview behind the sign-in banner. */
function demoStudied() {
  const out: Record<string, number> = {}
  const d = new Date()
  for (let i = 0; i < 28; i++) {
    if (i % 5 !== 3 && i % 7 !== 6) out[dayKey(d)] = 1
    d.setDate(d.getDate() - 1)
  }
  return out
}

function Skeleton() {
  return <section className="panel panel-skeleton" aria-hidden />
}

/**
 * Reserved space for a single ad unit. Renders nothing until an ad
 * client is configured (ADSENSE_CLIENT in src/config.ts), so no
 * third-party script loads by default.
 */
function AdSlot() {
  if (!ADSENSE_CLIENT) return null
  return <aside className="panel ad-slot" aria-label="Advertisement" data-ad-client={ADSENSE_CLIENT} />
}
