'use client'

import { ApolloProvider } from '@apollo/client/react'
import { useEffect, type ReactNode } from 'react'
import { apolloClient } from '@/lib/apollo'
import { refreshSession } from '@/lib/auth/session'
import { useSession } from '@/state/session'

/** GraphQL for client pages, and the session restored from the refresh cookie on first load. */
export function AuthProvider({ children }: { children: ReactNode }) {
  const status = useSession((s) => s.status)
  useEffect(() => {
    if (status === 'unknown') void refreshSession()
  }, [status])
  return <ApolloProvider client={apolloClient()}>{children}</ApolloProvider>
}
