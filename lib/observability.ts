import type { Breadcrumb, ErrorEvent } from '@sentry/nextjs'

/**
 * Header and query keys Sentry 10 used to drop when `sendDefaultPii` was off. v11 collects them unless named here.
 */
const SENSITIVE_KEYS = ['forwarded', '-ip', 'remote-', 'via', '-user']

/**
 * Sentry options shared by the browser, Node and Edge runtimes (§16.5): unexpected errors only — no performance
 * tracing, no session replay, no personal data. Query strings are removed everywhere because emailed links carry
 * tokens in them (/verify?token=, /reset?token=).
 *
 * v11 removed `sendDefaultPii`. An unset `dataCollection` collects user info, cookies, request bodies, database
 * values and local variables. These categories stay off, which is what `sendDefaultPii: false` and
 * `includeLocalVariables: false` did on v10. `beforeSend` still strips anything that arrives on the event.
 */
export function sentryOptions(dsn: string, environment: string, release?: string) {
  return {
    dsn,
    environment,
    release,
    dataCollection: {
      userInfo: false,
      cookies: false,
      httpHeaders: {
        request: { deny: SENSITIVE_KEYS },
        response: { deny: SENSITIVE_KEYS },
      },
      httpBodies: [],
      urlQueryParams: false,
      genAI: { inputs: false, outputs: false },
      mcp: { inputs: false, outputs: false },
      databaseQueryData: false,
      queues: false,
      graphQL: { document: false, variables: false },
      // Local variable values and the source lines around a frame can carry personal data or secrets.
      stackFrameVariables: false,
      frameContextLines: 0,
    },
    beforeSend: scrubEvent,
    beforeBreadcrumb: scrubBreadcrumb,
  }
}

const KEPT_HEADERS = new Set(['user-agent', 'content-type', 'x-request-id'])
const withoutQuery = (url: unknown) => (typeof url === 'string' ? url.split(/[?#]/)[0] : url)

export function scrubEvent<E extends ErrorEvent>(event: E): E {
  delete event.user
  if (event.request) {
    delete event.request.cookies
    delete event.request.data
    delete event.request.query_string
    event.request.url = withoutQuery(event.request.url) as string | undefined
    if (event.request.headers) {
      event.request.headers = Object.fromEntries(Object.entries(event.request.headers).filter(([k]) => KEPT_HEADERS.has(k.toLowerCase())))
    }
  }
  if (event.breadcrumbs) event.breadcrumbs = event.breadcrumbs.map(scrubBreadcrumb).filter((b): b is Breadcrumb => b !== null)
  return event
}

/** Console output is dropped; URLs keep their path only; UI breadcrumbs keep the element, never typed text. */
export function scrubBreadcrumb(crumb: Breadcrumb): Breadcrumb | null {
  if (crumb.category === 'console') return null
  if (!crumb.data) return crumb
  const data: Record<string, unknown> = { ...crumb.data }
  for (const key of ['url', 'from', 'to']) if (key in data) data[key] = withoutQuery(data[key])
  return { ...crumb, data }
}
