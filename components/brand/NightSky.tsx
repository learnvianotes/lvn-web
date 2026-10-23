import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

/**
 * The night-sky brand surface (UI reference: dark hero cards for the moments that matter), shared with the mobile
 * welcome screen: midnight to blue, with two soft lights for depth instead of an image. Content on it is white.
 */
export function NightSky({ as: Tag = 'div', className, children }: { as?: 'div' | 'section'; className?: string; children: ReactNode }) {
  return (
    <Tag className={cn('relative isolate overflow-hidden bg-inverse text-inverse-ink', className)}>
      <span aria-hidden className="pointer-events-none absolute inset-x-0 top-0 h-1 bg-accent" />
      {children}
    </Tag>
  )
}
