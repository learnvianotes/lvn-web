import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'
import { fileURLToPath, URL } from 'node:url'
import { readFileSync } from 'node:fs'

const pkg = JSON.parse(readFileSync(new URL('./package.json', import.meta.url), 'utf8')) as { version: string }

export default defineConfig({
  define: { 'import.meta.env.VITE_APP_VERSION': JSON.stringify(pkg.version) },
  plugins: [
    react(),
    // Installable app + offline support for the app shell. Study content comes from
    // Firestore and is cached on the device by the app itself (features/catalog/source.ts).
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'LearnViaNotes',
        short_name: 'LearnViaNotes',
        description: 'Quick, focused notes for CS interview preparation. Nothing required — just learn.',
        start_url: '/',
        scope: '/',
        display: 'standalone',
        background_color: '#f7f7f8',
        theme_color: '#ffffff',
        icons: [
          { src: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icons/icon-512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html}', 'icons/*.png'],
        navigateFallback: '/index.html',
        runtimeCaching: [
          {
            urlPattern: ({ url }) => ['fonts.googleapis.com', 'fonts.gstatic.com', 'cdn.jsdelivr.net'].includes(url.hostname),
            handler: 'CacheFirst',
            options: { cacheName: 'cdn', expiration: { maxEntries: 40, maxAgeSeconds: 60 * 60 * 24 * 365 }, cacheableResponse: { statuses: [0, 200] } },
          },
        ],
      },
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        // Long-lived vendor chunks: app deploys don't invalidate the cached libraries.
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (/[\\/](react|react-dom|scheduler|react-router|react-router-dom)[\\/]/.test(id)) return 'vendor-react'
          if (/[\\/]@firebase[\\/](app|component|logger|util)[\\/]|[\\/]firebase[\\/]app[\\/]/.test(id)) return 'vendor-firebase'
        },
      },
    },
  },
  server: { port: 9090, strictPort: true },
  resolve: {
    alias: {
      '@schema': fileURLToPath(new URL('./schema', import.meta.url)),
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
