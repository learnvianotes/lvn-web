/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_FIREBASE_API_KEY?: string
  readonly VITE_FIREBASE_AUTH_DOMAIN?: string
  readonly VITE_FIREBASE_PROJECT_ID?: string
  readonly VITE_FIREBASE_STORAGE_BUCKET?: string
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string
  readonly VITE_FIREBASE_APP_ID?: string
  readonly VITE_FIREBASE_MEASUREMENT_ID?: string
  /** Local development: e.g. http://127.0.0.1:9099 (npm run emulators) */
  readonly VITE_AUTH_EMULATOR?: string
  /** Local development: e.g. 127.0.0.1:8080 */
  readonly VITE_FIRESTORE_EMULATOR?: string
  /** production | test | development — from .env.<mode> */
  readonly VITE_SITE_ENV: 'production' | 'test' | 'development'
  /** The site's own address, no trailing slash (canonical links, sitemap) — from .env.<mode> */
  readonly VITE_SITE_URL: string
  /** Set by vite.config.ts from package.json */
  readonly VITE_APP_VERSION: string
}
/// <reference types="vite-plugin-pwa/client" />
