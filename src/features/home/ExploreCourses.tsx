/* ============================================================
   ExploreCourses — upcoming courses (not yet live subjects),
   behind a centered "Explore more courses" button. Opened: area
   filter + course cards; signed-in learners can "Notify me"
   (recorded as interest — it tells us what to build next).
   ============================================================ */

import { useMemo, useState } from 'react'
import { Bell, BellRing, ChevronDown, Compass } from 'lucide-react'
import { upcomingAreas, type Course } from '@/features/catalog/courses'
import { SubjectIcon } from '@/features/catalog/SubjectIcon'
import { useUser } from '@/features/auth/auth'
import { toggleInterest, usePrefs } from '@/features/progress/prefs'
import { track } from '@/features/telemetry/track'

export function ExploreCourses({ live }: { live: Set<string> }) {
  const areas = useMemo(() => upcomingAreas(live), [live])
  const [open, setOpen] = useState(false)
  const [area, setArea] = useState('all')
  const total = areas.reduce((n, a) => n + a.courses.length, 0)
  if (!total) return null

  const shown = area === 'all' ? areas : areas.filter((a) => a.id === area)

  return (
    <section className={`explore ${open ? 'is-open' : ''}`} aria-label="Explore more courses">
      <div className="explore-toggle-wrap">
        <button className="explore-toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open} aria-controls="explore-list">
          <Compass size={16} aria-hidden />
          {open ? 'Hide upcoming courses' : 'Explore more courses'}
          <span className="explore-count">{total}</span>
          <ChevronDown size={15} aria-hidden className="explore-chevron" />
        </button>
        {!open && <p className="muted small">Programming languages, AI, architecture and more — coming soon.</p>}
      </div>

      {open && (
        <div id="explore-list" className="explore-list">
          <div className="filter-chips" role="tablist" aria-label="Course areas">
            <button role="tab" aria-selected={area === 'all'} className="filter-chip" onClick={() => setArea('all')}>
              All <span className="filter-count">{total}</span>
            </button>
            {areas.map((a) => (
              <button key={a.id} role="tab" aria-selected={area === a.id} className="filter-chip" onClick={() => setArea(a.id)}>
                <span aria-hidden>{a.emoji}</span> {a.title} <span className="filter-count">{a.courses.length}</span>
              </button>
            ))}
          </div>
          {shown.map((a) => (
            <div key={a.id} className="explore-area">
              {area === 'all' && <h3 className="explore-area-title"><span aria-hidden>{a.emoji}</span> {a.title}</h3>}
              <div className="card-grid">
                {a.courses.map((c) => <CourseCard key={c.id} course={c} />)}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}

function CourseIcon({ course }: { course: Course }) {
  if (course.badge) return <span className="lang-badge" style={{ '--lang': course.color } as React.CSSProperties}>{course.badge}</span>
  return <span className="subject-card-icon"><SubjectIcon name={course.icon ?? 'book'} size={20} /></span>
}

function CourseCard({ course }: { course: Course }) {
  const user = useUser()
  const prefs = usePrefs()
  const interested = prefs.interests.includes(course.id)
  const [pulse, setPulse] = useState(false)

  return (
    <div className="subject-card course-card is-soon">
      <div className="subject-card-top">
        <CourseIcon course={course} />
        <span className="soon-badge">Coming soon</span>
      </div>
      <h3 className="subject-card-title">{course.title}</h3>
      <p className="subject-card-desc">{course.description}</p>
      {user && (
        <button
          className={`btn btn-sm notify-btn ${interested ? 'is-on' : ''} ${pulse ? 'is-pulse' : ''}`}
          aria-pressed={interested}
          onClick={() => {
            const now = toggleInterest(course.id)
            track('course_interest', { i: course.id, v: now ? 1 : 0 })
            setPulse(true)
            window.setTimeout(() => setPulse(false), 500)
          }}
        >
          {interested ? <BellRing size={14} aria-hidden /> : <Bell size={14} aria-hidden />}
          {interested ? 'You’ll be notified' : 'Notify me'}
        </button>
      )}
    </div>
  )
}
