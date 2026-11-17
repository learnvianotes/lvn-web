'use client'

import { useMutation } from '@apollo/client/react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { OAuthExchangeDocument } from '@/graphql/generated/graphql'
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { redirectUri, takeOAuthAttempt } from '@/lib/auth/oauth'
import { AgeBlocked } from './AgeBlocked'
import { useFinishSignIn } from './useFinishSignIn'

/** The provider redirects here with a one-time code; the API exchanges it with this tab's PKCE verifier. */
export function OAuthCallback() {
  const t = useTranslations('auth.callback')
  const params = useSearchParams()
  const [exchange] = useMutation(OAuthExchangeDocument)
  const finish = useFinishSignIn()
  const [failed, setFailed] = useState<string | null>(null)
  const [hold, setHold] = useState<AgeHold | null>(null)
  const started = useRef(false)

  useEffect(() => {
    if (started.current) return
    started.current = true
    const attempt = takeOAuthAttempt(params.get('state'))
    const code = params.get('code')
    if (!attempt || !code || params.get('error')) {
      setFailed(t('failed'))
      return
    }
    void exchange({ variables: { input: { provider: attempt.provider, code, codeVerifier: attempt.verifier, redirectUri: redirectUri() } } })
      .then(({ data }) => {
        const payload = data?.oauthExchange
        const ageHold = ageHoldFromProblems(payload?.userErrors)
        if (ageHold) return setHold(ageHold)
        if (payload?.session) return finish(payload.session, attempt.next, payload.mfaRequired)
        setFailed(payload?.userErrors[0]?.message ?? t('failed'))
      })
      .catch(() => setFailed(t('failed')))
  }, [params, exchange, finish, t])

  if (hold) return <AgeBlocked supportEmail={hold.supportEmail} kind={hold.kind} />
  if (!failed) return <p role="status" className="text-sm text-muted">{t('working')}</p>
  return (
    <div className="flex flex-col gap-4">
      <Alert tone="error">{failed}</Alert>
      <Button asChild variant="secondary"><Link href="/sign-in">{t('back')}</Link></Button>
    </div>
  )
}
