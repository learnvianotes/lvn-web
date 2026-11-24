'use client'

import { create } from 'zustand'

/**
 * The signed-in session of this tab (§7.1): the access token lives only in memory; the refresh token is an HttpOnly
 * cookie the browser sends to the API and scripts never see.
 */
export interface SessionState {
  status: 'unknown' | 'signed-in' | 'signed-out' | 'unreachable'
  accessToken: string | null
  expiresAt: number | null
  /** Last known global role, so a later admin error can tell an admin from everyone else. */
  role: string | null
  /** An admin or staff session still needs the emailed code. Never set for any other role. */
  mfaPending: boolean
  /** This tab already accepted a code. A slower status response must not ask again. */
  mfaVerified: boolean
  set(accessToken: string, expiresAt: string): void
  clear(): void
  /** The first session check could not reach the API. Signed-in state is left alone. */
  markUnreachable(): void
}

export const useSession = create<SessionState>((set) => ({
  status: 'unknown',
  accessToken: null,
  expiresAt: null,
  role: null,
  mfaPending: false,
  mfaVerified: false,
  set: (accessToken, expiresAt) => set({ status: 'signed-in', accessToken, expiresAt: Date.parse(expiresAt) }),
  clear: () => set({ status: 'signed-out', accessToken: null, expiresAt: null, role: null, mfaPending: false, mfaVerified: false }),
  markUnreachable: () => set({ status: 'unreachable', accessToken: null, expiresAt: null }),
}))
