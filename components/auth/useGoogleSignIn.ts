'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { SignInOptionsDocument, SignInWithGoogleDocument } from '@/graphql/generated/graphql'
import { googleIdToken } from '@/lib/auth/google'
import { firebaseConfig } from '@/lib/env'
import { useFinishSignIn } from './useFinishSignIn'

/**
 * Google sign-in for any page (lvn-backend ADR-0007), offered when the API and this deployment both have it. One click
 * opens Google's popup; a returning account goes on to `next` (or its profile), a new one to its details.
 */
export function useGoogleSignIn(next?: string | null) {
  const t = useTranslations('auth.providers')
  const { data } = useQuery(SignInOptionsDocument)
  const [exchange] = useMutation(SignInWithGoogleDocument)
  const finish = useFinishSignIn()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const signIn = async () => {
    setError(null)
    setBusy(true)
    try {
      const idToken = await googleIdToken()
      if (!idToken) return
      const { data: res } = await exchange({ variables: { idToken } })
      const payload = res?.signInWithGoogle
      // The API's messages are written for people; Firebase's and the network's are not.
      if (!payload?.session) return setError(payload?.userErrors[0]?.message ?? t('failed'))
      await finish(payload.session, next)
    } catch {
      setError(t('failed'))
    } finally {
      setBusy(false)
    }
  }

  return { available: !!data?.signInOptions.google && !!firebaseConfig, busy, error, signIn }
}
