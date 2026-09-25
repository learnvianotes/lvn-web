/* ============================================================
   DifficultyBadge — Sheet 150
   Renders a colored badge for Easy / Medium / Hard.
   Reuses existing .badge CSS classes from components.css.
   ============================================================ */

import type { Sheet150Difficulty } from '@/types/sheet150'

interface DifficultyBadgeProps {
  difficulty: Sheet150Difficulty
}

const VARIANT_MAP: Record<Sheet150Difficulty, string> = {
  Easy:   'badge--difficulty-easy',
  Medium: 'badge--difficulty-medium',
  Hard:   'badge--difficulty-hard',
}

export function DifficultyBadge({ difficulty }: DifficultyBadgeProps) {
  return (
    <span className={`badge ${VARIANT_MAP[difficulty]}`}>
      {difficulty}
    </span>
  )
}
