import { describe, expect, it } from 'vitest'
import { activityWindow, paramsFromDraft, presetRange, utcDayKey } from '@/features/admin/activity'
import { adminVerifyPath, classifyMfaProblem, isAdminMfaRole } from '@/lib/auth/mfa'

describe('admin email code', () => {
  it('is only for platform admins and managers', () => {
    expect(isAdminMfaRole('PLATFORM_ADMIN')).toBe(true)
    expect(isAdminMfaRole('MANAGER')).toBe(true)
    expect(isAdminMfaRole('TEACHER')).toBe(false)
    expect(isAdminMfaRole('STUDENT')).toBe(false)
    expect(isAdminMfaRole(null)).toBe(false)
    expect(isAdminMfaRole(undefined)).toBe(false)
  })

  it('names a wrong, expired, locked or rate-limited code', () => {
    expect(classifyMfaProblem('That code is incorrect.', 'VALIDATION')).toBe('wrong')
    expect(classifyMfaProblem('This code is not valid.', 'VALIDATION')).toBe('wrong')
    expect(classifyMfaProblem('This code has expired. Ask for a new one.', 'VALIDATION')).toBe('expired')
    expect(classifyMfaProblem('Too many attempts. Ask for a new code.', 'VALIDATION')).toBe('locked')
    expect(classifyMfaProblem('This code has already been used.', 'VALIDATION')).toBe('used')
    expect(classifyMfaProblem('Too many codes. Try again later.', 'RATE_LIMITED')).toBe('rate')
    expect(classifyMfaProblem('This sign-in factor is not available yet.', 'VALIDATION')).toBe('other')
  })

  it('keeps the return path on this site', () => {
    expect(adminVerifyPath('/admin/users')).toBe('/admin/verify?next=%2Fadmin%2Fusers')
    expect(adminVerifyPath('https://evil.example')).toBe('/admin/verify?next=%2Fadmin')
    expect(adminVerifyPath('/admin/verify?next=%2Fadmin%2Fplans')).toBe('/admin/verify?next=%2Fadmin%2Fplans')
  })
})

describe('activity window', () => {
  const now = new Date('2026-11-17T08:00:00.000Z')

  it('uses the last 30 days when the URL has no dates', () => {
    const parsed = activityWindow({ action: ' settings.updated ', actor: '', target: ' User ', from: '', to: '' }, now)
    expect(parsed).toMatchObject({
      window: {
        from: '2026-10-18T08:00:00.000Z',
        to: '2026-11-17T08:00:00.000Z',
        filter: { action: 'settings.updated', targetType: 'User', from: '2026-10-18T08:00:00.000Z', to: '2026-11-17T08:00:00.000Z' },
      },
    })
  })

  it('refuses an actor id that is not an account id, and a range longer than 366 days', () => {
    expect(activityWindow({ action: '', actor: 'asha@example.com', target: '', from: '', to: '' }, now)).toEqual({ issue: 'actor' })
    expect(activityWindow({ action: '', actor: '', target: '', from: '2025-01-01', to: '2026-11-17' }, now)).toEqual({ issue: 'range' })
    expect(activityWindow({ action: '', actor: '', target: '', from: '2026-11-17', to: '2026-11-01' }, now)).toEqual({ issue: 'order' })
  })

  it('writes filters back to the query string and labels UTC days', () => {
    expect(paramsFromDraft({ action: 'mfa.verified', actor: '', target: '', from: '2026-11-01', to: '' })).toBe('action=mfa.verified&from=2026-11-01')
    expect(presetRange(7, new Date(2026, 10, 17)).from <= presetRange(7, new Date(2026, 10, 17)).to).toBe(true)
    expect(utcDayKey('2026-11-01T00:00:00.000Z')).toBe('2026-11-01')
  })
})
