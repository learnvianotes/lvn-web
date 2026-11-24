import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { describe, expect, it } from 'vitest'
import { googleAuthDomain, googlePopupOutcome, tokenThenSignOut } from '@/lib/auth/google'
import { googleSignInProblem } from '@/lib/auth/google-message'

describe('Google popup failures', () => {
  it('treats a closed popup as a cancellation', () => {
    expect(googlePopupOutcome('auth/popup-closed-by-user')).toBe('cancel')
    expect(googlePopupOutcome('auth/cancelled-popup-request')).toBe('cancel')
    expect(googlePopupOutcome('auth/user-cancelled')).toBe('cancel')
  })

  it('falls back to a redirect when the popup is blocked', () => {
    expect(googlePopupOutcome('auth/popup-blocked')).toBe('redirect')
    expect(googlePopupOutcome('auth/operation-not-supported-in-this-environment')).toBe('redirect')
  })

  it('leaves other Firebase codes as errors', () => {
    expect(googlePopupOutcome('auth/network-request-failed')).toBe('error')
    expect(googlePopupOutcome('')).toBe('error')
  })
})

describe('which Firebase auth domain the browser uses', () => {
  const configured = 'project.firebaseapp.com'

  it('uses this site on https so /__/auth is first-party', () => {
    expect(googleAuthDomain(configured, { protocol: 'https:', hostname: 'beta.learnvianotes.in' })).toBe('beta.learnvianotes.in')
    expect(googleAuthDomain(configured, { protocol: 'https:', hostname: 'www.learnvianotes.in' })).toBe('www.learnvianotes.in')
  })

  it('keeps the configured domain for local http, localhost https, and Firebase’s own hosts', () => {
    expect(googleAuthDomain(configured, { protocol: 'http:', hostname: 'localhost' })).toBe(configured)
    expect(googleAuthDomain(configured, { protocol: 'https:', hostname: 'localhost' })).toBe(configured)
    expect(googleAuthDomain(configured, { protocol: 'https:', hostname: '127.0.0.1' })).toBe(configured)
    expect(googleAuthDomain(configured, { protocol: 'https:', hostname: 'project.firebaseapp.com' })).toBe(configured)
    expect(googleAuthDomain(configured, { protocol: 'https:', hostname: 'project.web.app' })).toBe(configured)
    expect(googleAuthDomain(configured, null)).toBe(configured)
  })
})

describe('reading the Firebase ID token', () => {
  it('returns the token even when signing Firebase out throws', async () => {
    await expect(tokenThenSignOut(async () => 'firebase-id-token', async () => {
      throw new Error('sign-out failed')
    })).resolves.toBe('firebase-id-token')
  })

  it('still signs Firebase out after the token is read', async () => {
    let signedOut = false
    await tokenThenSignOut(async () => 'firebase-id-token', async () => {
      signedOut = true
    })
    expect(signedOut).toBe(true)
  })
})

describe('what a failed Google exchange shows', () => {
  const fallback = 'That sign-in did not work. Try again.'
  const problem = (code: string, message: string) => new CombinedGraphQLErrors({ errors: [{ message, extensions: { code } }] })

  it('shows the API’s invite-only message and a token it could not verify', () => {
    expect(googleSignInProblem(problem('FORBIDDEN', 'LearnViaNotes beta is invite-only. Ask an admin to add your email.'), fallback)).toBe(
      'LearnViaNotes beta is invite-only. Ask an admin to add your email.',
    )
    expect(googleSignInProblem(problem('UNAUTHENTICATED', 'Google sign-in could not be verified. Try again.'), fallback)).toBe(
      'Google sign-in could not be verified. Try again.',
    )
    expect(googleSignInProblem(problem('RATE_LIMITED', 'Too many sign-ins. Wait a moment.'), fallback)).toBe('Too many sign-ins. Wait a moment.')
  })

  it('keeps the generic sentence for a network error or an internal code', () => {
    expect(googleSignInProblem(new Error('network'), fallback)).toBe(fallback)
    expect(googleSignInProblem(problem('INTERNAL', 'database exploded'), fallback)).toBe(fallback)
    expect(googleSignInProblem(problem('FORBIDDEN', '   '), fallback)).toBe(fallback)
  })
})
