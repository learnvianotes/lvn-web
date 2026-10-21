import { describe, expect, it } from 'vitest'
import { ageRefusedAt, birthDateInWords, markAgeRefused, REFUSED_FOR_MS } from '@/lib/age'

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
    expect(store.m.size).toBe(0)
  })

  it('ignores a record it cannot read, or one from the future', () => {
    const store = memory()
    store.setItem('lvn.age-refused', 'not json')
    expect(ageRefusedAt(1_000, store)).toBeNull()
    markAgeRefused(5_000, store)
    expect(ageRefusedAt(1_000, store)).toBeNull()
  })
})

describe('birthDateInWords', () => {
  it('spells the date out, so a wrong year stands out', () => {
    expect(birthDateInWords('2001-03-14')).toBe('14 March 2001')
    expect(birthDateInWords('2004-02-29')).toBe('29 February 2004')
  })

  it('is empty for anything that is not a real date', () => {
    expect(birthDateInWords('')).toBe('')
    expect(birthDateInWords('2003-02-29')).toBe('')
    expect(birthDateInWords('14/03/2001')).toBe('')
  })
})
