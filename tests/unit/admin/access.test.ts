import { describe, expect, it } from 'vitest'
import { formatAddedOn, parseAllowlistEmails } from '@/features/admin/access-model'
import { formatResetsAt, publicPlanPrice, usageRatio, usageText } from '@/features/plans/model'
import { isLimitCode, refusalMessage } from '@/lib/limit-error'
import { CombinedGraphQLErrors } from '@apollo/client/errors'

describe('beta allowlist emails', () => {
  it('accepts one address or many, lowercased, and skips duplicates', () => {
    expect(parseAllowlistEmails('  Asha@College.edu ')).toEqual({ ok: ['asha@college.edu'], invalid: [] })
    expect(parseAllowlistEmails('a@b.co, A@b.co\nnew@example.com; bad')).toEqual({
      ok: ['a@b.co', 'new@example.com'],
      invalid: ['bad'],
    })
    expect(parseAllowlistEmails('   ')).toEqual({ ok: [], invalid: [] })
  })

  it('formats the day an address was added', () => {
    expect(formatAddedOn('2026-10-02T00:00:00.000Z')).toMatch(/2026/)
    expect(formatAddedOn('not-a-date')).toBe('not-a-date')
  })
})

describe('plan prices and usage', () => {
  const per = { month: 'month', year: 'year' }
  it('shows Free for a zero price and rupees otherwise', () => {
    expect(publicPlanPrice(0, 'INR', 'NONE', per, 'Free')).toBe('Free')
    expect(publicPlanPrice(49900, 'INR', 'MONTH', per, 'Free')).toMatch(/₹\s?499\/month/)
  })

  it('describes used of limit, unlimited, and a daily reset', () => {
    expect(usageRatio('12', '20')).toBeCloseTo(0.6)
    expect(usageRatio('40', '20')).toBe(1)
    expect(usageRatio('3', null)).toBeNull()
    expect(usageText('12', '20', 'Unlimited')).toBe('12 / 20')
    expect(usageText('3', null, 'Unlimited')).toBe('Unlimited')
    expect(formatResetsAt('2026-10-24T00:00:00.000Z')).toMatch(/2026/)
  })
})

describe('limit refusals', () => {
  it('keeps the API message for a plan limit and an invite-only refusal', () => {
    expect(isLimitCode('RATE_LIMITED')).toBe(true)
    expect(isLimitCode('FORBIDDEN')).toBe(true)
    expect(isLimitCode('VALIDATION')).toBe(false)
    const error = new CombinedGraphQLErrors({
      errors: [{ message: "You've reached your plan's limit for notes.", extensions: { code: 'FORBIDDEN' } }],
    })
    expect(refusalMessage(error)).toBe("You've reached your plan's limit for notes.")
    expect(refusalMessage(new Error('network'))).toBeNull()
  })
})
