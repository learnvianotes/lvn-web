/* ============================================================
   TRACK — the learner activity log behind future analytics and
   recommendations (schema: EventBatchDoc in schema/firestore.ts).

   • Only while signed in; nothing is recorded for guests.
   • Events are queued and written as one document per batch
     (every 30 s, at 50 events, when the tab is hidden and before
     sign-out) — a few writes per session instead of hundreds.
   • Failed batches are kept and retried with the next flush.

   Usage:  track('topic_complete', { s: subjectId, k: topicId })
   ============================================================ */

import { EVENT_BATCH_MAX, type EventBatchDoc, type EventType, type StudyEvent } from '@schema/firestore'
import { getAuthState, onBeforeSignOut, subscribeAuth } from '@/features/auth/auth'
import { dayKey } from '@/shared/lib/date'
import { userData } from '@/services/userdata/repository'

const FLUSH_EVERY_MS = 30_000
const FLUSH_AT = 50
const MAX_QUEUE = 500
const RETRY_MS = 60_000

let uid: string | null = null
let queue: StudyEvent[] = []
let timer = 0
let flushing: Promise<void> | null = null
const session = Math.random().toString(36).slice(2, 10) + Date.now().toString(36)

export function track(type: EventType, fields: Omit<StudyEvent, 't' | 'type'> = {}) {
  if (!uid) return
  const e: StudyEvent = { t: Date.now(), type }
  if (fields.s) e.s = fields.s.slice(0, 80)
  if (fields.k) e.k = fields.k.slice(0, 120)
  if (fields.i) e.i = fields.i.slice(0, 200)
  if (typeof fields.v === 'number' && Number.isFinite(fields.v)) e.v = Math.round(fields.v)
  if (fields.l) e.l = fields.l.slice(0, 80)
  queue.push(e)
  if (queue.length > MAX_QUEUE) queue = queue.slice(-MAX_QUEUE)
  if (queue.length >= FLUSH_AT) void flush()
  else if (!timer) timer = window.setTimeout(() => void flush(), FLUSH_EVERY_MS)
}

function platform() {
  const ua = navigator.userAgent
  const os = ua.match(/(iPhone|iPad|Android|Mac OS X|Windows|Linux|CrOS)/)?.[0] ?? 'other'
  const standalone = window.matchMedia('(display-mode: standalone)').matches
  return `${os}${standalone ? ' · app' : ''}`
}

export function flush(): Promise<void> {
  window.clearTimeout(timer)
  timer = 0
  const id = uid
  if (!id || !queue.length) return Promise.resolve()
  if (flushing) return flushing
  const events = queue.slice(0, EVENT_BATCH_MAX)
  queue = queue.slice(events.length)
  const batch: EventBatchDoc = {
    day: dayKey(),
    createdAt: Date.now(),
    session,
    client: { app: import.meta.env.VITE_APP_VERSION ?? 'web', platform: platform(), width: window.innerWidth },
    events,
  }
  flushing = userData()
    .then((r) => r.appendEvents(id, batch))
    .then(
      () => {
        flushing = null
        if (queue.length) return flush() // more than one batch was waiting
      },
      () => {
        flushing = null
        // Keep the events and try again later — never retry in a tight loop.
        if (uid === id) {
          queue = [...events, ...queue].slice(-MAX_QUEUE)
          timer = window.setTimeout(() => void flush(), RETRY_MS)
        }
      },
    )
  return flushing
}

export function initTracking() {
  subscribeAuth(() => {
    const s = getAuthState()
    const next = s.status === 'signed-in' ? s.user.uid : null
    if (next === uid) return
    if (!next) queue = []
    uid = next
    if (uid) track('session_start', { v: window.innerWidth })
  })
  onBeforeSignOut(() => flush())
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') void flush() })
}
