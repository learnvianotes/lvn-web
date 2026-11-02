import { describe, expect, it } from 'vitest'
import { holdsVerification, isGated } from '@/lib/auth/gates'
import { resendVerificationNotice } from '@/lib/auth/resend'

const wait = (seconds: number) => `You can try again in ${seconds} seconds.`

describe('unverified gates', () => {
  it('holds an unconfirmed sign-in email and never a platform admin', () => {
    expect(holdsVerification(null)).toBe(false)
    expect(holdsVerification(undefined)).toBe(false)
    expect(holdsVerification({ emailVerified: true })).toBe(false)
    expect(holdsVerification({})).toBe(false)
    expect(holdsVerification({ emailVerified: false })).toBe(true)
    expect(holdsVerification({ emailVerified: false, globalRole: 'STUDENT' })).toBe(true)
    expect(holdsVerification({ emailVerified: false, globalRole: 'TEACHER' })).toBe(true)
    expect(holdsVerification({ emailVerified: false, globalRole: 'MANAGER' })).toBe(true)
    expect(holdsVerification({ emailVerified: false, globalRole: 'PLATFORM_ADMIN' })).toBe(false)
  })

  it('gates only the actions the public list names', () => {
    const viewer = { emailVerified: false, globalRole: 'STUDENT' }
    expect(isGated(viewer, ['PUBLISH_NOTE', 'FOLLOW'], 'PUBLISH_NOTE')).toBe(true)
    expect(isGated(viewer, ['PUBLISH_NOTE'], 'SHARE_NOTE')).toBe(false)
    expect(isGated(viewer, [], 'FOLLOW')).toBe(false)
    expect(isGated(viewer, null, 'FOLLOW')).toBe(false)
    expect(isGated({ emailVerified: true }, ['FOLLOW'], 'FOLLOW')).toBe(false)
    expect(isGated({ emailVerified: false, globalRole: 'PLATFORM_ADMIN' }, ['FOLLOW', 'COMMENT'], 'FOLLOW')).toBe(false)
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
