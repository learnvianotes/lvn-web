import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'

const here = (p: string) => fileURLToPath(new URL(p, import.meta.url))

/** Unit tests live in tests/unit; browser tests in tests/e2e run with Playwright (playwright.config.ts). */
export default defineConfig({
  // tsconfig keeps JSX for Next ("preserve"); tests compile it themselves.
  oxc: { jsx: { runtime: 'automatic' } },
  test: {
    include: ['tests/unit/**/*.test.{ts,tsx}'],
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
