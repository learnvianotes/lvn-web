'use client'

import { createClient, type Client } from 'graphql-ws'
import { useEffect, useRef } from 'react'
import { refreshSession } from '@/lib/auth/session'
import { liveEvent, type LiveEvent } from '@/lib/contracts/notifications'
import { liveUrl } from '@/lib/env'
import { useSession } from '@/state/session'

/** A live event, or RECONNECTED: the socket was down for a while, so whatever it would have said may have happened. */
export type LiveSignal = LiveEvent | { kind: 'RECONNECTED' }
type Listener = (signal: LiveSignal) => void

const listeners = new Set<Listener>()
let client: Client | null = null
let unsubscribe: (() => void) | null = null
let connectedBefore = false

/** The access token for a new socket: refreshed first when it has less than half a minute left. */
async function freshToken(): Promise<string | null> {
  const { accessToken, expiresAt } = useSession.getState()
  if (accessToken && expiresAt && expiresAt - Date.now() > 30_000) return accessToken
  return (await refreshSession()) ? useSession.getState().accessToken : null
}

const emit = (signal: LiveSignal) => listeners.forEach((l) => l(signal))

function open(url: string) {
  connectedBefore = false
  client = createClient({
    url,
    // The token is fetched for every connection, so a reconnect after expiry (closed with 4403) uses a fresh one.
    connectionParams: async () => {
      const token = await freshToken()
      return token ? { authorization: `Bearer ${token}` } : {}
    },
    retryAttempts: Infinity,
    shouldRetry: () => true,
    retryWait: (retries) => new Promise((resolve) => setTimeout(resolve, Math.min(30_000, 1000 * 2 ** retries) + Math.random() * 1000)),
    on: {
      connected: () => {
        if (connectedBefore) emit({ kind: 'RECONNECTED' })
        connectedBefore = true
      },
    },
  })
  unsubscribe = client.subscribe(
    { query: 'subscription Live { live { kind id at } }' },
    {
      next: ({ data }) => {
        const parsed = liveEvent.safeParse((data as { live?: unknown } | null | undefined)?.live)
        if (parsed.success) emit(parsed.data)
      },
      // The client retries on its own; nothing to show for a dropped socket.
      error: () => undefined,
      complete: () => undefined,
    },
  )
}

function close() {
  unsubscribe?.()
  unsubscribe = null
  void client?.dispose()
  client = null
}

/**
 * Live updates over lvn-backend's graphql-ws endpoint (ADR-0042): one socket per tab, opened while something listens
 * and the viewer is signed in. Events say only "something changed"; listeners refetch through the API.
 */
export function subscribeLive(listener: Listener): () => void {
  listeners.add(listener)
  if (listeners.size === 1 && liveUrl) open(liveUrl)
  return () => {
    listeners.delete(listener)
    if (!listeners.size) close()
  }
}

/** Calls `onSignal` for every live event while mounted; the latest callback is used without resubscribing. */
export function useLive(onSignal: Listener, enabled = true): void {
  const latest = useRef(onSignal)
  useEffect(() => {
    latest.current = onSignal
  })
  useEffect(() => {
    if (!enabled) return
    return subscribeLive((s) => latest.current(s))
  }, [enabled])
}
