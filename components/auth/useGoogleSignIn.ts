'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { SignInOptionsDocument, SignInWithGoogleDocument } from '@/graphql/generated/graphql'
import { ageHoldFromProblems, type AgeHold } from '@/lib/age-hold'
import { googleIdToken, googleRedirectIdToken, rememberGoogleNext, takeGoogleNext } from '@/lib/auth/google'
import { firebaseConfig } from '@/lib/env'
import { refusalMessage } from '@/lib/limit-error'
import { useFinishSignIn } from './useFinishSignIn'

/** One redirect return per page load, even if several buttons mount (React strict mode included). */
let redirectHandled = false

/**
 * Google sign-in for any page (lvn-backend ADR-0007), offered when the API (`signInOptions.google`) and this
 * deployment both have it. One click opens Google's popup, or a full-page redirect when the popup is blocked.
 * A returning account goes on to `next` (or Home), a new one to its details, including the age check.
 */
export function useGoogleSignIn(next?: string | null) {
  const t = useTranslations('auth.providers')
  const { data } = useQuery(SignInOptionsDocument)
  const [exchange] = useMutation(SignInWithGoogleDocument)
  const finish = useFinishSignIn()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [hold, setHold] = useState<AgeHold | null>(null)

  const complete = async (idToken: string, destination: string | null | undefined) => {
    const { data: res } = await exchange({ variables: { idToken } })
    const payload = res?.signInWithGoogle
    const ageHold = ageHoldFromProblems(payload?.userErrors)
    if (ageHold) return setHold(ageHold)
    // The API's messages are written for people; Firebase's and the network's are not.
    const blocked = payload?.userErrors.find((problem) => problem.code === 'FORBIDDEN')
    if (!payload?.session) return setError(blocked?.message ?? payload?.userErrors[0]?.message ?? t('failed'))
    await finish(payload.session, destination)
  }

  useEffect(() => {
    if (redirectHandled) return
    redirectHandled = true
    void (async () => {
      let idToken: string | null
      try {
        idToken = await googleRedirectIdToken()
      } catch (error) {
        setError(refusalMessage(error) ?? t('failed'))
        return
      }
      if (!idToken) return
      const stored = takeGoogleNext()
      setBusy(true)
      try {
        await complete(idToken, stored ?? next)
      } catch (error) {
        setError(refusalMessage(error) ?? t('failed'))
      } finally {
        setBusy(false)
      }
    })()
    // The redirect is consumed once, on the first mount of this page load.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const signIn = async () => {
    setError(null)
    setHold(null)
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
    } catch (error) {
      rememberGoogleNext(null)
      setError(refusalMessage(error) ?? t('failed'))
    } finally {
      setBusy(false)
    }
  }

  return { available: !!data?.signInOptions.google && !!firebaseConfig, busy, error, hold, signIn }
}
