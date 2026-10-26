'use client'

import Link from 'next/link'
import type { ReactNode } from 'react'
import { useSession } from '@/state/session'

/**
 * The wordmark's destination: the marketing home for a visitor, the app home once this tab knows they are signed in.
 * Session starts unknown, so the first paint matches the server (`/`) and updates without a hydration mismatch.
 */
export function HomeLink({ children, className, label }: { children: ReactNode; className?: string; label: string }) {
  const signedIn = useSession((s) => s.status === 'signed-in')
  return (
    <Link href={signedIn ? '/home' : '/'} aria-label={label} className={className}>
      {children}
    </Link>
  )
}
