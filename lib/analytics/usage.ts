/**
 * First-party usage events (page views and product actions). They batch to the platform ingest endpoint.
 * No third-party script is loaded. Props are a short allow-list: no email, name, query text or free-form notes.
 * A person who opts out of analytics is not recorded. Errors keep flowing; that choice is separate.
 */
import type { ErrorEventInput, UsageEventInput } from '@/lib/platform-api'
import { USAGE_EVENT_NAMES, ingestAnalytics, loadAnalyticsOptOut } from '@/lib/platform-api'
import { useSession } from '@/state/session'
import { installClientErrorListeners, setErrorSink, type ClientError } from './errors'

const FLUSH_MS = 5_000
const MAX_BATCH = 20
const BLOCKED_PROP = /email|name|handle|phone|token|password|query|message|reason|address|user|title|filename|fileName|content/i

export function pagePath(path: string): string {
  const clean = path.split(/[?#]/)[0] || '/'
  return (clean.startsWith('/') ? clean : `/${clean}`).slice(0, 200)
}

const ALLOWED_EVENTS = new Set<string>(USAGE_EVENT_NAMES)

/** Props safe to leave the browser: a JSON object of short tokens, numbers and booleans. Everything else is dropped. */
export function usageProps(props: Record<string, unknown> | undefined): Record<string, string | number | boolean> {
  const out: Record<string, string | number | boolean> = {}
  if (!props) return out
  for (const [key, value] of Object.entries(props)) {
    if (!/^[a-z][a-z0-9_]{0,31}$/i.test(key) || BLOCKED_PROP.test(key)) continue
    if (typeof value === 'boolean' || (typeof value === 'number' && Number.isFinite(value))) out[key] = value
    else if (typeof value === 'string' && value.length > 0 && value.length <= 40 && !value.includes('@') && !/[\s/]/.test(value)) out[key] = value
  }
  return out
}

export type UsageSender = (batch: { events: UsageEventInput[]; errors: ErrorEventInput[] }) => Promise<void>

export function createUsageTracker(deps: { send: UsageSender; signedIn: () => boolean; now?: () => string }) {
  const now = deps.now ?? (() => new Date().toISOString())
  let preference: 'unknown' | 'in' | 'out' = 'unknown'
  const events: UsageEventInput[] = []
  const errors: ErrorEventInput[] = []
  let timer: ReturnType<typeof setTimeout> | null = null
  let sending = false

  const schedule = () => {
    if (timer || sending) return
    timer = setTimeout(() => void flush(), FLUSH_MS)
  }

  const flush = async () => {
    if (timer) clearTimeout(timer)
    timer = null
    if (sending || !deps.signedIn()) return
    const eventBatch = preference === 'in' ? events.splice(0, MAX_BATCH) : []
    const errorBatch = errors.splice(0, MAX_BATCH)
    if (!eventBatch.length && !errorBatch.length) return
    sending = true
    try {
      await deps.send({ events: eventBatch, errors: errorBatch })
    } catch {
      events.unshift(...eventBatch)
      errors.unshift(...errorBatch)
    } finally {
      sending = false
      if (events.length + errors.length) schedule()
    }
  }

  return {
    setPreference(optedOut: boolean) {
      preference = optedOut ? 'out' : 'in'
      if (optedOut) events.length = 0
      else if (events.length || errors.length) schedule()
    },
    preference: () => preference,
    track(name: string, props?: Record<string, unknown>) {
      if (preference === 'out') return
      if (!ALLOWED_EVENTS.has(name)) return
      events.push({ name, platform: 'WEB', occurredAt: now(), props: usageProps(props) })
      if (events.length >= MAX_BATCH && preference === 'in') void flush()
      else if (preference === 'in') schedule()
    },
    report(event: ClientError) {
      errors.push({ code: event.type, message: event.message, platform: 'WEB', route: event.route, occurredAt: event.at })
      if (errors.length >= MAX_BATCH) void flush()
      else schedule()
    },
    flush,
    pending: () => ({ usage: events.length, errors: errors.length }),
  }
}

type Tracker = ReturnType<typeof createUsageTracker>
let tracker: Tracker | undefined

function shared(): Tracker {
  tracker ??= createUsageTracker({
    send: (batch) => ingestAnalytics(batch),
    signedIn: () => useSession.getState().status === 'signed-in',
  })
  return tracker
}

/** Records one product action. Dropped when the person has opted out, or before that choice is known and then discarded. */
export function trackUsage(name: string, props?: Record<string, unknown>): void {
  shared().track(name, props)
}

/** The profile switch calls this so collection stops before the next batch. */
export function setUsageOptOut(optedOut: boolean): void {
  shared().setPreference(optedOut)
}

let started = false

/** Loads the opt-out, listens for crashes, and flushes on a timer and when the tab hides. Idempotent. */
export function startUsageTracking(): void {
  if (started || typeof window === 'undefined') return
  started = true
  const current = shared()
  setErrorSink((event) => current.report(event))
  installClientErrorListeners()
  void loadAnalyticsOptOut()
    .then((optedOut) => current.setPreference(optedOut))
    .catch(() => current.setPreference(true))
  const flush = () => void current.flush()
  window.addEventListener('pagehide', flush)
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') flush()
  })
  useSession.subscribe((state, prev) => {
    if (state.status === 'signed-in' && prev.status !== 'signed-in') flush()
  })
}
