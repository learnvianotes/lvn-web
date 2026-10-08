import { describe, expect, it } from 'vitest'
import { afterSignIn, safeNext } from '@/lib/auth/destination'

describe('after sign-in', () => {
  it('asks for registration details first, keeping where the learner was going', () => {
    expect(afterSignIn({ registrationComplete: false }, '/core/python')).toBe('/sign-up/details?next=%2Fcore%2Fpython')
    expect(afterSignIn({ registrationComplete: false })).toBe('/sign-up/details')
  })

  it('returns to the page they came from, else their profile', () => {
    expect(afterSignIn({ registrationComplete: true }, '/verify')).toBe('/verify')
    expect(afterSignIn({ registrationComplete: true }, null)).toBe('/profile')
  })

  it.each(['https://evil.example', '//evil.example', '/\\evil.example', 'javascript:alert(1)', ''])('never sends people off-site via next=%j', (next) => {
    expect(safeNext(next)).toBeNull()
    expect(afterSignIn({ registrationComplete: true }, next)).toBe('/profile')
  })
})
