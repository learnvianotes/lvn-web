'use client'

import { useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { SignInOptionsDocument } from '@/graphql/generated/graphql'
import { oauthAvailable, startOAuth } from '@/lib/auth/oauth'
import { GoogleButton } from './GoogleButton'
import { useGoogleSignIn } from './useGoogleSignIn'

/**
 * Google first, then GitHub and LinkedIn. Google shows when an admin has left it on and this deployment has Firebase.
 * GitHub and LinkedIn show when both the API (signInOptions) and this deployment's configuration offer them.
 */
export function ProviderButtons({ next }: { next?: string | null }) {
  const t = useTranslations('auth.providers')
  const google = useGoogleSignIn(next)
  const { data } = useQuery(SignInOptionsDocument)
  const options = data?.signInOptions
  const show = { github: !!options?.github && oauthAvailable('GITHUB'), linkedin: !!options?.linkedin && oauthAvailable('LINKEDIN') }
  if (!google.available && !show.github && !show.linkedin) return null

  return (
    <div className="flex flex-col gap-3">
      {google.error ? <Alert tone="error">{google.error}</Alert> : null}
      {google.available ? <GoogleButton busy={google.busy} onClick={() => void google.signIn()} /> : null}
      {show.github ? <Button variant="secondary" disabled={google.busy} onClick={() => void startOAuth('GITHUB', next ?? undefined)}>{t('github')}</Button> : null}
      {show.linkedin ? <Button variant="secondary" disabled={google.busy} onClick={() => void startOAuth('LINKEDIN', next ?? undefined)}>{t('linkedin')}</Button> : null}
      <div className="flex items-center gap-3 text-xs text-muted" aria-hidden>
        <span className="h-px flex-1 bg-border" />
        {t('or')}
        <span className="h-px flex-1 bg-border" />
      </div>
    </div>
  )
}
