'use client'

import { SIGNED_IN_HINT_KEY } from '@/lib/auth/hint'
import { noteSessionMfa } from '@/lib/auth/mfa'
import { env } from '@/lib/env'
import { useSession } from '@/state/session'

/** Refresh a minute before the access token expires. */
const EARLY_MS = 60_000
/** How long the first session check waits before the app says the API did not answer. */
export const SESSION_CHECK_MS = 8_000
let timer: ReturnType<typeof setTimeout> | undefined
let inFlight: Promise<boolean> | null = null

const REFRESH_MFA = 'mutation { refreshSession(input: {}) { mfaRequired session { accessToken accessTokenExpiresAt user { globalRole } } } }'
const REFRESH = 'mutation { refreshSession(input: {}) { session { accessToken accessTokenExpiresAt } } }'

type RefreshBody = {
  data?: {
    refreshSession?: {
      mfaRequired?: boolean | null
      session?: { accessToken: string; accessTokenExpiresAt: string; user?: { globalRole?: string | null } | null } | null
    } | null
  }
  errors?: { message?: string }[]
}

/** The API this web build is talking to does not have the MFA fields yet. */
function missingMfaField(body: RefreshBody): boolean {
  return body.errors?.some((error) => /Cannot query field "(mfaRequired|mfaFactors)"/.test(error.message ?? '')) ?? false
}

/** Runs `fn` while holding a lock shared by every tab of this site (Web Locks API, where available). */
const acrossTabs = <T>(fn: () => Promise<T>): Promise<T> =>
  typeof navigator !== 'undefined' && navigator.locks ? (navigator.locks.request('lvn-refresh-session', fn) as Promise<T>) : fn()

/**
 * Exchanges the refresh cookie for a new access token. One refresh at a time — in this tab (single-flight) and
 * across tabs (a lock): the API rotates the refresh token on every use and treats a reused one as theft (§7.1), so
 * a second tab must wait and then refresh with the cookie the first one received.
 */
export function refreshSession(): Promise<boolean> {
  inFlight ??= (async () => {
    // A sign-in that lands while this request is open (the OAuth callback, another tab) stores a newer token.
    // The empty restore must not wipe that token: it only describes the cookie this request saw.
    const tokenAtStart = useSession.getState().accessToken
    const attempt = new AbortController()
    // TimeoutError, not a bare abort: Apollo cancels queries the same way, and those are not network failures.
    const attemptTimer = setTimeout(() => attempt.abort(new DOMException('session-check timeout', 'TimeoutError')), SESSION_CHECK_MS)
    try {
      const post = (query: string) =>
        acrossTabs(() => fetch(env.NEXT_PUBLIC_API_URL, {
          method: 'POST',
          credentials: 'include',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({ query }),
          signal: attempt.signal,
        }))
      let res = await post(REFRESH_MFA)
      let body = (await res.json()) as RefreshBody
      let mfaKnown = true
      if (missingMfaField(body)) {
        mfaKnown = false
        res = await post(REFRESH)
        body = (await res.json()) as RefreshBody
      }
      const payload = body.data?.refreshSession
      const s = payload?.session
      if (!s) {
        if (useSession.getState().accessToken === tokenAtStart) signedOut()
        return false
      }
      signedIn(s.accessToken, s.accessTokenExpiresAt)
      noteSessionMfa(s.user?.globalRole, mfaKnown && payload?.mfaRequired === true)
      return true
    } catch {
      // Offline or the API is down. A person already signed in keeps that session; the first check says so instead of a blank page.
      const state = useSession.getState()
      if (state.status === 'unknown') state.markUnreachable()
      return useSession.getState().status === 'signed-in'
    } finally {
      clearTimeout(attemptTimer)
      inFlight = null
    }
  })()
  return inFlight
}

/** Stores a fresh access token and schedules its refresh. */
export function signedIn(accessToken: string, expiresAt: string): void {
  useSession.getState().set(accessToken, expiresAt)
  setSignedInHint(true)
  clearTimeout(timer)
  timer = setTimeout(() => void refreshSession(), Math.max(5_000, Date.parse(expiresAt) - Date.now() - EARLY_MS))
}

export function signedOut(): void {
  clearTimeout(timer)
  useSession.getState().clear()
  setSignedInHint(false)
}

/** Remember or forget the landing-page hint. It is not the session; losing it only allows one flash of `/`. */
function setSignedInHint(on: boolean): void {
  try {
    if (on) localStorage.setItem(SIGNED_IN_HINT_KEY, '1')
    else localStorage.removeItem(SIGNED_IN_HINT_KEY)
  } catch {
    // Private mode, or no window. The session itself does not depend on the hint.
  }
}

/** Ask for the session again after the API could not be reached. */
export function retrySession(): Promise<boolean> {
  useSession.setState({ status: 'unknown', accessToken: null, expiresAt: null })
  return refreshSession()
}
