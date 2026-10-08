'use client'

import { env } from '@/lib/env'
import { useSession } from '@/state/session'

/** Refresh a minute before the access token expires. */
const EARLY_MS = 60_000
let timer: ReturnType<typeof setTimeout> | undefined
let inFlight: Promise<boolean> | null = null

const REFRESH = 'mutation { refreshSession(input: {}) { session { accessToken accessTokenExpiresAt } } }'

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
    try {
      const res = await acrossTabs(() => fetch(env.NEXT_PUBLIC_API_URL, {
        method: 'POST',
        credentials: 'include',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ query: REFRESH }),
      }))
      const body = (await res.json()) as { data?: { refreshSession?: { session?: { accessToken: string; accessTokenExpiresAt: string } } } }
      const s = body.data?.refreshSession?.session
      if (!s) {
        signedOut()
        return false
      }
      signedIn(s.accessToken, s.accessTokenExpiresAt)
      return true
    } catch {
      // Offline or the API is down: keep whatever we had; the next request retries.
      return useSession.getState().status === 'signed-in'
    } finally {
      inFlight = null
    }
  })()
  return inFlight
}

/** Stores a fresh access token and schedules its refresh. */
export function signedIn(accessToken: string, expiresAt: string): void {
  useSession.getState().set(accessToken, expiresAt)
  clearTimeout(timer)
  timer = setTimeout(() => void refreshSession(), Math.max(5_000, Date.parse(expiresAt) - Date.now() - EARLY_MS))
}

export function signedOut(): void {
  clearTimeout(timer)
  useSession.getState().clear()
}
