'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { AuthSettingsDocument, SignInOptionsDocument, SignInWithGoogleDocument } from '@/graphql/generated/graphql'
import { googleIdToken, googleRedirectIdToken, rememberGoogleNext, takeGoogleNext } from '@/lib/auth/google'
import { googleButtonVisible } from '@/lib/auth/unified'
import { firebaseConfig } from '@/lib/env'
import { useFinishSignIn } from './useFinishSignIn'

/** One redirect return per page load, even if several buttons mount (React strict mode included). */
let redirectHandled = false

/**
 * Google sign-in for any page (lvn-backend ADR-0007). Offered when an admin has left it on (authSettings) and this
 * deployment has Firebase. One click opens Google's popup, or a redirect where popups are blocked. A returning
 * account goes on to `next` (or its profile); a new one still has to finish registration, including the age check.
 */
export function useGoogleSignIn(next?: string | null) {
  const t = useTranslations('auth.providers')
  const settings = useQuery(AuthSettingsDocument)
  const options = useQuery(SignInOptionsDocument)
  const [exchange] = useMutation(SignInWithGoogleDocument)
  const finish = useFinishSignIn()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const complete = async (idToken: string, destination: string | null | undefined) => {
    const { data: res } = await exchange({ variables: { idToken } })
    const payload = res?.signInWithGoogle
    // The API's messages are written for people ("Google sign-in is not available here."); Firebase's are not.
    if (!payload?.session) {
      setError(payload?.userErrors[0]?.message ?? t('failed'))
      return
    }
    await finish(payload.session, destination)
  }

  useEffect(() => {
    if (redirectHandled) return
    redirectHandled = true
    void (async () => {
      let idToken: string | null
      try {
        idToken = await googleRedirectIdToken()
      } catch {
        return
      }
      if (!idToken) return
      const stored = takeGoogleNext()
      setBusy(true)
      try {
        await complete(idToken, stored ?? next)
      } catch {
        setError(t('failed'))
      } finally {
        setBusy(false)
      }
    })()
    // The redirect is consumed once, on the first mount of this page load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const signIn = async () => {
    setError(null)
    setBusy(true)
    try {
      rememberGoogleNext(next)
      const attempt = await googleIdToken()
      if (attempt.status === 'redirecting') return
      if (attempt.status === 'cancelled') {
        rememberGoogleNext(null)
        return
      }
      rememberGoogleNext(null)
      await complete(attempt.idToken, next)
    } catch {
      rememberGoogleNext(null)
      setError(t('failed'))
    } finally {
      setBusy(false)
    }
  }

  return {
    available: googleButtonVisible({
      firebaseConfigured: !!firebaseConfig,
      googleSignInEnabled: settings.data?.authSettings.googleSignInEnabled,
      signInOptionsGoogle: options.data?.signInOptions.google,
      authSettingsFailed: !!settings.error && !settings.data,
    }),
    busy,
    error,
    signIn,
  }
}
