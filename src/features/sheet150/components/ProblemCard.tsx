/* ============================================================
   ProblemCard — Sheet 150
   A single problem row card displayed on the category listing
   page. Clicking navigates to /sheet-150/problems/:slug.
   ============================================================ */

import { Link } from 'react-router-dom'
import { ArrowRight } from 'lucide-react'
import { DifficultyBadge } from './DifficultyBadge'
import type { Sheet150Problem } from '@/types/sheet150'

interface ProblemCardProps {
  problem: Pick<Sheet150Problem, 'slug' | 'lcNumber' | 'title' | 'difficulty' | 'tags'>
}

export function ProblemCard({ problem }: ProblemCardProps) {
  return (
    <Link
      to={`/sheet-150/problems/${problem.slug}`}
      className="s150-problem-card"
      aria-label={`${problem.title} — ${problem.difficulty}`}
    >
      <span className="s150-problem-card__num">#{problem.lcNumber}</span>

      <div className="s150-problem-card__body">
        <span className="s150-problem-card__title">{problem.title}</span>
        {problem.tags && problem.tags.length > 0 && (
          <div className="s150-problem-card__tags">
            {problem.tags.slice(0, 3).map((tag) => (
              <span key={tag} className="s150-tag s150-tag--sm">{tag}</span>
            ))}
          </div>
        )}
      </div>

      <div className="s150-problem-card__right">
        <DifficultyBadge difficulty={problem.difficulty} />
        <ArrowRight size={14} aria-hidden="true" className="s150-problem-card__arrow" />
      </div>
    </Link>
  )
}
