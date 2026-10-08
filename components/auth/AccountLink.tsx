'use client'

import Link from 'next/link'
import { useSession } from '@/state/session'

/** "Sign in", or "Your account" once this tab knows the visitor is signed in. */
export function AccountLink({ labels }: { labels: { signIn: string; account: string } }) {
  const signedIn = useSession((s) => s.status === 'signed-in')
  return (
    <Link href={signedIn ? '/profile' : '/sign-in'} className="whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg">
      {signedIn ? labels.account : labels.signIn}
    </Link>
  )
}
