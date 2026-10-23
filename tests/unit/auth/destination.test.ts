import { describe, expect, it } from 'vitest'
import { afterSignIn, APP_HOME, safeNext, signedInDestination } from '@/lib/auth/destination'

describe('after sign-in', () => {
  it('asks for registration details first, keeping where the learner was going', () => {
    expect(afterSignIn({ registrationComplete: false }, '/core/python')).toBe('/sign-up/details?next=%2Fcore%2Fpython')
    expect(afterSignIn({ registrationComplete: false })).toBe('/sign-up/details')
  })

  it('opens Home when they were not headed anywhere, and keeps a deep link', () => {
    expect(afterSignIn({ registrationComplete: true }, '/verify')).toBe('/verify')
    expect(afterSignIn({ registrationComplete: true }, '/subjects/dsa')).toBe('/subjects/dsa')
    expect(afterSignIn({ registrationComplete: true }, '/profile')).toBe('/profile')
    expect(afterSignIn({ registrationComplete: true }, null)).toBe(APP_HOME)
    expect(signedInDestination('/notes?folder=abc')).toBe('/notes?folder=abc')
  })

  it('does not finish on the landing page, which would only bounce back to Home', () => {
    expect(APP_HOME).not.toBe('/')
    expect(afterSignIn({ registrationComplete: true }, '/')).toBe(APP_HOME)
    expect(afterSignIn({ registrationComplete: true }, '/?utm=newsletter')).toBe(APP_HOME)
    expect(afterSignIn({ registrationComplete: true }, '/#features')).toBe(APP_HOME)
    expect(signedInDestination('/home')).toBe('/home')
  })

  it.each(['https://evil.example', '//evil.example', '/\\evil.example', 'javascript:alert(1)', ''])('never sends people off-site via next=%j', (next) => {
    expect(safeNext(next)).toBeNull()
    expect(afterSignIn({ registrationComplete: true }, next)).toBe(APP_HOME)
  })
})
