'use client'

import { useApolloClient } from '@apollo/client/react'
import { useRouter } from 'next/navigation'
import { useCallback } from 'react'
import { trackUsage } from '@/lib/analytics'
import { afterSignIn } from '@/lib/auth/destination'
import { adminVerifyPath, isAdminMfaRole, noteSessionMfa } from '@/lib/auth/mfa'
import { signedIn } from '@/lib/auth/session'

type FinishedSession = {
  accessToken: string
  accessTokenExpiresAt: string
  user: { registrationComplete: boolean; globalRole?: string | null }
}

/**
 * Stores the new session, forgets any cached data of a previous user, and moves on.
 * An admin or staff account that still needs a code goes to the email screen first. Anyone else never sees it.
 */
export function useFinishSignIn() {
  const client = useApolloClient()
  const router = useRouter()
  return useCallback(
    async (session: FinishedSession, next?: string | null, mfaRequired?: boolean | null) => {
      signedIn(session.accessToken, session.accessTokenExpiresAt)
      const needsCode = mfaRequired === true && isAdminMfaRole(session.user.globalRole)
      noteSessionMfa(session.user.globalRole, needsCode)
      trackUsage('sign_in')
      await client.clearStore()
      const dest = afterSignIn(session.user, next)
      router.replace(needsCode ? adminVerifyPath(dest) : dest)
    },
    [client, router],
  )
}
