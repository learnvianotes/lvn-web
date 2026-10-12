'use client'

import { NotebookPen, UserRound } from 'lucide-react'
import Link from 'next/link'
import { useSession } from '@/state/session'

/** "Sign in", or the visitor's notes and account once this tab knows they are signed in. */
export function AccountLink({ labels }: { labels: { signIn: string; account: string; notes: string; community: string } }) {
  const signedIn = useSession((s) => s.status === 'signed-in')
  return (
    <>
      {signedIn ? (
        <Link href="/community" className="hidden whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg md:inline-flex">
          {labels.community}
        </Link>
      ) : null}
      {signedIn ? (
        <Link href="/notes" aria-label={labels.notes} className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-lg px-2 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg sm:px-3">
          <NotebookPen className="size-4 sm:hidden" aria-hidden />
          <span className="hidden sm:inline">{labels.notes}</span>
        </Link>
      ) : null}
      <Link href={signedIn ? '/profile' : '/sign-in'} aria-label={signedIn ? labels.account : undefined} className="inline-flex items-center gap-1.5 whitespace-nowrap rounded-lg px-2 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg sm:px-3">
        {signedIn ? (
          <>
            <UserRound className="size-4 sm:hidden" aria-hidden />
            <span className="hidden sm:inline">{labels.account}</span>
          </>
        ) : (
          labels.signIn
        )}
      </Link>
    </>
  )
}
