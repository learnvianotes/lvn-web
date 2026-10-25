import { describe, expect, it } from 'vitest'
import { ageHoldFromProblems } from '@/lib/age-hold'
import { ageOutcomeOf } from '@/lib/platform-api'

describe('age hold', () => {
  it('reads supportEmail from an age-restricted or blocked sign-in error', () => {
    expect(ageHoldFromProblems([{ code: 'VALIDATION', message: 'Required', supportEmail: null }])).toBeNull()
    expect(ageHoldFromProblems([{ code: 'AGE_RESTRICTED', message: 'The account could not be activated.', supportEmail: 'support@learnvianotes.in' }])).toEqual({
      supportEmail: 'support@learnvianotes.in',
      kind: 'age',
    })
    expect(ageHoldFromProblems([{ code: 'AGE_RESTRICTED', message: 'No address was included.', supportEmail: null }])).toEqual({ supportEmail: '', kind: 'age' })
    expect(ageHoldFromProblems([{ code: 'FORBIDDEN', message: 'This account is blocked.', supportEmail: 'support@learnvianotes.in' }])).toEqual({
      supportEmail: 'support@learnvianotes.in',
      kind: 'blocked',
    })
  })

  it('reads an unblocked date of birth from the returned account status', () => {
    expect(ageOutcomeOf('ACTIVE')).toBe('unblocked')
    expect(ageOutcomeOf('AGE_BLOCKED')).toBe('still_under_age')
    expect(ageOutcomeOf('BLOCKED')).toBeNull()
    expect(ageOutcomeOf('SUSPENDED')).toBeNull()
    expect(ageOutcomeOf(null)).toBeNull()
  })
})