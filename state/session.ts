'use client'

import { create } from 'zustand'

/**
 * The signed-in session of this tab (§7.1): the access token lives only in memory; the refresh token is an HttpOnly
 * cookie the browser sends to the API and scripts never see.
 */
export interface SessionState {
  status: 'unknown' | 'signed-in' | 'signed-out'
  accessToken: string | null
  expiresAt: number | null
  set(accessToken: string, expiresAt: string): void
  clear(): void
}

export const useSession = create<SessionState>((set) => ({
  status: 'unknown',
  accessToken: null,
  expiresAt: null,
  set: (accessToken, expiresAt) => set({ status: 'signed-in', accessToken, expiresAt: Date.parse(expiresAt) }),
  clear: () => set({ status: 'signed-out', accessToken: null, expiresAt: null }),
}))
