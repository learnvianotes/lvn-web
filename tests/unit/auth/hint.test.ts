import { describe, expect, it } from 'vitest'
import { landingHoldScript, shouldHoldLanding, SIGNED_IN_HINT_KEY } from '@/lib/auth/hint'

describe('the landing hold', () => {
  it('hides / only when this browser has signed in', () => {
    expect(shouldHoldLanding('/', '1')).toBe(true)
    expect(shouldHoldLanding('/', null)).toBe(false)
    expect(shouldHoldLanding('/', '0')).toBe(false)
    expect(shouldHoldLanding('/home', '1')).toBe(false)
    expect(shouldHoldLanding('/subjects', '1')).toBe(false)
  })

  it('the head script hides / before paint, and only then', () => {
    const script = landingHoldScript()
    expect(script).toContain(`localStorage.getItem(${JSON.stringify(SIGNED_IN_HINT_KEY)})`)
    expect(script).toContain("location.pathname==='/'")
    expect(script).toContain("dataset.landing='away'")
    expect(script).toContain("style.visibility='hidden'")
    expect(script).not.toContain('/home')
  })
})
