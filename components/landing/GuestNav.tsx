'use client'

import Link from 'next/link'
import { useSession } from '@/state/session'

/** Board A's header for visitors: Features, Subjects and Community from 768 px, and Get Started. */
export function GuestNav({ labels }: { labels: { features: string; subjects: string; community: string; start: string; guide: string } }) {
  // Shown until the session is known to be someone's: a visitor sees it at once.
  const signedIn = useSession((s) => s.status === 'signed-in')
  if (signedIn) return null
  const link = 'hidden whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg md:inline-flex'
  return (
    <>
      <Link href="/#features" className={link}>
        {labels.features}
      </Link>
      <Link href="/subjects" className={link}>
        {labels.subjects}
      </Link>
      <Link href="/community" className={link}>
        {labels.community}
      </Link>
      <Link href="/guide" className={link}>
        {labels.guide}
      </Link>
      <Link href="/sign-up" className="order-last hidden h-9 items-center whitespace-nowrap rounded-[10px] bg-accent px-4 text-sm font-semibold text-accent-fg hover:opacity-90 sm:inline-flex">
        {labels.start}
      </Link>
    </>
  )
}
