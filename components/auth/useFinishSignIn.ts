'use client'

import { useApolloClient } from '@apollo/client/react'
import { useRouter } from 'next/navigation'
import { useCallback } from 'react'
import { trackUsage } from '@/lib/analytics'
import { afterSignIn } from '@/lib/auth/destination'
import { signedIn } from '@/lib/auth/session'

/** Stores the new session, forgets any cached data of a previous user, and moves on. */
export function useFinishSignIn() {
  const client = useApolloClient()
  const router = useRouter()
  return useCallback(
    async (session: { accessToken: string; accessTokenExpiresAt: string; user: { registrationComplete: boolean } }, next?: string | null) => {
      signedIn(session.accessToken, session.accessTokenExpiresAt)
      trackUsage('sign_in')
      await client.clearStore()
      router.replace(afterSignIn(session.user, next))
    },
    [client, router],
  )
}
