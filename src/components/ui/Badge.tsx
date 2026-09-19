/* ============================================================
   Badge — C-NOTE UI Primitive
   Small status/category indicator.
   ============================================================ */

import type { ReactNode } from 'react'
import type { Difficulty } from '@/types'

export type BadgeVariant =
  | 'default'
  | 'accent'
  | 'success'
  | 'warning'
  | 'danger'
  | 'info'
  | 'difficulty-easy'
  | 'difficulty-medium'
  | 'difficulty-hard'

interface BadgeProps {
  children: ReactNode
  variant?: BadgeVariant
  className?: string
}

/** Map difficulty values to badge variants */
export function difficultyVariant(d: Difficulty): BadgeVariant {
  return `difficulty-${d}` as BadgeVariant
}

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
  return (
    <span className={`badge badge--${variant} ${className}`}>
      {children}
    </span>
  )
}
