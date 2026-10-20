import { defineConfig } from 'vitest/config'
import { fileURLToPath, URL } from 'node:url'

// Unit tests only — no PWA or launch-check plugins (those are build concerns).
export default defineConfig({
  test: { include: ['src/**/*.test.ts', 'build/**/*.test.ts'] },
  resolve: {
    alias: {
      '@schema': fileURLToPath(new URL('./schema', import.meta.url)),
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
