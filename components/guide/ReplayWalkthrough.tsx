'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { requestWalkthrough } from '@/lib/walkthrough'
import { useSession } from '@/state/session'

/** Opens the tour in the signed-in shell, or sends a visitor through sign-in and back to Home with the tour. */
export function ReplayWalkthrough({ label }: { label: string }) {
  const signedIn = useSession((s) => s.status === 'signed-in')
  if (signedIn) {
    return (
      <Button type="button" variant="secondary" onClick={() => requestWalkthrough()}>
        {label}
      </Button>
    )
  }
  return (
    <Button asChild variant="secondary">
      <Link href={`/sign-in?next=${encodeURIComponent('/home?tour=1')}`}>{label}</Link>
    </Button>
  )
}
