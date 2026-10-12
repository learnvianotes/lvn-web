'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { useSession } from '@/state/session'
import { Discussion } from './Discussion'

/** A public note's discussion (lvn-backend ADR-0047): for signed-in readers; visitors are asked to sign in. */
export function PublicDiscussion({ noteId }: { noteId: string }) {
  return (
    <AuthProvider>
      <Inner noteId={noteId} />
    </AuthProvider>
  )
}

function Inner({ noteId }: { noteId: string }) {
  const t = useTranslations('discussion')
  const status = useSession((s) => s.status)
  const path = usePathname()
  if (status === 'signed-in') return <Discussion target={{ type: 'NOTE', id: noteId }} />
  if (status !== 'signed-out') return null
  return (
    <p className="rounded-3xl border border-border bg-surface px-5 py-4 text-sm text-muted">
      <Link href={`/sign-in?next=${encodeURIComponent(path)}`} className="font-semibold text-accent hover:underline">
        {t('signIn')}
      </Link>
    </p>
  )
}
