/* ============================================================
   InsightsPanel — the right-hand progress panel.
     Signed in:  progress wheel (the learner's own course list —
                 the essentials until they edit it), today's
                 summary, streak calendar
     Guests:     sign-in banner over a preview of the calendar
                 (tracking is a signed-in feature)
   ============================================================ */

import './insights.css'
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Check, Clock, Flame, History, Pencil, RotateCcw, Target } from 'lucide-react'
import { useCatalog } from '@/features/catalog/hooks'
import { dayKey, useProgress } from '@/features/progress/store'
import { daySeconds, formatDuration, useActivity } from '@/features/progress/activity'
import { activeDays, currentStreak, subjectProgress } from '@/features/progress/stats'
import { useAuth } from '@/features/auth/auth'
import { SignInBanner } from '@/features/auth/SignInBanner'
import { ProgressBreakdown, ProgressWheel } from './ProgressWheel'
import { StreakCalendar } from './StreakCalendar'
import { ADSENSE_CLIENT } from '@/config'
import { resetMyCourses, setMyCourses, usePrefs } from '@/features/progress/prefs'
import { groupByCategory, myCourses, selectedIds } from '@/features/progress/myCourses'
import { track } from '@/features/telemetry/track'
import type { Catalog } from '@/features/catalog/types'

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
  const prefs = usePrefs()
  const [editing, setEditing] = useState(false)
  const all = useMemo(
    () => (catalog ? catalog.subjects.map((s) => subjectProgress(s, progress)) : []),
    [catalog, progress],
  )
  const mine = useMemo(() => myCourses(all, prefs), [all, prefs])
  const today = activity[dayKey()]
  const todaySec = daySeconds(today) + (today?.focus ?? 0)
  const streak = currentStreak(activeDays(progress, activity))

  return (
    <>
      <section className="panel">
        <div className="panel-head">
          <h2 className="panel-title">{mine.custom ? 'My courses' : 'Progress · essentials'}</h2>
          {all.length > 0 && !editing && (
            <button type="button" className="panel-action" onClick={() => setEditing(true)} aria-label="Choose the courses to track">
              <Pencil size={13} aria-hidden /> Edit
            </button>
          )}
        </div>
        {catalog && editing ? (
          <CoursePicker catalog={catalog} initial={selectedIds(mine)} custom={mine.custom} onClose={() => setEditing(false)} />
        ) : mine.items.length > 0 && (
          <>
            <ProgressWheel items={mine.items} selectedId={selectedId} onSelect={onSelectSubject} />
            <details className="breakdown-toggle">
              <summary>By course ({mine.items.length} of {all.length})</summary>
              <ProgressBreakdown items={mine.items} selectedId={selectedId} onSelect={onSelectSubject} />
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

/** Checklist of every subject, grouped like the landing page. Saved to the learner's prefs (synced). */
function CoursePicker({ catalog, initial, custom, onClose }: { catalog: Catalog; initial: string[]; custom: boolean; onClose: () => void }) {
  const [picked, setPicked] = useState(() => new Set(initial))
  const titles = new Map((catalog.categories ?? []).map((c) => [c.id, c.title]))
  const toggle = (id: string) => setPicked((prev) => {
    const next = new Set(prev)
    if (next.has(id)) next.delete(id)
    else next.add(id)
    return next
  })
  const save = () => {
    const ids = catalog.subjects.filter((s) => picked.has(s.id)).map((s) => s.id)
    setMyCourses(ids)
    track('my_courses', { v: ids.length, i: ids.join(',') })
    onClose()
  }
  const reset = () => {
    resetMyCourses()
    track('my_courses', { v: 0, i: 'essentials' })
    onClose()
  }

  return (
    <div className="course-picker">
      <p className="course-picker-hint">Pick the courses you're studying — the wheel tracks just these.</p>
      {[...groupByCategory(catalog.subjects, (catalog.categories ?? []).map((c) => c.id))].map(([cat, subjects]) => (
        <fieldset key={cat} className="course-picker-group">
          <legend>{titles.get(cat) ?? 'More'}</legend>
          {subjects.map((s) => (
            <label key={s.id} className="course-picker-row">
              <input type="checkbox" checked={picked.has(s.id)} onChange={() => toggle(s.id)} />
              <span>{s.title}</span>
            </label>
          ))}
        </fieldset>
      ))}
      <div className="course-picker-actions">
        {custom && <button type="button" className="btn" onClick={reset}><RotateCcw size={13} aria-hidden /> Essentials</button>}
        <span className="spacer" />
        <button type="button" className="btn" onClick={onClose}>Cancel</button>
        <button type="button" className="btn btn-primary" onClick={save} disabled={!picked.size}><Check size={14} aria-hidden /> Save</button>
      </div>
    </div>
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
