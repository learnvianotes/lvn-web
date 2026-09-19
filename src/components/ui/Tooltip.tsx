/* ============================================================
   Tooltip — C-NOTE UI Primitive
   Simple CSS-powered tooltip using title-style semantics.
   For Phase 1: renders via data-tooltip attribute.
   A full accessible tooltip (role=tooltip + aria-describedby)
   can be introduced when interaction complexity demands it.
   ============================================================ */

import type { ReactElement, ReactNode } from 'react'
import { cloneElement } from 'react'

interface TooltipProps {
  content: string
  children: ReactElement
  position?: 'top' | 'bottom' | 'left' | 'right'
}

export function Tooltip({ content, children, position = 'top' }: TooltipProps) {
  // Attach data attributes to trigger element; CSS handles display
  return cloneElement(children as ReactElement<Record<string, unknown>>, {
    'data-tooltip': content,
    'data-tooltip-position': position,
    className: [
      (children as ReactElement<{ className?: string }>).props.className ?? '',
      'tooltip-trigger',
    ]
      .filter(Boolean)
      .join(' '),
  } as Record<string, unknown>)
}

/** Wrapper that renders tooltip content node (for Design System demo) */
export function TooltipDemo({ children }: { children: ReactNode }) {
  return <>{children}</>
}
