import { readFileSync } from 'node:fs'
import type { NextConfig } from 'next'
import { PHASE_PRODUCTION_BUILD } from 'next/constants'
import createNextIntlPlugin from 'next-intl/plugin'
import { launchProblems } from './lib/launch-checks'
import { siteHeadersFromProcess } from './lib/security-headers'

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

const config: NextConfig = {
  // E2E builds go to their own folder so they never clobber a running `next dev` (playwright.config.ts).
  distDir: process.env.NEXT_DIST_DIR ?? '.next',
  // The container image (Dockerfile) runs the self-contained server Next traces into .next/standalone.
  output: process.env.NEXT_OUTPUT === 'standalone' ? 'standalone' : undefined,
  reactStrictMode: true,
  poweredByHeader: false,
  // Shown in the /core help centre, the site footer and /version, and attached to feedback reports.
  // The commit is the build-time git SHA (Dockerfile ARG NEXT_PUBLIC_GIT_SHA). Empty means it was not passed.
  env: {
    NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION ?? version,
    NEXT_PUBLIC_GIT_SHA: process.env.NEXT_PUBLIC_GIT_SHA || 'unknown',
  },
  // / and /core have separate root layouts, so an unmatched URL needs a 404 page of its own.
  experimental: { globalNotFound: true },
  async headers() {
    return [
      ...siteHeadersFromProcess(),
      // The retired app's service worker is replaced by public/sw.js, which removes itself.
      { source: '/sw.js', headers: [{ key: 'Cache-Control', value: 'no-cache' }] },
      // pdf.js's character maps, fonts and decoders (scripts/pdfjs-assets.mjs), under a versioned path: the phone's PDF
      // reader, a web view without this origin, loads them too (lvn-backend ADR-0040).
      { source: '/pdfjs/:path*', headers: [{ key: 'Access-Control-Allow-Origin', value: '*' }, { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' }] },
    ]
  },
  async rewrites() {
    // Transparent proxy: the browser stays on this origin. A 302 to firebaseapp.com would put the session
    // back in third-party storage. The route forwards Google's own redirect to accounts.google.com as-is.
    return { beforeFiles: [{ source: '/__/auth/:path*', destination: '/api/firebase-auth/:path*' }] }
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
      // The Google callback sends a blocked beta sign-in to /signin?error=invite_only.
      { source: '/signin', destination: '/sign-in', permanent: false },
      ...retiredPages.map((page) => ({ source: `/${page}`, destination: '/', permanent: false })),
    ]
  },
}

const withIntl = createNextIntlPlugin('./i18n/request.ts')

/** `next build` runs the launch checks first (lib/launch-checks.ts, lvn-backend ADR-0093); dev and start don't. */
export default function nextConfig(phase: string): NextConfig {
  if (phase === PHASE_PRODUCTION_BUILD) {
    const problems = launchProblems({
      appEnv: process.env.NEXT_PUBLIC_APP_ENV ?? 'development',
      siteUrl: process.env.NEXT_PUBLIC_SITE_URL ?? '',
      apiUrl: process.env.NEXT_PUBLIC_API_URL ?? '',
      liveUrl: process.env.NEXT_PUBLIC_LIVE_URL ?? '',
      firebaseProject: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID ?? '',
    })
    if (problems.length) throw new Error(`Launch check failed:\n  - ${problems.join('\n  - ')}`)
  }
  return withIntl(config)
}
