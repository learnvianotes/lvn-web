import { describe, expect, it } from 'vitest'
import { AGE_MAX, AGE_MIN, ageFromBirthDate, ageRefusedAt, birthDateLimits, markAgeRefused, parseAge, REFUSED_FOR_MS } from '@/lib/age'

const memory = () => {
  const m = new Map<string, string>()
  return { getItem: (k: string) => m.get(k) ?? null, setItem: (k: string, v: string) => void m.set(k, v), removeItem: (k: string) => void m.delete(k), m }
}

describe('the refusal remembered on the device (lvn-backend ADR-0091)', () => {
  it('holds for a day, then clears itself', () => {
    const store = memory()
    expect(ageRefusedAt(1_000, store)).toBeNull()
    markAgeRefused(1_000, store)
    expect(ageRefusedAt(1_000 + REFUSED_FOR_MS - 1, store)).toBe(1_000)
    expect(ageRefusedAt(1_000 + REFUSED_FOR_MS, store)).toBeNull()
    expect(store.m.has('lvn.age-refused')).toBe(false)
  })

  it('turns Google Analytics off on the device (lvn-backend ADR-0092)', () => {
    const store = memory()
    markAgeRefused(1_000, store)
    expect(JSON.parse(store.getItem('lvn.consent')!)).toMatchObject({ analytics: 'denied' })
  })

  it('ignores a record it cannot read, or one from the future', () => {
    const store = memory()
    store.setItem('lvn.age-refused', 'not json')
    expect(ageRefusedAt(1_000, store)).toBeNull()
    markAgeRefused(5_000, store)
    expect(ageRefusedAt(1_000, store)).toBeNull()
  })
})

describe('parseAge (lvn-backend ADR-0104)', () => {
  it('reads whole years from 13 to 120, and refuses 12', () => {
    expect([AGE_MIN, AGE_MAX]).toEqual([13, 120])
    expect(parseAge('13')).toEqual({ age: 13 })
    expect(parseAge('17')).toEqual({ age: 17 })
    expect(parseAge(' 34 ')).toEqual({ age: 34 })
    expect(parseAge('120')).toEqual({ age: 120 })
    expect(parseAge('12')).toEqual({ problem: 'range' })
    expect(parseAge('8')).toEqual({ problem: 'range' })
    expect(parseAge('7')).toEqual({ problem: 'range' })
  })

  it('asks for an age when there is none', () => {
    expect(parseAge('')).toEqual({ problem: 'required' })
    expect(parseAge('   ')).toEqual({ problem: 'required' })
  })

  it('refuses anything that is not a whole number', () => {
    for (const text of ['17.5', '17,5', '1e2', '18 years', 'eighteen', '+18', '0x12', '١٨']) expect(parseAge(text)).toEqual({ problem: 'whole' })
  })

  it('refuses whole numbers outside 13 to 120', () => {
    for (const text of ['0', '7', '8', '12', '-3', '121', '999', '99999999999999999999']) expect(parseAge(text)).toEqual({ problem: 'range' })
  })
})

describe('birth dates for an account', () => {
  const now = new Date(2026, 10, 6)

  it('allows a birthday from 13 years ago back to 120 years ago, and not a day younger', () => {
    expect(birthDateLimits(now)).toEqual({ min: '1906-11-06', max: '2013-11-06' })
    expect(ageFromBirthDate('2013-11-06', now)).toBe(13)
    expect(ageFromBirthDate('2013-11-07', now)).toBe(12)
  })
})
