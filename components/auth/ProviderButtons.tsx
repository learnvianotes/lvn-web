'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { SignInOptionsDocument, SignInWithGoogleDocument } from '@/graphql/generated/graphql'
import { firebaseConfig } from '@/lib/env'
import { googleIdToken } from '@/lib/auth/google'
import { oauthAvailable, startOAuth } from '@/lib/auth/oauth'
import { useFinishSignIn } from './useFinishSignIn'


/**
 * Google, GitHub and LinkedIn — each shown only when both the API (signInOptions) and this deployment's
 * configuration offer it.
 */
export function ProviderButtons({ next }: { next?: string | null }) {
  const t = useTranslations('auth.providers')
  const { data } = useQuery(SignInOptionsDocument)
  const [google] = useMutation(SignInWithGoogleDocument)
  const finish = useFinishSignIn()
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const options = data?.signInOptions
  const show = {
    google: !!options?.google && !!firebaseConfig,
    github: !!options?.github && oauthAvailable('GITHUB'),
    linkedin: !!options?.linkedin && oauthAvailable('LINKEDIN'),
  }
  if (!show.google && !show.github && !show.linkedin) return null

  const withGoogle = async () => {
    setError(null)
    setBusy(true)
    try {
      const idToken = await googleIdToken()
      const { data: res } = await google({ variables: { idToken } })
      const payload = res?.signInWithGoogle
      if (!payload?.session) throw new Error(payload?.userErrors[0]?.message ?? t('failed'))
      await finish(payload.session, next)
    } catch (e) {
      setError(e instanceof Error && e.message ? e.message : t('failed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex flex-col gap-3">
      {error ? <Alert tone="error">{error}</Alert> : null}
      {show.google ? <Button variant="secondary" disabled={busy} onClick={withGoogle}>{t('google')}</Button> : null}
      {show.github ? <Button variant="secondary" onClick={() => void startOAuth('GITHUB', next ?? undefined)}>{t('github')}</Button> : null}
      {show.linkedin ? <Button variant="secondary" onClick={() => void startOAuth('LINKEDIN', next ?? undefined)}>{t('linkedin')}</Button> : null}
      <div className="flex items-center gap-3 text-xs text-muted" aria-hidden>
        <span className="h-px flex-1 bg-border" />
        {t('or')}
        <span className="h-px flex-1 bg-border" />
      </div>
    </div>
  )
}
