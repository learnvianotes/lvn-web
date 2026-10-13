'use client'

import { LEARNING_LIMITS, type LearningEventInput } from '@/lib/contracts/validation/learning'
import type { LearningEventType } from '@/lib/contracts/domain/enums'
import { newId } from '@/lib/ids'
import { SetLearningTimeZoneDocument, TrackEventsDocument } from '@/graphql/generated/graphql'
import { apolloClient } from '@/lib/apollo'
import { useSession } from '@/state/session'

/**
 * Learning events from the web (lvn-backend ADR-0067): the one way components report what a person did. Events wait in
 * `localStorage` (they survive a reload and being offline) and go to `trackEvents` every 10 s, at 20 events, when the
 * connection returns, and when the page is hidden. Only for a signed-in person; dropped at sign-out.
 */
const KEY = 'lvn.learning.queue'
const SESSION = typeof crypto !== 'undefined' ? newId() : 'server'

type Fields = Partial<Pick<LearningEventInput, 'entityType' | 'entityId' | 'topicKeys' | 'durationMs' | 'metadata'>>

let queue: LearningEventInput[] | null = null
let timer: ReturnType<typeof setTimeout> | null = null
let sending = false
let listening = false

function load(): LearningEventInput[] {
  if (queue) return queue
  try {
    queue = JSON.parse(localStorage.getItem(KEY) ?? '[]') as LearningEventInput[]
  } catch {
    queue = []
  }
  return queue
}

function save() {
  try {
    localStorage.setItem(KEY, JSON.stringify(queue ?? []))
  } catch {
    // Storage full or blocked: the events stay in memory until sent.
  }
}

function listen() {
  if (listening || typeof window === 'undefined') return
  listening = true
  window.addEventListener('online', () => void flush())
  document.addEventListener('visibilitychange', () => document.visibilityState === 'hidden' && void flush({ keepalive: true }))
  // Sign-out drops what was not sent: it was the previous person's.
  useSession.subscribe((s, before) => {
    if (s.status === 'signed-out' && before.status === 'signed-in') clear()
    if (s.status === 'signed-in' && before.status !== 'signed-in') void flush()
  })
}

let zoneTold: string | null = null

/**
 * Tells the server the browser's time zone once someone is signed in, not only with the first batch of events: a new
 * account's days and exam countdowns are in their zone from the first page (ADR-0067, ADR-0070). Once per zone.
 */
export async function tellTimeZone(): Promise<void> {
  if (typeof window === 'undefined' || useSession.getState().status !== 'signed-in') return
  const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
  if (!timeZone || zoneTold === timeZone) return
  zoneTold = timeZone
  try {
    await apolloClient().mutate({ mutation: SetLearningTimeZoneDocument, variables: { input: { timeZone } } })
  } catch {
    zoneTold = null
  }
}

/** Records one learning event (types and fields: §14.1, ADR-0067). Nothing is recorded signed out. */
export function track(type: LearningEventType, fields: Fields = {}): void {
  if (typeof window === 'undefined' || useSession.getState().status !== 'signed-in') return
  listen()
  const q = load()
  q.push({ id: newId(), type, ...fields, clientTs: new Date().toISOString(), sessionId: SESSION, platform: 'WEB' })
  // While offline for long, the oldest go first.
  if (q.length > LEARNING_LIMITS.queued) q.splice(0, q.length - LEARNING_LIMITS.queued)
  save()
  if (q.length >= LEARNING_LIMITS.flushEvery) void flush()
  else timer ??= setTimeout(() => void flush(), LEARNING_LIMITS.flushSeconds * 1000)
}

/** Sends what is waiting, a batch at a time. Kept for later when offline or refused for now. */
export async function flush(options: { keepalive?: boolean } = {}): Promise<void> {
  if (timer) clearTimeout(timer)
  timer = null
  if (sending || !load().length || useSession.getState().status !== 'signed-in' || (typeof navigator !== 'undefined' && !navigator.onLine)) return
  sending = true
  try {
    for (let waiting = load(); waiting.length; waiting = load()) {
      const batch = waiting.slice(0, LEARNING_LIMITS.batch)
      const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone
      const res = await apolloClient().mutate({ mutation: TrackEventsDocument, variables: { input: { events: batch, timeZone } }, context: { fetchOptions: { keepalive: options.keepalive } } })
      const answer = res.data?.trackEvents
      // A refused batch (rate limit) is tried again later; a refused event never will be accepted, so it goes too.
      if (!answer || answer.userErrors.length) break
      const sent = new Set(batch.map((e) => e.id))
      queue = waiting.filter((e) => !sent.has(e.id))
      save()
    }
  } catch {
    // Offline or the API is away: kept for the next try.
  } finally {
    sending = false
    if (load().length) timer ??= setTimeout(() => void flush(), LEARNING_LIMITS.flushSeconds * 1000)
  }
}

/** What waits to be sent (tests, and sign-out). */
export function pending(): readonly LearningEventInput[] {
  return load()
}

export function clear(): void {
  queue = []
  save()
}
