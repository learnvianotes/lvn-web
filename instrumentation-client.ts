/**
 * Browser error reporting (§16.5), on only when NEXT_PUBLIC_SENTRY_DSN is set: the SDK is a separate chunk fetched
 * after start-up, so pages — /core included — load exactly as before without a DSN.
 */
const dsn = process.env.NEXT_PUBLIC_SENTRY_DSN

if (dsn) {
  void Promise.all([import('@sentry/nextjs'), import('./lib/observability')]).then(([Sentry, { sentryOptions }]) => {
    Sentry.init(sentryOptions(dsn, process.env.NEXT_PUBLIC_APP_ENV ?? 'development', process.env.NEXT_PUBLIC_APP_VERSION))
  })
}
