import { describe, expect, it } from 'vitest'
import { filterModels, groupModels, modelsForUse, pickerModels, presetsAsModels, routeModelUse, type ListedModel } from '@/features/ai/admin/catalog'
import { aiRangeIssue, aiRangeVariables, failureRate, formatBytes, formatDecimal, microUsdToUsd, providerLabel } from '@/features/admin/metrics'
import { currencyIssue, deleteChoice, entitlementIssues, formatPlanPrice, isFreePlan, majorToMinor, minorUnitsText, planCodeIssue, priceMinorIssue } from '@/features/admin/plans-model'
import { effectiveIntegerMin, groupSettings, isRiskyChange, validateSetting, type SettingShape } from '@/features/admin/settings-model'

const setting = (over: Partial<SettingShape> & Pick<SettingShape, 'key' | 'type'>): SettingShape => ({
  key: over.key,
  type: over.type,
  constraints: { min: null, max: null, maxLength: null, pattern: null, nullable: false, ...over.constraints },
})

describe('admin metrics', () => {
  it('keeps an AI window to 366 days and turns days into DateTime bounds', () => {
    expect(aiRangeIssue('', '')).toBeNull()
    expect(aiRangeIssue('2026-10-01', '')).toBe('incomplete')
    expect(aiRangeIssue('2026-10-23', '2026-10-01')).toBe('order')
    expect(aiRangeIssue('2024-01-01', '2024-12-31')).toBeNull()
    expect(aiRangeIssue('2024-01-01', '2025-01-01')).toBe('span')
    expect(aiRangeVariables('2026-10-01', '2026-10-23')).toEqual({ from: '2026-10-01T00:00:00.000Z', to: '2026-10-23T23:59:59.999Z' })
    expect(aiRangeVariables('', '')).toBeUndefined()
    expect(aiRangeVariables('2024-01-01', '2025-01-01')).toBeUndefined()
  })

  it('formats tokens, micro-USD, bytes and failure rate', () => {
    expect(formatDecimal('84200120')).toBe('84,200,120')
    expect(formatDecimal('12.5')).toBe('12.5')
    expect(formatDecimal('n/a')).toBe('n/a')
    expect(microUsdToUsd('18650000')).toBe(18.65)
    expect(microUsdToUsd('1250000')).toBe(1.25)
    expect(microUsdToUsd('nope')).toBeNull()
    expect(formatBytes('0')).toBe('0 B')
    expect(formatBytes('1536')).toBe('1.5 KB')
    expect(formatBytes('12884901888')).toBe('12 GB')
    expect(failureRate(0, 0)).toBe(0)
    expect(failureRate(210, 18420)).toBeCloseTo(0.0114, 4)
    expect(providerLabel('ANTHROPIC')).toBe('Anthropic')
    expect(providerLabel('OpenAI')).toBe('OpenAI')
  })
})

describe('admin settings', () => {
  const age = setting({ key: 'account_minimum_age', type: 'INTEGER', constraints: { min: 0, max: 120, maxLength: null, pattern: null, nullable: false } })
  const uploads = setting({ key: 'uploads_enabled', type: 'BOOLEAN' })
  const budget = setting({ key: 'ai_monthly_budget_micro_usd', type: 'INTEGER', constraints: { min: null, max: null, maxLength: null, pattern: null, nullable: true } })

  it('never accepts an account minimum age below 18', () => {
    expect(effectiveIntegerMin(age)).toBe(18)
    expect(validateSetting(age, '17')).toBe('minimumAge')
    expect(validateSetting(age, '18')).toBeNull()
    expect(validateSetting(age, '21')).toBeNull()
    expect(validateSetting(age, '121')).toBe('max')
    expect(validateSetting(age, '')).toBe('required')
    expect(validateSetting(budget, '')).toBeNull()
    expect(validateSetting(budget, '1.5')).toBe('integer')
  })

  it('checks strings and confirms risky changes before they are saved', () => {
    const code = setting({ key: 'site_code', type: 'STRING', constraints: { min: null, max: null, maxLength: 4, pattern: '^[a-z]+$', nullable: false } })
    expect(validateSetting(code, 'abcd')).toBeNull()
    expect(validateSetting(code, 'abcde')).toBe('maxLength')
    expect(validateSetting(code, 'AB')).toBe('pattern')
    expect(isRiskyChange(uploads, 'true', 'false')).toBe(true)
    expect(isRiskyChange(uploads, 'false', 'true')).toBe(false)
    expect(isRiskyChange(uploads, 'true', 'true')).toBe(false)
    expect(isRiskyChange(age, '18', '21')).toBe(true)
    expect(isRiskyChange(budget, '1', '2')).toBe(false)
  })

  it('groups settings in category order and keeps unknown categories', () => {
    const groups = groupSettings([
      { category: 'search', key: 'search_hybrid' },
      { category: 'auth', key: 'google_sign_in' },
      { category: 'billing', key: 'extra' },
    ])
    expect(groups.map((group) => group.category)).toEqual(['auth', 'search', 'billing'])
  })
})

describe('admin plans', () => {
  it('shows minor units as money and stores what the admin typed', () => {
    expect(formatPlanPrice(49900, 'INR', 'MONTH', { month: 'month', year: 'year' })).toMatch(/₹\s?499\/month/)
    expect(formatPlanPrice(499900, 'INR', 'YEAR', { month: 'month', year: 'year' })).toMatch(/₹\s?4,999\/year/)
    expect(majorToMinor('499', 'INR')).toBe(49900)
    expect(majorToMinor('499.5', 'INR')).toBe(49950)
    expect(majorToMinor('499.501', 'INR')).toBeNull()
    expect(minorUnitsText(49900, 'INR')).toBe('499')
    expect(minorUnitsText(49950, 'INR')).toBe('499.5')
    expect(priceMinorIssue(0)).toBeNull()
    expect(priceMinorIssue(2_000_000_001)).toBe('range')
    expect(currencyIssue('INR')).toBeNull()
    expect(currencyIssue('RUPEE')).toBe('currency')
  })

  it('keeps FREE, and will not delete a plan people are on', () => {
    expect(planCodeIssue('plus')).toBeNull()
    expect(planCodeIssue('A')).toBe('format')
    expect(planCodeIssue('1AB')).toBe('format')
    expect(isFreePlan('free')).toBe(true)
    expect(deleteChoice({ code: 'FREE', subscriberCount: 0 })).toBe('blocked')
    expect(deleteChoice({ code: 'PLUS', subscriberCount: 42 })).toBe('deactivate')
    expect(deleteChoice({ code: 'CAMPUS', subscriberCount: 0 })).toBe('delete')
    expect(entitlementIssues([{ key: 'STORAGE_BYTES', limit: '', role: '' }])).toBeNull()
    expect(entitlementIssues([{ key: 'STORAGE_BYTES', limit: 'nope', role: '' }])).toBe('limit')
    expect(entitlementIssues([{ key: '', limit: '', role: '' }])).toBe('key')
    expect(entitlementIssues([
      { key: 'STORAGE_BYTES', limit: '', role: '' },
      { key: 'STORAGE_BYTES', limit: '1', role: 'STUDENT' },
    ])).toBe('duplicate')
  })
})

describe('AI model pickers', () => {
  const chat: ListedModel = { id: 'gemini-3.8-flash', kind: 'CHAT', supports: ['CHAT', 'TRANSCRIBE'] }
  const pro: ListedModel = { id: 'gemini-2.5-pro', kind: 'CHAT', supports: ['CHAT'] }
  const embed: ListedModel = { id: 'text-embedding-004', kind: 'EMBEDDING', supports: ['EMBEDDING'] }
  const speech: ListedModel = { id: 'gemini-tts', kind: 'TTS', supports: ['TTS'] }
  const pickers = [
    { use: 'CHAT' as const, models: [chat, pro] },
    { use: 'EMBEDDING' as const, models: [embed] },
    { use: 'TRANSCRIBE' as const, models: [chat] },
    { use: 'TTS' as const, models: [speech] },
    { use: 'IMAGE' as const, models: [] },
  ]

  it('offers only the models that support that use, and hides an empty picker', () => {
    expect(routeModelUse('SUMMARIZE')).toBe('CHAT')
    expect(routeModelUse('EMBED')).toBe('EMBEDDING')
    expect(routeModelUse('TRANSCRIBE')).toBe('TRANSCRIBE')
    expect(modelsForUse(pickers, 'CHAT').map((model) => model.id)).toEqual(['gemini-3.8-flash', 'gemini-2.5-pro'])
    expect(modelsForUse(pickers, 'EMBEDDING').map((model) => model.id)).toEqual(['text-embedding-004'])
    expect(modelsForUse(pickers, 'TRANSCRIBE').map((model) => model.id)).not.toContain('text-embedding-004')
    expect(modelsForUse(pickers, 'IMAGE')).toEqual([])
    expect(pickerModels([])).toBeNull()
    expect(pickerModels(modelsForUse(pickers, 'CHAT'))?.map((model) => model.id)).toContain('gemini-2.5-pro')
  })

  it('sorts by kind and filters by the search text', () => {
    const groups = groupModels([speech, embed, chat, pro])
    expect(groups.map((group) => group.kind)).toEqual(['CHAT', 'EMBEDDING', 'TTS'])
    expect(groups[0]?.models.map((model) => model.id)).toEqual(['gemini-2.5-pro', 'gemini-3.8-flash'])
    expect(filterModels([chat, pro, embed], 'embed').map((model) => model.id)).toEqual(['text-embedding-004'])
    expect(presetsAsModels(['gemma4'], 'CHAT')).toEqual([{ id: 'gemma4', kind: 'CHAT', supports: ['CHAT'] }])
  })
})
