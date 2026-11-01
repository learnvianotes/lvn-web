/**
 * Content Security Policy and the other response headers (lvn-backend ADR-0090, Phase 9).
 * Pages are cached (ISR), so scripts cannot carry a per-request nonce: inline scripts stay allowed (Next's own and
 * the theme script). Everything else is shut: plugins, other sites framing us, a changed base URL, and frames other
 * than Google sign-in. Forms post only to this site, except Google's own sign-in host. Connections go only to the
 * site, the API and its live updates, storage (NEXT_PUBLIC_STORAGE_ORIGINS), Google sign-in, Sentry and, where it
 * is configured, Google Analytics (ADR-0092); without storage origins (development, tests) to any origin. Images
 * and media come by pre-signed URL, itself the permission, so they allow any HTTPS origin (and plain HTTP or
 * WebSocket only where the site itself runs on HTTP, the local environment).
 *
 * /__/auth is Firebase's helper proxied onto this origin (lib/auth/firebase-auth-proxy.ts). It is framed by the
 * sign-in page, so it does not get the site's `frame-ancestors 'none'` or `X-Frame-Options: DENY`. That rule is
 * listed after the site-wide one: a later match replaces the same header.
 *
 * Relative imports only: next.config.ts loads this file without the @/ alias.
 */
import { FIREBASE_AUTH_HELPER_HEADERS } from './auth/firebase-auth-proxy'

export type HeaderRule = { source: string; headers: { key: string; value: string }[] }

export type SiteHeaderEnv = {
  siteUrl?: string
  apiUrl?: string
  liveUrl?: string
  storageOrigins?: string
  sentryDsn?: string
  gaMeasurementId?: string
  /** When development, the policy allows eval (next dev). */
  nodeEnv?: string
}

/** Header rules for this deployment. /__/auth comes last so its framing policy replaces the site-wide one. */
export function siteHeaderRules(env: SiteHeaderEnv): HeaderRule[] {
  const plain = (env.siteUrl ?? 'http://localhost:3000').startsWith('http:')
  const anyOrigin = plain ? 'https: http:' : 'https:'
  const devEval = env.nodeEnv === 'development' ? " 'unsafe-eval'" : ''
  const originOf = (url: string | undefined) => {
    try {
      return url ? new URL(url).origin : null
    } catch {
      return null
    }
  }
  const storageOrigins = env.storageOrigins?.trim()
  const analytics = env.gaMeasurementId
    ? { script: ' https://www.googletagmanager.com', connect: ['https://www.googletagmanager.com', 'https://*.google-analytics.com', 'https://*.analytics.google.com'] }
    : { script: '', connect: [] as string[] }
  const connections = storageOrigins
    ? [
        "'self'",
        'blob:',
        'data:',
        originOf(env.apiUrl),
        originOf(env.liveUrl),
        ...storageOrigins.split(/\s+/),
        // Google sign-in through Firebase Authentication (identitytoolkit, securetoken) and Sentry, when set.
        'https://*.googleapis.com',
        'https://accounts.google.com',
        'https://*.firebaseapp.com',
        originOf(env.sentryDsn),
        ...analytics.connect,
      ]
        .filter((origin): origin is string => !!origin && origin !== 'null')
        .join(' ')
    : `'self' ${anyOrigin} ${plain ? 'wss: ws:' : 'wss:'}`
  const contentSecurityPolicy = [
    "default-src 'self'",
    // 'wasm-unsafe-eval': pdf.js decodes JPEG 2000 and colour profiles with WebAssembly (public/pdfjs/<version>/wasm).
    `script-src 'self' 'unsafe-inline' 'wasm-unsafe-eval'${devEval} https://apis.google.com https://www.gstatic.com https://*.firebaseapp.com${analytics.script}`,
    "style-src 'self' 'unsafe-inline'",
    `img-src 'self' data: blob: ${anyOrigin}`,
    `media-src 'self' blob: ${anyOrigin}`,
    "font-src 'self' data:",
    `connect-src ${connections}`,
    // 'self': the Firebase auth iframe is proxied to /__/auth on this origin.
    "frame-src 'self' https://*.firebaseapp.com https://accounts.google.com",
    "worker-src 'self' blob:",
    "manifest-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    // The helper, and a popup that posts from this origin, must be able to submit to Google.
    "form-action 'self' https://accounts.google.com https://*.google.com https://*.firebaseapp.com",
    "frame-ancestors 'none'",
    ...(plain ? [] : ['upgrade-insecure-requests']),
  ].join('; ')

  const securityHeaders = [
    { key: 'Content-Security-Policy', value: contentSecurityPolicy },
    { key: 'X-Content-Type-Options', value: 'nosniff' },
    { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
    { key: 'X-Frame-Options', value: 'DENY' },
    { key: 'Permissions-Policy', value: 'camera=(), microphone=(self), geolocation=(), payment=()' },
    { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' },
  ]

  return [
    { source: '/:path*', headers: securityHeaders },
    { source: '/__/auth/:path*', headers: FIREBASE_AUTH_HELPER_HEADERS },
  ]
}

export function siteHeadersFromProcess(): HeaderRule[] {
  return siteHeaderRules({
    siteUrl: process.env.NEXT_PUBLIC_SITE_URL,
    apiUrl: process.env.NEXT_PUBLIC_API_URL,
    liveUrl: process.env.NEXT_PUBLIC_LIVE_URL,
    storageOrigins: process.env.NEXT_PUBLIC_STORAGE_ORIGINS,
    sentryDsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
    gaMeasurementId: process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID,
    nodeEnv: process.env.NODE_ENV,
  })
}
