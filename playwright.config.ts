import { defineConfig, devices } from '@playwright/test'

const port = Number(process.env.PORT ?? 3100)

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
    : {
        command: `pnpm build && pnpm start -p ${port}`,
        // A stand-in Firebase web config, so the Google button shows whenever the mocked API offers Google. Firebase is
        // only loaded on a click, which no test makes.
        env: {
          NEXT_DIST_DIR: '.next-e2e',
          NEXT_PUBLIC_FIREBASE_API_KEY: 'e2e-api-key',
          NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN: 'lvn-e2e.firebaseapp.com',
          NEXT_PUBLIC_FIREBASE_PROJECT_ID: 'lvn-e2e',
          NEXT_PUBLIC_FIREBASE_APP_ID: '1:0:web:e2e',
        },
        port,
        timeout: 300_000,
        reuseExistingServer: !process.env.CI,
      },
})
