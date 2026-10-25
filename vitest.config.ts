import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'

const here = (p: string) => fileURLToPath(new URL(p, import.meta.url))

/** Unit tests live in tests/unit; browser tests in tests/e2e run with Playwright (playwright.config.ts). */
export default defineConfig({
  // Next's tsconfig uses the automatic JSX runtime; tests compile JSX themselves.
  oxc: { jsx: { runtime: 'automatic' } },
  test: {
    include: ['tests/unit/**/*.test.{ts,tsx}'],
    env: { NEXT_PUBLIC_SITE_URL: 'http://localhost:3000', NEXT_PUBLIC_API_URL: 'http://localhost:4000/graphql' },
    environment: 'node',
    testTimeout: 30_000,
  },
  resolve: {
    alias: {
      '@core-schema': here('./core-app/schema'),
      '@core-server': here('./core-app/server'),
      '@core': here('./core-app/src'),
      '@': here('./'),
      // `server-only` throws outside a React Server Components build; tests import server modules directly.
      'server-only': here('./tests/support/empty.ts'),
    },
  },
})
