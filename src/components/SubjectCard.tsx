import { forwardRef } from 'react'
import { Link } from 'react-router-dom'
import type { SubjectProgress } from '@/progress/stats'
import { SubjectIcon } from './SubjectIcon'

interface Props {
  to: string
  icon?: string
  title: string
  description?: string
  countLabel: string
  progress: Pick<SubjectProgress, 'done' | 'total' | 'ratio'>
  highlighted?: boolean
}

/** Card used for subjects (landing page) and Sheet 150 categories. */
export const SubjectCard = forwardRef<HTMLAnchorElement, Props>(function SubjectCard(
  { to, icon, title, description, countLabel, progress, highlighted },
  ref,
) {
  return (
    <Link ref={ref} to={to} className={`subject-card ${highlighted ? 'is-highlighted' : ''}`}>
      <div className="subject-card-top">
        {icon && <span className="subject-card-icon"><SubjectIcon name={icon} size={20} /></span>}
        <span className="subject-card-count">{countLabel}</span>
      </div>
      <h3 className="subject-card-title">{title}</h3>
      {description && <p className="subject-card-desc">{description}</p>}
      <div className="subject-card-progress">
        <span className="bar" aria-hidden><span style={{ width: `${progress.ratio * 100}%` }} /></span>
        <span className="muted">{progress.done}/{progress.total}</span>
      </div>
    </Link>
  )
})
