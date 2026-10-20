import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { activeRefusal, ageOn, isAdult, isValidBirthDate, markRefused } from './age'

const today = new Date(2026, 9, 22) // 22 October 2026, local time

describe('isValidBirthDate', () => {
  it('accepts a real past date', () => {
    expect(isValidBirthDate({ year: 2000, month: 2, day: 29 }, today)).toBe(true)
  })
  it('rejects missing parts, impossible dates and the future', () => {
    expect(isValidBirthDate({}, today)).toBe(false)
    expect(isValidBirthDate({ year: 2000, month: 5 }, today)).toBe(false)
    expect(isValidBirthDate({ year: 2001, month: 2, day: 29 }, today)).toBe(false) // not a leap year
    expect(isValidBirthDate({ year: 2000, month: 4, day: 31 }, today)).toBe(false)
    expect(isValidBirthDate({ year: 2026, month: 10, day: 23 }, today)).toBe(false)
    expect(isValidBirthDate({ year: 1890, month: 1, day: 1 }, today)).toBe(false)
  })
})

describe('ageOn / isAdult', () => {
  it('turns 18 on the 18th birthday, not the day before', () => {
    expect(ageOn({ year: 2008, month: 10, day: 22 }, today)).toBe(18)
    expect(isAdult({ year: 2008, month: 10, day: 22 }, today)).toBe(true)
    expect(ageOn({ year: 2008, month: 10, day: 23 }, today)).toBe(17)
    expect(isAdult({ year: 2008, month: 10, day: 23 }, today)).toBe(false)
  })
  it('counts months, not just years', () => {
    expect(isAdult({ year: 2008, month: 11, day: 1 }, today)).toBe(false)
    expect(isAdult({ year: 2008, month: 9, day: 30 }, today)).toBe(true)
  })
  it('a 29 February birthday counts from 1 March in other years', () => {
    expect(ageOn({ year: 2008, month: 2, day: 29 }, new Date(2026, 1, 28))).toBe(17)
    expect(ageOn({ year: 2008, month: 2, day: 29 }, new Date(2026, 2, 1))).toBe(18)
  })
})

describe('refusal on this device', () => {
  const store = new Map<string, string>()
  beforeEach(() => {
    store.clear()
    vi.stubGlobal('localStorage', {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => void store.set(k, v),
      removeItem: (k: string) => void store.delete(k),
    })
  })
  afterEach(() => { vi.unstubAllGlobals() })

  it('lasts a day, then lifts', () => {
    expect(activeRefusal()).toBeNull()
    markRefused('uid-1')
    const r = activeRefusal()
    expect(r?.uid).toBe('uid-1')
    expect(activeRefusal(r!.at + 23 * 3600_000)).not.toBeNull()
    expect(activeRefusal(r!.at + 25 * 3600_000)).toBeNull()
    expect(activeRefusal()).toBeNull() // and it was cleared
  })
})
