'use client'

import { firebaseConfig } from '@/lib/env'

/** What Firebase reports when the visitor closes Google's popup: changing your mind, not an error. */
const CANCELLED = new Set(['auth/popup-closed-by-user', 'auth/cancelled-popup-request', 'auth/user-cancelled'])

/** Popups are refused: fall through to a full-page redirect, which comes back to this same address. */
const POPUP_BLOCKED = new Set(['auth/popup-blocked', 'auth/operation-not-supported-in-this-environment'])

const NEXT_KEY = 'lvn:google-next'
const PENDING_KEY = 'lvn:google-redirect'

/**
 * Playwright's stand-in Firebase project (playwright.config.ts). Clicking Continue with Google must not load Firebase
 * or open Google; the mocked API accepts this token. Production builds never use this project id.
 */
const E2E_PROJECT = 'lvn-e2e'
export const E2E_GOOGLE_ID_TOKEN = 'e2e-google-id-token'

export type GoogleSignInAttempt = { status: 'token'; idToken: string } | { status: 'cancelled' } | { status: 'redirecting' }

/** How a failed popup should be treated. Unknown codes are real errors. */
export function googlePopupOutcome(code: string): 'cancel' | 'redirect' | 'error' {
  if (CANCELLED.has(code)) return 'cancel'
  if (POPUP_BLOCKED.has(code)) return 'redirect'
  return 'error'
}

type FirebaseAuthModule = typeof import('firebase/auth')

async function firebaseAuth(): Promise<{ auth: ReturnType<FirebaseAuthModule['getAuth']>; mod: FirebaseAuthModule }> {
  if (!firebaseConfig) throw new Error('Google sign-in is not configured')
  const [{ initializeApp, getApps }, mod] = await Promise.all([import('firebase/app'), import('firebase/auth')])
  const app = getApps().find((candidate) => candidate.name === 'lvn') ?? initializeApp(firebaseConfig, 'lvn')
  return { auth: mod.getAuth(app), mod }
}

/** Where to continue after a redirect round-trip. A missing value clears a previous attempt. */
export function rememberGoogleNext(next?: string | null): void {
  if (next) sessionStorage.setItem(NEXT_KEY, next)
  else sessionStorage.removeItem(NEXT_KEY)
}

/** The path stored before a redirect, consumed so it cannot be replayed. */
export function takeGoogleNext(): string | null {
  const next = sessionStorage.getItem(NEXT_KEY)
  sessionStorage.removeItem(NEXT_KEY)
  return next
}

/**
 * Google sign-in through Firebase Authentication (lvn-backend ADR-0007): a popup, or a redirect where popups are
 * blocked, yields a Firebase ID token. The API exchanges it once for an LVN session. Firebase is loaded only for
 * this attempt and signed out of straight after — its tokens are never sent again.
 */
export async function googleIdToken(): Promise<GoogleSignInAttempt> {
  if (!firebaseConfig) throw new Error('Google sign-in is not configured')
  if (firebaseConfig.projectId === E2E_PROJECT) return { status: 'token', idToken: E2E_GOOGLE_ID_TOKEN }
  sessionStorage.removeItem(PENDING_KEY)
  const { auth, mod } = await firebaseAuth()
  const provider = new mod.GoogleAuthProvider()
  try {
    const result = await mod.signInWithPopup(auth, provider)
    try {
      return { status: 'token', idToken: await result.user.getIdToken() }
    } finally {
      await mod.signOut(auth)
    }
  } catch (error) {
    const code = (error as { code?: string }).code ?? ''
    const outcome = googlePopupOutcome(code)
    if (outcome === 'cancel') return { status: 'cancelled' }
    if (outcome !== 'redirect') throw error
    sessionStorage.setItem(PENDING_KEY, '1')
    await mod.signInWithRedirect(auth, provider)
    return { status: 'redirecting' }
  }
}

let redirectOnce: Promise<string | null> | undefined

/**
 * The ID token from a redirect that just returned to this page, or null when this load is not one.
 * Firebase is not loaded unless a redirect was started in this tab.
 */
export function googleRedirectIdToken(): Promise<string | null> {
  if (typeof sessionStorage === 'undefined') return Promise.resolve(null)
  if (!firebaseConfig || firebaseConfig.projectId === E2E_PROJECT) return Promise.resolve(null)
  if (sessionStorage.getItem(PENDING_KEY) !== '1') return Promise.resolve(null)
  redirectOnce ??= (async () => {
    sessionStorage.removeItem(PENDING_KEY)
    const { auth, mod } = await firebaseAuth()
    const result = await mod.getRedirectResult(auth)
    if (!result) return null
    try {
      return await result.user.getIdToken()
    } finally {
      await mod.signOut(auth)
    }
  })()
  return redirectOnce
}
