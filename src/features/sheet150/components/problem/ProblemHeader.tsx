/* ============================================================
   ProblemHeader — Sheet 150
   Renders the title row: problem number, title, difficulty
   badge, and an external LeetCode link.
   ============================================================ */

import { ExternalLink } from 'lucide-react'
import { DifficultyBadge } from '../DifficultyBadge'
import type { Sheet150Problem } from '@/types/sheet150'

interface ProblemHeaderProps {
  problem: Pick<Sheet150Problem, 'lcNumber' | 'title' | 'difficulty' | 'category' | 'tags' | 'leetcodeUrl'>
}

/** Converts a category slug to a readable label, e.g. "arrays-hashing" → "Arrays & Hashing" */
function categoryLabel(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
    .replace('And', '&')
}

export function ProblemHeader({ problem }: ProblemHeaderProps) {
  return (
    <div className="s150-problem-header">
      {/* LC number + title */}
      <div className="s150-problem-header__title-row">
        <span className="s150-problem-header__lc-num">#{problem.lcNumber}</span>
        <h1 className="s150-problem-header__title">{problem.title}</h1>
      </div>

      {/* Meta row: difficulty + category + LeetCode link */}
      <div className="s150-problem-header__meta">
        <DifficultyBadge difficulty={problem.difficulty} />

        <span className="s150-problem-header__category">
          {categoryLabel(problem.category)}
        </span>

        {problem.tags && problem.tags.length > 0 && (
          <div className="s150-problem-header__tags">
            {problem.tags.map((tag) => (
              <span key={tag} className="s150-tag">{tag}</span>
            ))}
          </div>
        )}

        {problem.leetcodeUrl && (
          <a
            href={problem.leetcodeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="s150-problem-header__lc-link"
            aria-label={`Open ${problem.title} on LeetCode`}
          >
            LeetCode
            <ExternalLink size={12} aria-hidden="true" />
          </a>
        )}
      </div>
    </div>
  )
}
