'use client'

import { firebaseConfig } from '@/lib/env'

/** What Firebase reports when the visitor closes Google's popup: changing your mind, not an error. */
const CANCELLED = new Set(['auth/popup-closed-by-user', 'auth/cancelled-popup-request', 'auth/user-cancelled'])

/**
 * Google sign-in through Firebase Authentication (lvn-backend ADR-0007): a popup (or redirect where popups are
 * blocked) yields a Firebase ID token, which the API exchanges once for an LVN session; null when the popup is closed.
 * Firebase is loaded only when someone taps the button, and signed out of straight after — its tokens are never sent
 * again.
 */
export async function googleIdToken(): Promise<string | null> {
  if (!firebaseConfig) throw new Error('Google sign-in is not configured')
  const [{ initializeApp, getApps }, { getAuth, GoogleAuthProvider, signInWithPopup, signOut }] = await Promise.all([import('firebase/app'), import('firebase/auth')])
  const app = getApps().find((a) => a.name === 'lvn') ?? initializeApp(firebaseConfig, 'lvn')
  const auth = getAuth(app)
  const result = await signInWithPopup(auth, new GoogleAuthProvider()).catch((e: { code?: string }) => {
    if (CANCELLED.has(e.code ?? '')) return null
    throw e
  })
  if (!result) return null
  try {
    return await result.user.getIdToken()
  } finally {
    await signOut(auth)
  }
}
