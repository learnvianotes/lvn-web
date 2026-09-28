/* ============================================================
   AUTH — Firebase Authentication, loaded after first paint so
   reading notes never waits for it.

     email + password (with verification and password reset)
     Google · GitHub · LinkedIn (OIDC provider "oidc.linkedin")

   Security notes
   • Error messages never reveal whether an email is registered
     (sign-in, sign-up and reset all answer generically).
   • Sessions persist in IndexedDB on this device only; signing
     out also clears the local copy of the user's study data
     (see progress/sync.ts), so a shared computer leaks nothing.
   • Which providers work is decided in the Firebase console —
     see docs/auth-setup.md.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import type { Auth, AuthProvider, User } from 'firebase/auth'
import { firebaseApp, firebaseConfigured } from '@/services/firebase/app'

export interface AppUser {
  uid: string
  name: string
  email: string
  photoURL: string
  emailVerified: boolean
  /** 'password' | 'google.com' | 'github.com' | 'oidc.linkedin' */
  provider: string
}

export type AuthState =
  | { status: 'loading' }
  | { status: 'unavailable' }
  | { status: 'signed-out' }
  | { status: 'signed-in'; user: AppUser }

export type ProviderId = 'google' | 'github' | 'linkedin'

/* ── state store ─────────────────────────────────────────── */

let state: AuthState = firebaseConfigured ? { status: 'loading' } : { status: 'unavailable' }
const listeners = new Set<() => void>()

function setState(next: AuthState) {
  state = next
  listeners.forEach((l) => l())
}

export function subscribeAuth(listener: () => void) {
  listeners.add(listener)
  return () => { listeners.delete(listener) }
}

export const getAuthState = () => state

export function useAuth(): AuthState {
  return useSyncExternalStore(subscribeAuth, getAuthState)
}

export function useUser(): AppUser | null {
  const s = useAuth()
  return s.status === 'signed-in' ? s.user : null
}

/* ── Firebase Auth (lazy) ────────────────────────────────── */

type AuthModule = typeof import('firebase/auth')
let ready: Promise<{ mod: AuthModule; auth: Auth }> | null = null

function toAppUser(u: User): AppUser {
  return {
    uid: u.uid,
    name: u.displayName || u.email?.split('@')[0] || 'Learner',
    email: u.email ?? '',
    photoURL: u.photoURL ?? '',
    emailVerified: u.emailVerified,
    provider: u.providerData[0]?.providerId ?? 'password',
  }
}

/** sessionStorage flag: a provider sign-in fell back to a full-page redirect. */
const REDIRECT_PENDING = 'lvn:auth-redirect'

function load() {
  ready ??= import('firebase/auth').then((mod) => {
    // No popupRedirectResolver here on purpose: with one, every page load waits for an iframe
    // from Google before auth is ready (slow networks / blocked scripts would stall sign-in).
    // It's passed only to the popup / redirect calls instead.
    const auth = mod.initializeAuth(firebaseApp(), {
      persistence: [mod.indexedDBLocalPersistence, mod.browserLocalPersistence],
    })
    auth.useDeviceLanguage()
    // Local development against the Auth emulator (npm run emulators).
    if (import.meta.env.DEV && import.meta.env.VITE_AUTH_EMULATOR) mod.connectAuthEmulator(auth, import.meta.env.VITE_AUTH_EMULATOR, { disableWarnings: true })
    mod.onAuthStateChanged(auth, (u) => setState(u ? { status: 'signed-in', user: toAppUser(u) } : { status: 'signed-out' }))
    // Finish a sign-in that fell back to a full-page redirect (only when one was started).
    if (sessionStorage.getItem(REDIRECT_PENDING)) {
      sessionStorage.removeItem(REDIRECT_PENDING)
      mod.getRedirectResult(auth, mod.browserPopupRedirectResolver).catch(() => {})
    }
    return { mod, auth }
  })
  return ready
}

/** Starts Firebase Auth. Called once from main.tsx. */
export function initAuth() {
  if (!firebaseConfigured) return
  load().catch(() => setState({ status: 'unavailable' }))
}

/* ── actions ─────────────────────────────────────────────── */

export async function signInWithEmail(email: string, password: string) {
  const { mod, auth } = await load()
  await mod.signInWithEmailAndPassword(auth, normalizeEmail(email), password)
}

export async function signUpWithEmail(name: string, email: string, password: string) {
  const { mod, auth } = await load()
  const cred = await mod.createUserWithEmailAndPassword(auth, normalizeEmail(email), password)
  const displayName = name.trim().slice(0, 60)
  if (displayName) await mod.updateProfile(cred.user, { displayName })
  await mod.sendEmailVerification(cred.user).catch(() => {})
  setState({ status: 'signed-in', user: toAppUser(cred.user) })
}

export async function signInWithProvider(id: ProviderId) {
  const { mod, auth } = await load()
  let provider: AuthProvider
  if (id === 'google') {
    const p = new mod.GoogleAuthProvider()
    p.setCustomParameters({ prompt: 'select_account' })
    provider = p
  } else if (id === 'github') {
    const p = new mod.GithubAuthProvider()
    p.addScope('read:user')
    p.addScope('user:email')
    provider = p
  } else {
    const p = new mod.OAuthProvider('oidc.linkedin')
    ;['openid', 'profile', 'email'].forEach((s) => p.addScope(s))
    provider = p
  }
  try {
    await mod.signInWithPopup(auth, provider, mod.browserPopupRedirectResolver)
  } catch (e) {
    // Popups blocked (common on mobile / in-app browsers): use a full-page redirect instead.
    if (errorCode(e) === 'auth/popup-blocked' || errorCode(e) === 'auth/operation-not-supported-in-this-environment') {
      sessionStorage.setItem(REDIRECT_PENDING, '1')
      await mod.signInWithRedirect(auth, provider, mod.browserPopupRedirectResolver)
      return
    }
    throw e
  }
}

/** Always resolves the same way whether or not the account exists. */
export async function sendPasswordReset(email: string) {
  const { mod, auth } = await load()
  try {
    await mod.sendPasswordResetEmail(auth, normalizeEmail(email))
  } catch (e) {
    const code = errorCode(e)
    if (code === 'auth/user-not-found' || code === 'auth/invalid-email') return
    throw e
  }
}

export async function resendVerification() {
  const { mod, auth } = await load()
  if (auth.currentUser) await mod.sendEmailVerification(auth.currentUser)
}

/** Re-reads the user (e.g. after they clicked the verification link). */
export async function refreshUser() {
  const { auth } = await load()
  if (!auth.currentUser) return
  await auth.currentUser.reload()
  setState({ status: 'signed-in', user: toAppUser(auth.currentUser) })
}

type SignOutHook = () => Promise<void> | void
const beforeSignOut = new Set<SignOutHook>()
/** progress/sync.ts flushes pending writes and wipes local data here. */
export function onBeforeSignOut(hook: SignOutHook) {
  beforeSignOut.add(hook)
}

/** Longest sign-out waits for pending uploads (offline must never block signing out). */
const SIGN_OUT_WAIT_MS = 4000

export async function signOutUser() {
  const { mod, auth } = await load()
  const hooks = Promise.allSettled([...beforeSignOut].map((hook) => Promise.resolve().then(hook)))
  await Promise.race([hooks, new Promise((r) => setTimeout(r, SIGN_OUT_WAIT_MS))])
  await mod.signOut(auth)
}

/** Deletes the Firebase account. The caller removes the user's data first. */
export async function deleteCurrentUser() {
  const { mod, auth } = await load()
  if (auth.currentUser) await mod.deleteUser(auth.currentUser)
}

/* ── helpers ─────────────────────────────────────────────── */

export function normalizeEmail(email: string) {
  return email.trim().toLowerCase()
}

export function isValidEmail(email: string) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.trim())
}

/** Requirements the password doesn't meet yet (empty = OK). */
export function passwordIssues(pw: string): string[] {
  const issues: string[] = []
  if (pw.length < 8) issues.push('at least 8 characters')
  if (!/[a-z]/i.test(pw)) issues.push('a letter')
  if (!/\d/.test(pw)) issues.push('a number')
  if (pw.length > 128) issues.push('at most 128 characters')
  return issues
}

/** 0–4, for the strength meter. */
export function passwordStrength(pw: string): number {
  let score = 0
  if (pw.length >= 8) score++
  if (pw.length >= 12) score++
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++
  if (/\d/.test(pw) && /[^a-z0-9]/i.test(pw)) score++
  return score
}

export function errorCode(e: unknown): string {
  return typeof e === 'object' && e && 'code' in e ? String((e as { code: unknown }).code) : ''
}

/** Friendly, non-revealing message for an auth error. */
export function authErrorMessage(e: unknown): string {
  switch (errorCode(e)) {
    case 'auth/invalid-credential':
    case 'auth/wrong-password':
    case 'auth/user-not-found':
    case 'auth/invalid-email':
      return 'Email or password is incorrect.'
    case 'auth/email-already-in-use':
      return 'We couldn’t create an account with that email. If you already have one, sign in or reset your password.'
    case 'auth/weak-password':
    case 'auth/password-does-not-meet-requirements':
      return 'Choose a stronger password.'
    case 'auth/too-many-requests':
      return 'Too many attempts. Please wait a few minutes and try again.'
    case 'auth/network-request-failed':
      return 'You appear to be offline. Check your connection and try again.'
    case 'auth/popup-closed-by-user':
    case 'auth/cancelled-popup-request':
    case 'auth/user-cancelled':
      return ''
    case 'auth/account-exists-with-different-credential':
      return 'This email already uses a different sign-in method. Sign in with that one instead.'
    case 'auth/operation-not-allowed':
      return import.meta.env.DEV
        ? 'This sign-in method isn’t enabled — turn it on in Firebase console → Authentication → Sign-in method (docs/auth-setup.md).'
        : 'This sign-in method isn’t available yet. Please try another one.'
    case 'auth/configuration-not-found':
      return import.meta.env.DEV
        ? 'Firebase Authentication isn’t set up for this project — open Firebase console → Authentication → Get started (docs/auth-setup.md).'
        : 'Sign-in isn’t available right now. Please try again later.'
    case 'auth/unauthorized-domain':
      return 'Sign-in isn’t allowed from this address yet.'
    case 'auth/requires-recent-login':
      return 'For your security, sign in again and then retry.'
    case 'auth/user-disabled':
      return 'This account has been disabled.'
    default:
      return 'Something went wrong. Please try again.'
  }
}

/** Only same-site paths are allowed as a post-login destination. */
export function safeNext(next: string | null): string {
  return next && next.startsWith('/') && !next.startsWith('//') && !next.startsWith('/\\') ? next : '/'
}
