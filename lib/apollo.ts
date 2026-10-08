'use client'

import { ApolloClient, HttpLink, InMemoryCache } from '@apollo/client'
import { env } from '@/lib/env'
import { useSession } from '@/state/session'
import { refreshSession } from './auth/session'

const isUnauthenticated = (body: { errors?: { extensions?: { code?: string } }[] }) => body.errors?.some((e) => e.extensions?.code === 'UNAUTHENTICATED') ?? false

/**
 * Sends the access token, and when the API answers UNAUTHENTICATED to a request that carried one (it expired or the
 * session was revoked), refreshes once and retries. Cookies are included so refreshSession can rotate the cookie.
 */
const authFetch: typeof fetch = async (input, init) => {
  const send = (token: string | null) => {
    const headers = new Headers(init?.headers)
    if (token) headers.set('authorization', `Bearer ${token}`)
    return fetch(input, { ...init, headers, credentials: 'include' })
  }
  const token = useSession.getState().accessToken
  const res = await send(token)
  if (!token) return res
  const body = await res.clone().json().catch(() => ({}))
  if (!isUnauthenticated(body)) return res
  return (await refreshSession()) ? send(useSession.getState().accessToken) : res
}

let client: ApolloClient | undefined

/** One client per tab. */
export function apolloClient(): ApolloClient {
  client ??= new ApolloClient({
    link: new HttpLink({ uri: env.NEXT_PUBLIC_API_URL, fetch: authFetch }),
    cache: new InMemoryCache(),
    defaultOptions: { watchQuery: { fetchPolicy: 'cache-and-network' } },
  })
  return client
}
