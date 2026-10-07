import { forwardRef } from 'react'
import { Link } from 'react-router-dom'
import type { SubjectProgress } from '@core/features/progress/stats'
import { SubjectIcon } from '@core/features/catalog/SubjectIcon'

interface Props {
  to: string
  icon?: string
  title: string
  description?: string
  countLabel: string
  /** omitted for guests (progress is a signed-in feature) */
  progress?: Pick<SubjectProgress, 'done' | 'total' | 'ratio'>
  highlighted?: boolean
  /** small label next to the count, e.g. "Live" */
  badge?: string
  /** landing-page category id — tints the icon (see home.css) */
  category?: string
}

/** Card used for subjects (landing page) and Sheet 150 categories. */
export const SubjectCard = forwardRef<HTMLAnchorElement, Props>(function SubjectCard(
  { to, icon, title, description, countLabel, progress, highlighted, badge, category },
  ref,
) {
  return (
    <Link ref={ref} to={to} className={`subject-card ${highlighted ? 'is-highlighted' : ''}`} data-cat={category}>
      <div className="subject-card-top">
        {icon && <span className="subject-card-icon"><SubjectIcon name={icon} size={20} /></span>}
        <span className="subject-card-count">
          {badge && <span className="live-badge">{badge}</span>}
          {countLabel}
        </span>
      </div>
      <h3 className="subject-card-title">{title}</h3>
      {description && <p className="subject-card-desc">{description}</p>}
      {progress && (
        <div className="subject-card-progress">
          <span className="bar" aria-hidden><span style={{ width: `${progress.ratio * 100}%` }} /></span>
          <span className="muted">{progress.done}/{progress.total}</span>
        </div>
      )}
    </Link>
  )
})
