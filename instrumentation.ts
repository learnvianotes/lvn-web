import type { Instrumentation } from 'next'

/**
 * Server and Edge error reporting (§16.5), on only when NEXT_PUBLIC_SENTRY_DSN is set. Sentry is imported lazily so a
 * build without a DSN carries none of it.
 */
const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN

export async function register(): Promise<void> {
  if (!dsn) return
  const [Sentry, { sentryOptions }] = await Promise.all([import('@sentry/nextjs'), import('./lib/observability')])
  Sentry.init({
    ...sentryOptions(dsn, process.env.NEXT_PUBLIC_APP_ENV ?? 'development', process.env.NEXT_PUBLIC_APP_VERSION),
    // `dataCollection` already refuses local variables and source lines. These integrations are the ones that would
    // attach them, plus console breadcrumbs, if a future default turned the categories back on.
    integrations: (defaults) => defaults.filter((i) => !['LocalVariables', 'LocalVariablesAsync', 'ContextLines', 'Console'].includes(i.name)),
  })
}

/** Errors thrown while rendering or in route handlers. */
export const onRequestError: Instrumentation.onRequestError = async (...args) => {
  if (!dsn) return
  const Sentry = await import('@sentry/nextjs')
  Sentry.captureRequestError(...args)
}
