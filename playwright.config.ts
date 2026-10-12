import { defineConfig, devices } from '@playwright/test'
import { E2E_REVALIDATE_SECRET, LIVE_URL } from './tests/e2e/support/constants'

const port = Number(process.env.PORT ?? 3100)
const ssrApiPort = 3199

export default defineConfig({
  testDir: 'tests/e2e',
  use: { baseURL: process.env.E2E_BASE_URL ?? `http://localhost:${port}` },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'phone', use: { ...devices['Pixel 7'] } },
  ],
  // A production build in its own folder (.next-e2e), so a running `pnpm dev` is never disturbed.
  webServer: process.env.E2E_BASE_URL
    ? undefined
    : [
        {
          // What server rendering (public note pages, the sitemap) reads instead of lvn-backend: tests/e2e/support.
          command: `node tests/e2e/support/ssr-api.mjs`,
          env: { SSR_API_PORT: String(ssrApiPort) },
          url: `http://127.0.0.1:${ssrApiPort}/`,
          reuseExistingServer: !process.env.CI,
        },
        {
          command: `pnpm build && pnpm start -p ${port}`,
          // A stand-in Firebase web config, so the Google button shows whenever the mocked API offers Google. Firebase is
          // only loaded on a click, which no test makes.
          env: {
            NEXT_DIST_DIR: '.next-e2e',
            // Live updates go to an address nothing answers; tests that need a socket intercept it (tests/e2e/support).
            NEXT_PUBLIC_LIVE_URL: LIVE_URL,
            NEXT_PUBLIC_FIREBASE_API_KEY: 'e2e-api-key',
            NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: 'lvn-e2e.firebaseapp.com',
            NEXT_PUBLIC_FIREBASE_PROJECT_ID: 'lvn-e2e',
            NEXT_PUBLIC_FIREBASE_APP_ID: '1:0:web:e2e',
            API_INTERNAL_URL: `http://127.0.0.1:${ssrApiPort}/graphql`,
            REVALIDATE_SECRET: E2E_REVALIDATE_SECRET,
          },
          port,
          timeout: 300_000,
          reuseExistingServer: !process.env.CI,
        },
      ],
})
