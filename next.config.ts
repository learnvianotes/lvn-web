import { readFileSync } from 'node:fs'
import type { NextConfig } from 'next'
import createNextIntlPlugin from 'next-intl/plugin'

/** Subjects that used to live at the site root (learnvianotes.in/<subject>/<topic>) now live under /core. */
const legacySubjects = (JSON.parse(readFileSync('content-build/catalog.json', 'utf8')) as { subjects: { id: string }[] })
  .subjects.map((s) => s.id)

/** Pages of the retired app with no equivalent yet; accounts arrive with the Phase 1 backend. */
const retiredPages = ['about', 'login', 'signup', 'forgot-password', 'history', 'settings']

const securityHeaders = [
  { key: 'X-Content-Type-Options', value: 'nosniff' },
  { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
  { key: 'X-Frame-Options', value: 'DENY' },
  { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=(), payment=()' },
  { key: 'Strict-Transport-Security', value: 'max-age=31536000; includeSubDomains' },
]

const config: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  async headers() {
    return [
      { source: '/:path*', headers: securityHeaders },
      // The retired app's service worker is replaced by public/sw.js, which removes itself.
      { source: '/sw.js', headers: [{ key: 'Cache-Control', value: 'no-cache' }] },
    ]
  },
  async redirects() {
    return [
      ...legacySubjects.flatMap((id) => [
        { source: `/${id}`, destination: `/core/${id}`, permanent: true },
        { source: `/${id}/:item`, destination: `/core/${id}/:item`, permanent: true },
      ]),
      ...retiredPages.map((page) => ({ source: `/${page}`, destination: '/', permanent: false })),
    ]
  },
}

export default createNextIntlPlugin('./i18n/request.ts')(config)
