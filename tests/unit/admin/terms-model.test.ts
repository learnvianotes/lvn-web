import { describe, expect, it } from 'vitest'
import { PUBLISHED_TERMS_VERSIONS, TERMS_VERSION } from '@/features/legal/documents'
import { groupSettings, isRiskyChange, SETTING_CATEGORIES, validateSetting, type SettingShape } from '@/features/admin/settings-model'
import { currentIsUnpublished, initialTermsChoice, selectableTermsVersions, termsChoiceIssue, termsRegistryGaps, TERMS_PUBLISHED_VERSIONS_KEY, TERMS_VERSION_KEY } from '@/features/admin/terms-model'

const web = [
  { version: '2026-10-08', summary: 'First.' },
  { version: '2026-11-03', summary: 'Adults only.' },
  { version: '2026-12-01', summary: 'Next.' },
]

describe('terms version picker (lvn-backend ADR-0103)', () => {
  it('offers only versions both this web build and the API publish, newest first', () => {
    expect(selectableTermsVersions(['2026-10-08', '2026-11-03'], web).map((v) => v.version)).toEqual(['2026-11-03', '2026-10-08'])
    // 2026-12-01 has text here but the API does not allow it yet; 2027-01-01 is allowed but has no text here.
    expect(selectableTermsVersions(['2026-11-03', '2027-01-01'], web).map((v) => v.version)).toEqual(['2026-11-03'])
    expect(selectableTermsVersions([], web)).toEqual([])
    expect(selectableTermsVersions(PUBLISHED_TERMS_VERSIONS.map((v) => v.version)).map((v) => v.version)).toEqual(PUBLISHED_TERMS_VERSIONS.map((v) => v.version).reverse())
    // The API's built-in allowlist is still 2026-10-08,2026-11-03 until 2026-11-12 is added there.
    expect(termsRegistryGaps(['2026-10-08', '2026-11-03']).webOnly).toEqual(['2026-11-12', '2026-11-25'])
    // The registry itself is not reordered.
    expect(web.map((v) => v.version)).toEqual(['2026-10-08', '2026-11-03', '2026-12-01'])
  })

  it('names the versions the two lists disagree on', () => {
    expect(termsRegistryGaps(['2026-10-08', '2026-11-03', '2026-12-01'], web)).toEqual({ webOnly: [], apiOnly: [] })
    expect(termsRegistryGaps(['2026-11-03', '2027-02-01', '2027-01-01'], web)).toEqual({ webOnly: ['2026-10-08', '2026-12-01'], apiOnly: ['2027-01-01', '2027-02-01'] })
  })

  it('starts on the version in effect, or on nothing when it cannot be chosen', () => {
    const selectable = selectableTermsVersions(['2026-10-08', '2026-11-03'], web)
    expect(initialTermsChoice('2026-11-03', selectable)).toBe('2026-11-03')
    expect(initialTermsChoice('2027-01-01', selectable)).toBe('')
    expect(currentIsUnpublished('2027-01-01', web)).toBe(true)
    expect(currentIsUnpublished('2026-11-03', web)).toBe(false)
    expect(currentIsUnpublished(TERMS_VERSION)).toBe(false)
  })

  it('only lets a different, selectable version be switched to', () => {
    const selectable = selectableTermsVersions(['2026-10-08', '2026-11-03'], web)
    expect(termsChoiceIssue('2026-11-03', '', selectable)).toBe('empty')
    expect(termsChoiceIssue('2026-11-03', '2026-11-03', selectable)).toBe('unchanged')
    expect(termsChoiceIssue('2026-11-03', '2026-12-01', selectable)).toBe('unavailable')
    expect(termsChoiceIssue('2026-11-03', '2026-10-08', selectable)).toBeNull()
  })
})

describe('the Legal settings category', () => {
  const termsVersion: SettingShape = { key: TERMS_VERSION_KEY, type: 'STRING', constraints: { min: null, max: null, maxLength: 10, pattern: '^\\d{4}-\\d{2}-\\d{2}$', nullable: false } }
  const published: SettingShape = { key: TERMS_PUBLISHED_VERSIONS_KEY, type: 'STRING', constraints: { min: null, max: null, maxLength: 1000, pattern: '^\\d{4}-\\d{2}-\\d{2}(,\\d{4}-\\d{2}-\\d{2})*$', nullable: false } }

  it('is a known category, listed after accounts and before ones this app does not know', () => {
    expect(SETTING_CATEGORIES).toContain('legal')
    const groups = groupSettings([
      { key: 'x', category: 'notes' },
      { key: TERMS_PUBLISHED_VERSIONS_KEY, category: 'legal' },
      { key: TERMS_VERSION_KEY, category: 'legal' },
      { key: 'account_minimum_age', category: 'accounts' },
    ])
    expect(groups.map((g) => g.category)).toEqual(['accounts', 'legal', 'notes'])
    expect(groups[1]?.settings.map((s) => s.key)).toEqual([TERMS_PUBLISHED_VERSIONS_KEY, TERMS_VERSION_KEY])
  })

  it('always confirms a change of the terms version, never an unchanged one', () => {
    expect(isRiskyChange(termsVersion, '2026-11-03', '2026-10-08')).toBe(true)
    expect(isRiskyChange(termsVersion, '2026-11-03', '2026-11-03')).toBe(false)
    // The allowlist re-prompts nobody.
    expect(isRiskyChange(published, '2026-10-08,2026-11-03', '2026-10-08,2026-11-03,2026-12-01')).toBe(false)
  })

  it('checks the API’s patterns before sending', () => {
    expect(validateSetting(termsVersion, '2026-11-03')).toBeNull()
    expect(validateSetting(termsVersion, '3 November 2026')).toBe('maxLength')
    expect(validateSetting(termsVersion, '2026/11/03')).toBe('pattern')
    expect(validateSetting(published, '2026-10-08,2026-11-03')).toBeNull()
    expect(validateSetting(published, '2026-10-08, 2026-11-03')).toBe('pattern')
  })
})
