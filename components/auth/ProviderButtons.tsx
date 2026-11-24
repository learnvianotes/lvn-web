'use client'

import { useTranslations } from 'next-intl'
import { useEffect } from 'react'
import { Alert } from '@/components/ui/alert'
import type { AgeHold } from '@/lib/age-hold'
import { GoogleButton } from './GoogleButton'
import { useGoogleSignIn } from './useGoogleSignIn'

/**
 * Google sign-in, when this deployment offers it. GitHub and LinkedIn sign-in are retired (lvn-backend ADR-0115).
 * `divider` draws the "or" rule under it, for forms that do not draw their own.
 */
export function ProviderButtons({ next, onAgeHold, divider = true }: { next?: string | null; onAgeHold?: (hold: AgeHold) => void; divider?: boolean }) {
  const t = useTranslations('auth.providers')
  const google = useGoogleSignIn(next)
  useEffect(() => {
    if (google.hold) onAgeHold?.(google.hold)
  }, [google.hold, onAgeHold])
  if (!google.available) return null

  return (
    <div className="flex flex-col gap-3">
      {google.error ? <Alert tone="error">{google.error}</Alert> : null}
      <GoogleButton busy={google.busy} onClick={() => void google.signIn()} />
      {divider ? (
        <div className="flex items-center gap-3 text-xs text-muted" aria-hidden>
          <span className="h-px flex-1 bg-border" />
          {t('or')}
          <span className="h-px flex-1 bg-border" />
        </div>
      ) : null}
    </div>
  )
}
