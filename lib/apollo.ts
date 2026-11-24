'use client'

import { ApolloClient, HttpLink, InMemoryCache } from '@apollo/client'
import { apiProblem, reportClientError } from '@/lib/analytics'
import { isAdminMfaRole } from '@/lib/auth/mfa'
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

function errorParts(err: unknown): { name: string; message: string } {
  if (typeof err === 'string') return { name: '', message: err }
  if (typeof err !== 'object' || err === null) return { name: '', message: '' }
  return {
    name: 'name' in err && typeof err.name === 'string' ? err.name : '',
    message: 'message' in err && typeof err.message === 'string' ? err.message : '',
  }
}

/** Chromium, Firefox, and the DOM abort a fetch with one of these when nothing was wrong with the network. */
const ABORTED = /signal is aborted without reason|user aborted a request|operation was aborted/i

/**
 * Apollo's HttpLink calls `abort()` with no reason when a query unsubscribes (navigation, unmount, refetch).
 * That cancellation is not a failed request. A timeout is, including the session check, which aborts with TimeoutError.
 */
export function isIntentionalAbort(err: unknown): boolean {
  const { name, message } = errorParts(err)
  if (name === 'TimeoutError' || /timeout/i.test(message)) return false
  return name === 'AbortError' || ABORTED.test(message)
}

const isUnauthenticated = (body: { errors?: { extensions?: { code?: string } }[] }) => body.errors?.some((e) => e.extensions?.code === 'UNAUTHENTICATED') ?? false

/** An admin tool refused to run until the emailed code is entered. Opt-in MFA for anyone else stays quiet. */
function noticeAdminMfa(body: { errors?: { extensions?: { code?: string } }[] }): void {
  const codes = new Set(body.errors?.map((error) => error.extensions?.code).filter((code): code is string => Boolean(code)))
  if (codes.has('ADMIN_MFA_REQUIRED') || (codes.has('MFA_REQUIRED') && isAdminMfaRole(useSession.getState().role))) {
    useSession.setState({ mfaPending: true, mfaVerified: false })
  }
}

/**
 * Sends the access token, and when the API answers UNAUTHENTICATED to a request that carried one (it expired or the
 * session was revoked), refreshes once and retries. Cookies are included so refreshSession can rotate the cookie.
 */
export const authFetch: typeof fetch = async (input, init) => {
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
    if (!isIntentionalAbort(error)) {
      reportClientError({
        type: 'api.network',
        message: error instanceof Error ? error.message : 'network',
        stack: error instanceof Error ? error.stack : null,
        route: operation,
      })
    }
    throw error
  }
  const body = await res.clone().json().catch(() => ({}))
  const problem = apiProblem(res.status, body, operation)
  if (problem) reportClientError({ type: 'api', message: problem })
  noticeAdminMfa(body)
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
