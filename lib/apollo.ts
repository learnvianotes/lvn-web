'use client'

import { ApolloClient, HttpLink, InMemoryCache } from '@apollo/client'
import { apiProblem, reportClientError } from '@/lib/analytics'
import { env } from '@/lib/env'
import { useSession } from '@/state/session'
import { refreshSession } from './auth/session'

function operationName(init?: RequestInit): string | undefined {
  if (typeof init?.body !== 'string') return undefined
  try {
    return (JSON.parse(init.body) as { operationName?: string }).operationName
  } catch {
    return undefined
  }
}

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
  const operation = operationName(init)
  let res: Response
  try {
    res = await send(token)
  } catch (error) {
    reportClientError({ type: 'api.network', message: error instanceof Error ? error.message : 'network' })
    throw error
  }
  const body = await res.clone().json().catch(() => ({}))
  const problem = apiProblem(res.status, body, operation)
  if (problem) reportClientError({ type: 'api', message: problem })
  if (!token || !isUnauthenticated(body)) return res
  return (await refreshSession()) ? send(useSession.getState().accessToken) : res
}

let client: ApolloClient | undefined

/** One client per tab. */
export function apolloClient(): ApolloClient {
  client ??= new ApolloClient({
    link: new HttpLink({ uri: env.NEXT_PUBLIC_API_URL, fetch: authFetch }),
    // A quiz choice's id is unique only within its question, so choices are kept inside their question, not by id.
    // A profile has no id: queries that read different parts of it merge them rather than replace each other.
    cache: new InMemoryCache({ typePolicies: { ClassQuizChoice: { keyFields: false }, StudentProfile: { merge: true } } }),
    defaultOptions: { watchQuery: { fetchPolicy: 'cache-and-network' } },
  })
  return client
}
