import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

/**
 * The night-sky brand surface (UI reference: dark hero cards for the moments that matter), shared with the mobile
 * welcome screen: midnight to indigo, with two soft lights for depth instead of an image. Content on it is white.
 */
export function NightSky({ as: Tag = 'div', className, children }: { as?: 'div' | 'section'; className?: string; children: ReactNode }) {
  return (
    <Tag className={cn('relative isolate overflow-hidden bg-[linear-gradient(160deg,#120F2E_0%,#2B2560_55%,#4F46E5_100%)] text-white', className)}>
      <span aria-hidden className="pointer-events-none absolute -right-24 -top-16 -z-10 size-72 rounded-full bg-[#818CF8]/20" />
      <span aria-hidden className="pointer-events-none absolute -bottom-24 -left-20 -z-10 size-64 rounded-full bg-white/5" />
      {children}
    </Tag>
  )
}
