import { describe, expect, it } from 'vitest'
import { googleButtonVisible, isEmailLinkPending, linkedSignInMethods } from '@/lib/auth/unified'

describe('googleButtonVisible', () => {
  it('hides Continue with Google when an admin has switched it off', () => {
    expect(googleButtonVisible({ firebaseConfigured: true, googleSignInEnabled: false, signInOptionsGoogle: true })).toBe(false)
  })

  it('hides Continue with Google when this deployment has no Firebase project', () => {
    expect(googleButtonVisible({ firebaseConfigured: false, googleSignInEnabled: true, signInOptionsGoogle: true })).toBe(false)
  })

  it('shows it only when Firebase is configured and the admin left it on', () => {
    expect(googleButtonVisible({ firebaseConfigured: true, googleSignInEnabled: true })).toBe(true)
  })

  it('keeps the older signInOptions flag when authSettings cannot be read', () => {
    expect(googleButtonVisible({ firebaseConfigured: true, googleSignInEnabled: undefined, signInOptionsGoogle: true, authSettingsFailed: true })).toBe(true)
    expect(googleButtonVisible({ firebaseConfigured: true, googleSignInEnabled: undefined, signInOptionsGoogle: false, authSettingsFailed: true })).toBe(false)
  })
})

describe('isEmailLinkPending', () => {
  it('is the check-your-email case when sign-up returns the flag and no session', () => {
    expect(isEmailLinkPending({ emailLinkPending: true, session: null, userErrors: [] })).toBe(true)
  })

  it('stays the existing sign-in conflict when the account already has a password', () => {
    expect(isEmailLinkPending({ emailLinkPending: false, session: null, userErrors: [{ code: 'CONFLICT' }] })).toBe(false)
    expect(isEmailLinkPending({ emailLinkPending: true, session: null, userErrors: [{ code: 'CONFLICT' }] })).toBe(false)
  })

  it('is not pending once a session exists', () => {
    expect(isEmailLinkPending({ emailLinkPending: true, session: { accessToken: 'h.p.s' }, userErrors: [] })).toBe(false)
  })
})

describe('linkedSignInMethods', () => {
  it('lists the signed-in user’s methods in a stable order', () => {
    expect(linkedSignInMethods(['GITHUB', 'EMAIL', 'GOOGLE'])).toEqual(['EMAIL', 'GOOGLE', 'GITHUB'])
  })

  it('lists nothing when the sign-in response left them null', () => {
    expect(linkedSignInMethods(null)).toEqual([])
    expect(linkedSignInMethods(undefined)).toEqual([])
  })
})
