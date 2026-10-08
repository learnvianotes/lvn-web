import { describe, expect, it, vi } from 'vitest'
import { applyProblems } from '@/components/auth/forms'

describe('applyProblems', () => {
  it('puts field errors on their fields and returns the rest for an alert', () => {
    const setError = vi.fn()
    const general = applyProblems(
      [
        { field: ['input', 'email'], message: 'An account with this email already exists.', code: 'CONFLICT' },
        { field: null, message: 'Too many attempts.', code: 'RATE_LIMITED' },
        { field: ['input', 'unknownField'], message: 'Ignored as a field.', code: 'VALIDATION' },
      ],
      setError,
      ['email', 'password'] as const,
    )
    expect(setError).toHaveBeenCalledTimes(1)
    expect(setError).toHaveBeenCalledWith('email', { type: 'server', message: 'An account with this email already exists.' })
    expect(general).toBe('Too many attempts.')
  })
})
