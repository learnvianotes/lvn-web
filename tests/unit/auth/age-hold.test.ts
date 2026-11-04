import { describe, expect, it } from 'vitest'
import { ageHoldFromProblems } from '@/lib/age-hold'
import { ageEditOf, ageOutcomeOf } from '@/lib/platform-api'

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

  it('reads an unblocked age or date of birth from the returned account status', () => {
    expect(ageOutcomeOf('ACTIVE')).toBe('unblocked')
    expect(ageOutcomeOf('AGE_BLOCKED')).toBe('still_under_age')
    expect(ageOutcomeOf('BLOCKED')).toBeNull()
    expect(ageOutcomeOf('SUSPENDED')).toBeNull()
    expect(ageOutcomeOf(null)).toBeNull()
  })
})

describe('an admin’s age correction (lvn-backend ADR-0104)', () => {
  const declared = { age: 12, dateOfBirth: null }
  const born = { age: 22, dateOfBirth: '2004-05-01' }

  it('sends a new age for an account without a date of birth, and only when it changed', () => {
    expect(ageEditOf(declared, { age: '22', dateOfBirth: '' })).toEqual({ age: 22 })
    expect(ageEditOf(declared, { age: ' 12 ', dateOfBirth: '' })).toEqual({})
  })

  it('never sends an age for an account whose date of birth decides it, only a changed date', () => {
    expect(ageEditOf(born, { age: '30', dateOfBirth: '2004-05-01' })).toEqual({})
    expect(ageEditOf(born, { age: '', dateOfBirth: '2003-05-01' })).toEqual({ dateOfBirth: '2003-05-01' })
  })

  it('leaves an account that never gave an age alone, and refuses an age that is not one', () => {
    expect(ageEditOf({ age: null, dateOfBirth: null }, { age: '', dateOfBirth: '' })).toEqual({})
    expect(ageEditOf({ age: null, dateOfBirth: null }, { age: '40', dateOfBirth: '' })).toEqual({ age: 40 })
    for (const age of ['', '17.5', '0', '121', 'abc']) expect(ageEditOf(declared, { age, dateOfBirth: '' })).toBe('invalid')
  })
})