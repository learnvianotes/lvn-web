'use client'

import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { GoogleButton } from '@/components/auth/GoogleButton'
import { useGoogleSignIn } from '@/components/auth/useGoogleSignIn'
import { Alert } from '@/components/ui/alert'
import { legalLinks } from '@/features/legal/links'
import { useSession } from '@/state/session'

/** The hero's way in (board A): Get Started Free, Google when the environment has it, and sign-in; or Home when signed in. */
export function HeroActions() {
  return (
    <AuthProvider>
      <Actions />
    </AuthProvider>
  )
}

function Actions() {
  const t = useTranslations('home.hero')
  const tw = useTranslations('auth.welcome')
  const signedIn = useSession((s) => s.status === 'signed-in')
  const google = useGoogleSignIn()
  if (signedIn) {
    return (
      <div className="flex flex-wrap gap-3">
        <Link href="/home" className="inline-flex h-12 items-center rounded-full bg-accent px-6 text-[15px] font-semibold text-accent-fg hover:bg-[var(--accent-hover)]">
          {t('openHome')}
        </Link>
        <Link href="/profile" className="inline-flex h-12 items-center rounded-full border border-border bg-surface px-6 text-[15px] font-semibold text-fg hover:bg-surface-2">
          {t('account')}
        </Link>
      </div>
    )
  }
  return (
    <div className="flex flex-col gap-3">
      {google.error ? <Alert tone="error">{google.error}</Alert> : null}
      <div className="flex flex-wrap items-center gap-3">
        <Link href="/sign-up" className="inline-flex h-12 items-center rounded-full bg-accent px-6 text-[15px] font-semibold text-accent-fg hover:bg-[var(--accent-hover)]">
          {t('start')}
        </Link>
        {google.available ? (
          <div className="w-64">
            <GoogleButton busy={google.busy} onClick={() => void google.signIn()} />
          </div>
        ) : null}
      </div>
      <p className="text-sm text-muted">
        {t('haveAccount')}{' '}
        <Link href="/sign-in" className="font-semibold text-accent hover:underline">
          {t('signIn')}
        </Link>
      </p>
      {google.available ? <p className="max-w-md text-xs leading-5 text-muted">{tw.rich('legal', legalLinks)}</p> : null}
    </div>
  )
}
