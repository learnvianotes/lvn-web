'use client'

import { ApolloProvider } from '@apollo/client/react'
import { useEffect, type ReactNode } from 'react'
import { AdminMfaRedirect } from '@/components/auth/AdminMfaRedirect'
import { apolloClient } from '@/lib/apollo'
import { refreshSession } from '@/lib/auth/session'
import { tellTimeZone } from '@/lib/learning'
import { useSession } from '@/state/session'

/** GraphQL for client pages, and the session restored from the refresh cookie on first load. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const status = useSession((s) => s.status)
  useEffect(() => {
    if (status === 'unknown') void refreshSession()
    if (status === 'signed-in') void tellTimeZone()
  }, [status])
  return (
    <ApolloProvider client={apolloClient()}>
      <AdminMfaRedirect />
      {children}
    </ApolloProvider>
  )
}
