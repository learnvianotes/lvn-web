import { describe, expect, it } from 'vitest'
import { ageHoldFromProblems } from '@/lib/age-hold'
import { ageRecheckOf } from '@/lib/platform-api'

describe('age hold', () => {
  it('reads the support address from an AGE_RESTRICTED or AGE_BLOCKED error', () => {
    expect(ageHoldFromProblems([{ code: 'VALIDATION', message: 'Required' }])).toBeNull()
    expect(ageHoldFromProblems([{ code: 'AGE_RESTRICTED', message: 'Write to support@learnvianotes.in if this is wrong.' }])).toEqual({
      supportEmail: 'support@learnvianotes.in',
    })
    expect(ageHoldFromProblems([{ code: 'AGE_BLOCKED', message: 'Blocked. No address was included.' }])).toEqual({ supportEmail: '' })
  })

  it('maps the age re-check to unblocked or still under age', () => {
    expect(ageRecheckOf('UNBLOCKED', 'AGE_BLOCKED')).toBe('unblocked')
    expect(ageRecheckOf('STILL_UNDER_AGE', 'ACTIVE')).toBe('still_under_age')
    expect(ageRecheckOf(null, 'ACTIVE')).toBe('unblocked')
    expect(ageRecheckOf(null, 'AGE_BLOCKED')).toBe('still_under_age')
    expect(ageRecheckOf(null, 'BLOCKED')).toBeNull()
  })
})