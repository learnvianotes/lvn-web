/* ============================================================
   FIREBASE — the app instance. Config comes from .env.local.
   Firestore lives in ./db.ts and is only imported lazily, so
   pages that don't need it never download it.
   ============================================================ */

import { initializeApp, type FirebaseApp } from 'firebase/app'
import { SAME_SITE_AUTH_DOMAINS } from '@/config'

const env = import.meta.env

/** Sign in through the site's own domain where it's hosted on Firebase; elsewhere (dev) the default. */
function authDomain(): string | undefined {
  const host = typeof location !== 'undefined' ? location.hostname : ''
  return SAME_SITE_AUTH_DOMAINS.includes(host) ? host : env.VITE_FIREBASE_AUTH_DOMAIN
}

export const firebaseConfigured = Boolean(env.VITE_FIREBASE_API_KEY && env.VITE_FIREBASE_PROJECT_ID)

let app: FirebaseApp | undefined

export function firebaseApp(): FirebaseApp {
  if (!firebaseConfigured) throw new Error('Firebase is not configured — set the VITE_FIREBASE_* variables in .env.local.')
  app ??= initializeApp({
    apiKey: env.VITE_FIREBASE_API_KEY,
    authDomain: authDomain(),
    projectId: env.VITE_FIREBASE_PROJECT_ID,
    storageBucket: env.VITE_FIREBASE_STORAGE_BUCKET,
    messagingSenderId: env.VITE_FIREBASE_MESSAGING_SENDER_ID,
    appId: env.VITE_FIREBASE_APP_ID,
    measurementId: env.VITE_FIREBASE_MEASUREMENT_ID,
  })
  return app
}
