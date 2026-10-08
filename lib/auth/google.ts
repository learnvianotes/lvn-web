'use client'

import { firebaseConfig } from '@/lib/env'

/**
 * Google sign-in through Firebase Authentication (lvn-backend ADR-0007): a popup (or redirect where popups are
 * blocked) yields a Firebase ID token, which the API exchanges once for an LVN session. Firebase is loaded only when
 * someone taps the button, and signed out of straight after — its tokens are never sent again.
 */
export async function googleIdToken(): Promise<string> {
  if (!firebaseConfig) throw new Error('Google sign-in is not configured')
  const [{ initializeApp, getApps }, { getAuth, GoogleAuthProvider, signInWithPopup, signOut }] = await Promise.all([import('firebase/app'), import('firebase/auth')])
  const app = getApps().find((a) => a.name === 'lvn') ?? initializeApp(firebaseConfig, 'lvn')
  const auth = getAuth(app)
  const { user } = await signInWithPopup(auth, new GoogleAuthProvider())
  try {
    return await user.getIdToken()
  } finally {
    await signOut(auth)
  }
}
