/**
 * First-party usage events (page views and product actions). They batch to the platform ingest endpoint.
 * No third-party script is loaded. Props are a short allow-list: no email, name, query text or free-form notes.
 * A person who opts out of analytics is not recorded. Errors keep flowing; that choice is separate.
 */
import type { ErrorEventInput, UsageEventInput } from '@/lib/platform-api'
import { ingestEvents, loadAnalyticsOptOut } from '@/lib/platform-api'
import { useSession } from '@/state/session'
import { installClientErrorListeners, setErrorSink, type ClientError } from './errors'

const FLUSH_MS = 5_000
const MAX_BATCH = 20
const BLOCKED_PROP = /email|name|handle|phone|token|password|query|message|reason|address|user|title|filename|fileName|content/i

export function pagePath(path: string): string {
  const clean = path.split(/[?#]/)[0] || '/'
  return (clean.startsWith('/') ? clean : `/${clean}`).slice(0, 200)
}

/** Props safe to leave the browser: short tokens, numbers and booleans. Everything else is dropped. */
export function usageProps(props: Record<string, unknown> | undefined): { key: string; value: string }[] {
  if (!props) return []
  const out: { key: string; value: string }[] = []
  for (const [key, value] of Object.entries(props)) {
    if (!/^[a-z][a-z0-9_]{0,31}$/i.test(key) || BLOCKED_PROP.test(key)) continue
    if (typeof value === 'boolean' || (typeof value === 'number' && Number.isFinite(value))) out.push({ key, value: String(value) })
    else if (typeof value === 'string' && value.length > 0 && value.length <= 40 && !value.includes('@') && !/[\s/]/.test(value)) out.push({ key, value })
  }
  return out
}

export type UsageSender = (batch: { usage: UsageEventInput[]; errors: ErrorEventInput[] }) => Promise<void>

export function createUsageTracker(deps: { send: UsageSender; signedIn: () => boolean; now?: () => string; path?: () => string }) {
  const now = deps.now ?? (() => new Date().toISOString())
  const path = deps.path ?? (() => (typeof location === 'undefined' ? '/' : pagePath(location.pathname)))
  let preference: 'unknown' | 'in' | 'out' = 'unknown'
  const usage: UsageEventInput[] = []
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
    const usageBatch = preference === 'in' ? usage.splice(0, MAX_BATCH) : []
    const errorBatch = errors.splice(0, MAX_BATCH)
    if (!usageBatch.length && !errorBatch.length) return
    sending = true
    try {
      await deps.send({ usage: usageBatch, errors: errorBatch })
    } catch {
      usage.unshift(...usageBatch)
      errors.unshift(...errorBatch)
    } finally {
      sending = false
      if (usage.length + errors.length) schedule()
    }
  }

  return {
    setPreference(optedOut: boolean) {
      preference = optedOut ? 'out' : 'in'
      if (optedOut) usage.length = 0
      else if (usage.length || errors.length) schedule()
    },
    preference: () => preference,
    track(name: string, props?: Record<string, unknown>) {
      if (preference === 'out') return
      if (!/^[a-z][a-z0-9_]{0,40}$/.test(name)) return
      usage.push({ name, at: now(), path: pagePath(path()), props: usageProps(props) })
      if (usage.length >= MAX_BATCH && preference === 'in') void flush()
      else if (preference === 'in') schedule()
    },
    report(event: ClientError) {
      errors.push({ type: event.type, message: event.message, route: event.route, stack: event.stack, at: event.at })
      if (errors.length >= MAX_BATCH) void flush()
      else schedule()
    },
    flush,
    pending: () => ({ usage: usage.length, errors: errors.length }),
  }
}

type Tracker = ReturnType<typeof createUsageTracker>
let tracker: Tracker | undefined

function shared(): Tracker {
  tracker ??= createUsageTracker({
    send: (batch) => ingestEvents(batch),
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
