/* ============================================================
   FIREBASE CONFIGURATION & INITIALIZATION
   Connected to project: c-notes-4e9d3
   ============================================================ */

import { initializeApp, getApps, getApp, type FirebaseApp } from 'firebase/app'
import { getFirestore, type Firestore } from 'firebase/firestore'
import { getAuth, type Auth } from 'firebase/auth'
import { getAnalytics, isSupported, type Analytics } from 'firebase/analytics'

export const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || 'AIzaSyDQfNg66gT4J5nBWkE9RNdFg4Vq6RkoVWU',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || 'c-notes-4e9d3.firebaseapp.com',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || 'c-notes-4e9d3',
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || 'c-notes-4e9d3.firebasestorage.app',
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '744631117844',
  appId: import.meta.env.VITE_FIREBASE_APP_ID || '1:744631117844:web:66cd024ffabde869bf9f01',
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || 'G-FJD44EBRL8',
}

/** Initialize Firebase singleton instance */
export const app: FirebaseApp = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig)

/** Cloud Firestore Database */
export const db: Firestore = getFirestore(app)

/** Firebase Authentication */
export const auth: Auth = getAuth(app)

/** Optional Firebase Analytics with browser environment check */
export let analytics: Analytics | null = null
if (typeof window !== 'undefined') {
  isSupported()
    .then((supported) => {
      if (supported) {
        analytics = getAnalytics(app)
      }
    })
    .catch(() => {
      // Ignored if blocked or offline
    })
}
