import { readFileSync } from 'node:fs'
import type { NextConfig } from 'next'
import createNextIntlPlugin from 'next-intl/plugin'

/** Subjects that used to live at the site root (learnvianotes.in/<subject>/<topic>) now live under /core. */
const legacySubjects = (JSON.parse(readFileSync('content-build/catalog.json', 'utf8')) as { subjects: { id: string }[] })
  .subjects.map((s) => s.id)

/** Pages of the retired app with no equivalent yet; accounts arrive with the Phase 1 backend. */
const retiredPages = ['login', 'signup', 'forgot-password', 'history', 'settings']

const { version } = JSON.parse(readFileSync('package.json', 'utf8')) as { version: string }

const securityHeaders = [
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
      ...legacySubjects.flatMap((id) => [
        { source: `/${id}`, destination: `/core/${id}`, permanent: true },
        { source: `/${id}/:item`, destination: `/core/${id}/:item`, permanent: true },
      ]),
      { source: '/about', destination: '/core/about', permanent: true },
      ...retiredPages.map((page) => ({ source: `/${page}`, destination: '/', permanent: false })),
    ]
  },
}

export default createNextIntlPlugin('./i18n/request.ts')(config)
