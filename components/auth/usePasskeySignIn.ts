'use client'

import { useMutation } from '@apollo/client/react'
import { browserSupportsWebAuthn, startAuthentication } from '@simplewebauthn/browser'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { FinishPasskeySignInDocument, StartPasskeySignInDocument } from '@/graphql/generated/graphql'
import { refusalMessage } from '@/lib/limit-error'
import { useFinishSignIn } from './useFinishSignIn'

/**
 * Passkey sign-in (lvn-backend ADR-0115). The browser offers the passkeys it has for this site and asks for the screen
 * lock; only a signature leaves the device. `available` waits for mount so the server HTML matches the first render.
 */
export function usePasskeySignIn(next?: string | null) {
  const t = useTranslations('auth.signIn')
  const te = useTranslations('auth.errors')
  const [start] = useMutation(StartPasskeySignInDocument)
  const [finishPasskey] = useMutation(FinishPasskeySignInDocument)
  const finish = useFinishSignIn()
  const [available, setAvailable] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => setAvailable(browserSupportsWebAuthn()), [])

  const signIn = async () => {
    setBusy(true)
    setError(null)
    try {
      const { data } = await start()
      const begun = data?.startPasskeySignIn
      if (!begun) throw new Error('no options')
      let response
      try {
        response = await startAuthentication({ optionsJSON: JSON.parse(begun.optionsJson) })
      } catch {
        setError(t('passkeyCancelled'))
        return
      }
      const res = await finishPasskey({ variables: { input: { attemptId: begun.attemptId, responseJson: JSON.stringify(response) } } })
      const payload = res.data?.finishPasskeySignIn
      if (payload?.session) return void (await finish(payload.session, next, payload.mfaRequired))
      setError(payload?.userErrors[0]?.message ?? te('generic'))
    } catch (e) {
      setError(refusalMessage(e) ?? te('generic'))
    } finally {
      setBusy(false)
    }
  }

  return { available, busy, error, signIn }
}
