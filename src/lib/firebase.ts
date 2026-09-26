/* ============================================================
   FIREBASE — Firestore (lite) only.
   No auth, no analytics: content is public and read-only
   (see firestore.rules). Config comes from .env.local.
   ============================================================ */

import { initializeApp } from 'firebase/app'
import { getFirestore } from 'firebase/firestore/lite'

const env = import.meta.env

export const firebaseConfigured = Boolean(env.VITE_FIREBASE_API_KEY && env.VITE_FIREBASE_PROJECT_ID)

const app = initializeApp({
  apiKey: env.VITE_FIREBASE_API_KEY,
  authDomain: env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: env.VITE_FIREBASE_APP_ID,
})

export const db = getFirestore(app)
