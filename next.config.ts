import { readFileSync } from 'node:fs'
import type { NextConfig } from 'next'
import createNextIntlPlugin from 'next-intl/plugin'

/**
 * Subjects that used to live at the site root (learnvianotes.in/<subject>/<topic>): under /core while the old notes are on,
 * otherwise on the app's own subject pages, which share their slugs (the curated catalogue).
 */
const legacySubjects = (JSON.parse(readFileSync('content-build/catalog.json', 'utf8')) as { subjects: { id: string }[] })
  .subjects.map((s) => s.id)

/** Pages of the retired app with no equivalent yet; accounts arrive with the Phase 1 backend. History came back in
 * Phase 6 (lvn-backend ADR-0067): the old /history address now opens the new learning history. */
const retiredPages = ['login', 'signup', 'forgot-password', 'settings']

/** The old notes at /core are kept for later and off unless NEXT_PUBLIC_CORE_ENABLED=true (owner, 2026-10-14). */
const coreEnabled = process.env.NEXT_PUBLIC_CORE_ENABLED === 'true'

const { version } = JSON.parse(readFileSync('package.json', 'utf8')) as { version: string }

/**
 * Content Security Policy (lvn-backend ADR-0090, Phase 9). Pages are cached (ISR), so scripts cannot carry a per-request
 * nonce: inline scripts stay allowed (Next's own and the theme script). Everything else is shut: plugins, other sites
 * framing us, a changed base URL, forms posting elsewhere and frames other than Google sign-in. Files come from storage
 * by pre-signed URL, whose origin is the environment's, so images, media and connections allow any HTTPS origin (and
 * plain HTTP or WebSocket only where the site itself runs on HTTP, the local environment).
 */
const plain = (process.env.NEXT_PUBLIC_SITE_URL ?? 'http://localhost:3000').startsWith('http:')
const anyOrigin = plain ? 'https: http:' : 'https:'
// `next dev` evaluates its modules; built pages never do.
const devEval = process.env.NODE_ENV === 'development' ? " 'unsafe-eval'" : ''
const contentSecurityPolicy = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline'${devEval} https://apis.google.com https://www.gstatic.com https://*.firebaseapp.com`,
  "style-src 'self' 'unsafe-inline'",
  `img-src 'self' data: blob: ${anyOrigin}`,
  `media-src 'self' blob: ${anyOrigin}`,
  "font-src 'self' data:",
  `connect-src 'self' ${anyOrigin} ${plain ? 'wss: ws:' : 'wss:'}`,
  'frame-src https://*.firebaseapp.com https://accounts.google.com',
  "worker-src 'self' blob:",
  "manifest-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
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

const config: NextConfig = {
  // E2E builds go to their own folder so they never clobber a running `next dev` (playwright.config.ts).
  distDir: process.env.NEXT_DIST_DIR ?? '.next',
  // The container image (Dockerfile) runs the self-contained server Next traces into .next/standalone.
  output: process.env.NEXT_OUTPUT === 'standalone' ? 'standalone' : undefined,
  reactStrictMode: true,
  poweredByHeader: false,
  // Shown in the /core help centre and attached to feedback reports.
  env: { NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION ?? version },
  // / and /core have separate root layouts, so an unmatched URL needs a 404 page of its own.
  experimental: { globalNotFound: true },
  async headers() {
    return [
      { source: '/:path*', headers: securityHeaders },
      // The retired app's service worker is replaced by public/sw.js, which removes itself.
      { source: '/sw.js', headers: [{ key: 'Cache-Control', value: 'no-cache' }] },
      // pdf.js's character maps, fonts and decoders (scripts/pdfjs-assets.mjs), under a versioned path: the phone's PDF
      // reader, a web view without this origin, loads them too (lvn-backend ADR-0040).
      { source: '/pdfjs/:path*', headers: [{ key: 'Access-Control-Allow-Origin', value: '*' }, { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }] },
    ]
  },
  async redirects() {
    return [
      ...(coreEnabled
        ? [
            ...legacySubjects.flatMap((id) => [
              { source: `/${id}`, destination: `/core/${id}`, permanent: true },
              { source: `/${id}/:item`, destination: `/core/${id}/:item`, permanent: true },
            ]),
            { source: '/about', destination: '/core/about', permanent: true },
          ]
        : [
            // Temporary while /core is off, so they can point back to it later.
            ...legacySubjects.flatMap((id) => [
              { source: `/${id}`, destination: `/subjects/${id}`, permanent: false },
              { source: `/${id}/:item`, destination: `/subjects/${id}`, permanent: false },
            ]),
            { source: '/about', destination: '/', permanent: false },
            { source: '/core', destination: '/subjects', permanent: false },
            { source: '/core/:subject/:rest*', destination: '/subjects/:subject', permanent: false },
          ]),
      ...retiredPages.map((page) => ({ source: `/${page}`, destination: '/', permanent: false })),
    ]
  },
}

export default createNextIntlPlugin('./i18n/request.ts')(config)
