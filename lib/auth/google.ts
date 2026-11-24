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

export type GoogleRedirectAttempt = { status: 'none' } | { status: 'missing' } | { status: 'token'; idToken: string }

/**
 * authDomain the browser should use. On https, off localhost and off Firebase's own hosts, that is this site:
 * the SDK then loads /__/auth here (proxied) and Google's redirect URI is https://<this host>/__/auth/handler.
 * HTTP (local) keeps the configured firebaseapp.com domain, whose handler is already registered.
 */
export function googleAuthDomain(configured: string, location: { protocol: string; hostname: string } | null): string {
  if (!location || location.protocol !== 'https:') return configured
  const hostname = location.hostname.toLowerCase()
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1') return configured
  if (hostname.endsWith('.firebaseapp.com') || hostname.endsWith('.web.app')) return configured
  if (hostname === configured.toLowerCase()) return configured
  return location.hostname
}

/** The ID token is the result. Signing Firebase out afterwards must not discard it if sign-out throws. */
export async function tokenThenSignOut(read: () => Promise<string>, signOut: () => Promise<unknown>): Promise<string> {
  const idToken = await read()
  await signOut().catch(() => undefined)
  return idToken
}

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
  const location = typeof window === 'undefined' ? null : window.location
  const config = { ...firebaseConfig, authDomain: googleAuthDomain(firebaseConfig.authDomain, location) }
  const app = getApps().find((candidate) => candidate.name === 'lvn') ?? initializeApp(config, 'lvn')
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
    const idToken = await tokenThenSignOut(() => result.user.getIdToken(), () => mod.signOut(auth))
    return { status: 'token', idToken }
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

let redirectOnce: Promise<GoogleRedirectAttempt> | undefined

/**
 * The ID token from a redirect that just returned to this page.
 * `none` when this load is not one (Firebase is not loaded). `missing` when a redirect was started and came
 * back without a credential — the page says so, instead of leaving the button as if nothing was clicked.
 */
export function googleRedirectIdToken(): Promise<GoogleRedirectAttempt> {
  if (typeof sessionStorage === 'undefined') return Promise.resolve({ status: 'none' })
  if (!firebaseConfig || firebaseConfig.projectId === E2E_PROJECT) return Promise.resolve({ status: 'none' })
  if (sessionStorage.getItem(PENDING_KEY) !== '1') return Promise.resolve({ status: 'none' })
  redirectOnce ??= (async () => {
    sessionStorage.removeItem(PENDING_KEY)
    const { auth, mod } = await firebaseAuth()
    const result = await mod.getRedirectResult(auth)
    if (!result) return { status: 'missing' }
    const idToken = await tokenThenSignOut(() => result.user.getIdToken(), () => mod.signOut(auth))
    return { status: 'token', idToken }
  })()
  return redirectOnce
}
