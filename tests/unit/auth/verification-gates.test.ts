import { describe, expect, it } from 'vitest'
import { holdsVerification, isGated, isKnownGatedAction, publicVisibilityHeld, skipsVerificationPrompt } from '@/lib/auth/gates'
import { resendVerificationNotice } from '@/lib/auth/resend'

const wait = (seconds: number) => `You can try again in ${seconds} seconds.`

describe('unverified gates', () => {
  it('uses viewerNeedsVerification when it is present, and the role when it is not', () => {
    expect(holdsVerification(null)).toBe(false)
    expect(holdsVerification(undefined)).toBe(false)
    expect(skipsVerificationPrompt({ viewerNeedsVerification: false, emailVerified: false, globalRole: 'STUDENT' })).toBe(true)
    expect(holdsVerification({ viewerNeedsVerification: false, emailVerified: false, globalRole: 'STUDENT' })).toBe(false)
    expect(holdsVerification({ viewerNeedsVerification: true, emailVerified: false, globalRole: 'STUDENT' })).toBe(true)
    expect(holdsVerification({ viewerNeedsVerification: true, emailVerified: true, globalRole: 'STUDENT' })).toBe(false)
    expect(holdsVerification({ viewerNeedsVerification: null, emailVerified: false, globalRole: 'PLATFORM_ADMIN' })).toBe(false)
    expect(holdsVerification({ viewerNeedsVerification: null, emailVerified: false, globalRole: 'STUDENT' })).toBe(true)
    expect(holdsVerification({ viewerNeedsVerification: null, emailVerified: true, globalRole: 'STUDENT' })).toBe(false)
    expect(holdsVerification({ emailVerified: false, globalRole: 'PLATFORM_ADMIN' })).toBe(false)
    expect(holdsVerification({ emailVerified: false, globalRole: 'MANAGER' })).toBe(true)
    expect(holdsVerification({ emailVerified: false })).toBe(true)
    expect(holdsVerification({})).toBe(false)
  })

  it('gates only the dotted names the public list includes', () => {
    const viewer = { emailVerified: false, globalRole: 'STUDENT', viewerNeedsVerification: true }
    expect(isGated(viewer, ['note.publish', 'note.share'], 'note.publish')).toBe(true)
    expect(isGated(viewer, ['note.publish'], 'note.share')).toBe(false)
    expect(isGated(viewer, ['note.publish', 'workshop.custom'], 'workshop.custom')).toBe(true)
    expect(isGated(viewer, ['note.publish'], 'comment')).toBe(false)
    expect(isGated(viewer, [], 'note.publish')).toBe(false)
    expect(isGated({ emailVerified: false, globalRole: 'PLATFORM_ADMIN' }, ['note.publish'], 'note.publish')).toBe(false)
    expect(isGated({ viewerNeedsVerification: false, emailVerified: false }, ['note.share'], 'note.share')).toBe(false)
    expect(isKnownGatedAction('note.publish')).toBe(true)
    expect(isKnownGatedAction('contest.enter')).toBe(true)
    expect(isKnownGatedAction('comment')).toBe(false)
    expect(isKnownGatedAction('workshop.custom')).toBe(false)
  })

  it('holds Public only when the setting is on and this person still needs to verify', () => {
    const held = { emailVerified: false, globalRole: 'STUDENT' as const }
    expect(publicVisibilityHeld(held, true)).toBe(true)
    expect(publicVisibilityHeld(held, false)).toBe(false)
    expect(publicVisibilityHeld(held, null)).toBe(false)
    expect(publicVisibilityHeld({ emailVerified: true, globalRole: 'STUDENT' }, true)).toBe(false)
    expect(publicVisibilityHeld({ viewerNeedsVerification: false, emailVerified: false }, true)).toBe(false)
  })
})

describe('resend verification', () => {
  it('keeps the API sentence and adds the wait when it is not already there', () => {
    expect(resendVerificationNotice([{ code: 'RATE_LIMITED', message: 'Please wait before asking again.', retryAfter: 60 }], wait)).toEqual({
      tone: 'error',
      message: 'Please wait before asking again. You can try again in 60 seconds.',
    })
    expect(resendVerificationNotice([{ code: 'RATE_LIMITED', message: 'Try again in 60 seconds.', retryAfter: 60 }], wait)).toEqual({
      tone: 'error',
      message: 'Try again in 60 seconds.',
    })
    expect(resendVerificationNotice([{ code: 'RATE_LIMITED', message: '', retryAfter: 30 }], wait)).toEqual({
      tone: 'error',
      message: 'You can try again in 30 seconds.',
    })
    expect(resendVerificationNotice([{ code: 'VALIDATION', message: 'Sign in first.' }], wait)).toEqual({ tone: 'error', message: 'Sign in first.' })
    expect(resendVerificationNotice([], wait)).toEqual({ tone: 'empty' })
    expect(resendVerificationNotice(null, wait)).toEqual({ tone: 'empty' })
  })
})
