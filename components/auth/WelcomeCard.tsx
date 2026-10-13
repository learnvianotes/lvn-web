'use client'

import { Mail } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { legalLinks } from '@/features/legal/links'
import { Alert } from '@/components/ui/alert'
import { cn } from '@/lib/cn'
import { useSession } from '@/state/session'
import { GoogleButton } from './GoogleButton'
import { useGoogleSignIn } from './useGoogleSignIn'

const card = 'flex animate-rise flex-col gap-3 rounded-3xl bg-surface p-6 text-fg shadow-2xl shadow-black/30 [animation-delay:200ms] sm:p-7'

/**
 * The landing page's way in, like the mobile welcome sheet: Continue with Google first, then email sign-up and sign-in.
 * Without Google, email sign-up is the primary button. Someone already signed in gets their account instead.
 */
export function WelcomeCard() {
  const t = useTranslations('auth.welcome')
  const signedIn = useSession((s) => s.status === 'signed-in')
  const google = useGoogleSignIn()

  if (signedIn) {
    return (
      <div className={card}>
        <h2 className="text-xl font-bold tracking-tight">{t('signedInTitle')}</h2>
        <p className="text-sm text-muted">{t('signedInLead')}</p>
        <Link href="/home" className="mt-1 inline-flex h-12 items-center justify-center rounded-full bg-accent text-[15px] font-semibold text-accent-fg hover:opacity-90">
          {t('home')}
        </Link>
        <Link href="/profile" className="inline-flex h-11 items-center justify-center rounded-full border border-border text-sm font-semibold hover:bg-surface-2">
          {t('account')}
        </Link>
      </div>
    )
  }

  return (
    <div className={card}>
      <div className="mb-1 flex flex-col gap-1">
        <h2 className="text-xl font-bold tracking-tight">{t('sheetTitle')}</h2>
        <p className="text-sm text-muted">{t('sheetLead')}</p>
      </div>
      {google.error ? <Alert tone="error">{google.error}</Alert> : null}
      {google.available ? <GoogleButton busy={google.busy} onClick={() => void google.signIn()} /> : null}
      <Link
        href="/sign-up"
        className={cn(
          'inline-flex h-12 items-center justify-center gap-2.5 rounded-full text-[15px] font-semibold transition-colors',
          google.available ? 'border border-border bg-surface-2/60 hover:bg-surface-2' : 'bg-accent text-accent-fg hover:opacity-90',
        )}
      >
        <Mail className="size-[18px]" aria-hidden />
        {t('email')}
      </Link>
      <p className="pt-1 text-center text-sm text-muted">
        {t('haveAccount')}{' '}
        <Link href="/sign-in" className="font-semibold text-accent hover:underline">
          {t('signIn')}
        </Link>
      </p>
      <p className="text-center text-xs leading-5 text-muted">{t.rich('legal', legalLinks)}</p>
    </div>
  )
}
