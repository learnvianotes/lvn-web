/**
 * Client errors for the platform error log and for Sentry. Messages are scrubbed of email addresses. Window errors
 * go to the log only: when Sentry is on, its own handler already records them. Handled failures (uploads, API) are
 * sent to both, because nothing else reports them.
 */

export type ClientError = {
  type: string
  message: string
  route: string | null
  stack: string | null
  at: string
}

const EMAIL = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi
const SKIP_OPS = new Set(['IngestEvents', 'AnalyticsOptOut', 'Refresh'])
const SKIP_CODES = new Set(['UNAUTHENTICATED', 'FORBIDDEN', 'VALIDATION', 'BAD_USER_INPUT', 'RATE_LIMITED', 'NOT_FOUND'])

let sink: (event: ClientError) => void = () => undefined

/** Where captured errors are queued. The usage tracker registers this so one ingest call carries both. */
export function setErrorSink(fn: (event: ClientError) => void): void {
  sink = fn
}

export function scrubText(text: string, max = 500): string {
  return text.replace(EMAIL, '[email]').replace(/\s+/g, ' ').trim().slice(0, max)
}

export function reportClientError(input: { type: string; message: string; route?: string | null; stack?: string | null; at?: string }, sentry = true): void {
  const event: ClientError = {
    type: scrubText(input.type, 80),
    message: scrubText(input.message),
    route: input.route?.split(/[?#]/)[0]?.slice(0, 200) || null,
    stack: input.stack ? scrubText(input.stack, 2000) : null,
    at: input.at ?? new Date().toISOString(),
  }
  if (!event.type || !event.message) return
  sink(event)
  if (sentry) void sendToSentry(event)
}

/** An unexpected API failure worth logging, or null for auth, validation and the ingest call itself. */
export function apiProblem(status: number, body: unknown, operation?: string): string | null {
  if (operation && SKIP_OPS.has(operation)) return null
  if (status >= 500) return `API request failed (${status})`
  const errors = (body as { errors?: { message?: string; extensions?: { code?: string } }[] } | null)?.errors
  if (!errors?.length) return null
  const unexpected = errors.filter((e) => !SKIP_CODES.has(String(e.extensions?.code ?? '')))
  if (!unexpected.length) return null
  return scrubText(unexpected[0]?.message || 'API error')
}

type ErrorTarget = Pick<Window, 'addEventListener' | 'removeEventListener'> & { location?: { pathname?: string } }

/** `window.onerror` and unhandled promise rejections. Returns the unsubscribe. Sentry records these on its own. */
export function installClientErrorListeners(target: ErrorTarget = window): () => void {
  const onError = (event: Event) => {
    const e = event as ErrorEvent
    reportClientError({ type: 'window.onerror', message: e.message || 'Script error', stack: e.error instanceof Error ? e.error.stack : null, route: target.location?.pathname }, false)
  }
  const onReject = (event: Event) => {
    const e = event as PromiseRejectionEvent
    const reason = e.reason
    const message = reason instanceof Error ? reason.message : typeof reason === 'string' ? reason : 'Unhandled rejection'
    reportClientError({ type: 'unhandledrejection', message, stack: reason instanceof Error ? reason.stack : null, route: target.location?.pathname }, false)
  }
  target.addEventListener('error', onError)
  target.addEventListener('unhandledrejection', onReject)
  return () => {
    target.removeEventListener('error', onError)
    target.removeEventListener('unhandledrejection', onReject)
  }
}

async function sendToSentry(event: ClientError): Promise<void> {
  if (!process.env.NEXT_PUBLIC_SENTRY_DSN) return
  try {
    const Sentry = await import('@sentry/nextjs')
    const error = new Error(event.message)
    error.name = event.type
    if (event.stack) error.stack = event.stack
    Sentry.captureException(error, { tags: { error_type: event.type }, extra: event.route ? { route: event.route } : undefined })
  } catch {
    // Sentry is optional. The platform log still has the error.
  }
}
