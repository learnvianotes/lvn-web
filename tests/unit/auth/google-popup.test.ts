import { describe, expect, it } from 'vitest'
import { googlePopupOutcome } from '@/lib/auth/google'

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
