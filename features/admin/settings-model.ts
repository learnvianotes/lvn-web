/** Client checks for platform settings, including the floor the product never crosses. */

export const SETTING_CATEGORIES = ['auth', 'verification', 'uploads', 'ai', 'search', 'accounts'] as const

export const ACCOUNT_MINIMUM_AGE_KEY = 'account_minimum_age'
export const MINIMUM_ACCOUNT_AGE = 18

export type SettingType = 'BOOLEAN' | 'INTEGER' | 'STRING'

export type SettingConstraints = {
  min: number | null
  max: number | null
  maxLength: number | null
  pattern: string | null
  nullable: boolean
}

export type SettingShape = {
  key: string
  type: SettingType
  constraints: SettingConstraints
}

export type SettingIssue = 'boolean' | 'required' | 'integer' | 'min' | 'max' | 'maxLength' | 'pattern' | 'minimumAge'

/** Turning these off, or changing an age, is confirmed before it is saved. */
const RISKY_WHEN_OFF = new Set(['google_sign_in', 'student_id_verification', 'uploads_enabled', 'ai_public_pipeline', 'search_hybrid'])
const RISKY_WHEN_CHANGED = new Set([ACCOUNT_MINIMUM_AGE_KEY, 'digital_consent_age'])

/** The lowest integer the control accepts. account_minimum_age is never below 18, whatever the server sent. */
export function effectiveIntegerMin(setting: SettingShape): number | null {
  if (setting.key === ACCOUNT_MINIMUM_AGE_KEY) return Math.max(setting.constraints.min ?? MINIMUM_ACCOUNT_AGE, MINIMUM_ACCOUNT_AGE)
  return setting.constraints.min
}

export function validateSetting(setting: SettingShape, value: string): SettingIssue | null {
  if (setting.type === 'BOOLEAN') return value === 'true' || value === 'false' ? null : 'boolean'
  if (setting.type === 'INTEGER') {
    if (value === '') return setting.constraints.nullable ? null : 'required'
    if (!/^-?\d+$/.test(value)) return 'integer'
    const n = Number(value)
    if (!Number.isSafeInteger(n)) return 'integer'
    if (setting.key === ACCOUNT_MINIMUM_AGE_KEY && n < MINIMUM_ACCOUNT_AGE) return 'minimumAge'
    const min = effectiveIntegerMin(setting)
    if (min != null && n < min) return setting.key === ACCOUNT_MINIMUM_AGE_KEY ? 'minimumAge' : 'min'
    if (setting.constraints.max != null && n > setting.constraints.max) return 'max'
    return null
  }
  if (setting.constraints.maxLength != null && [...value].length > setting.constraints.maxLength) return 'maxLength'
  if (setting.constraints.pattern) {
    let pattern: RegExp
    try {
      pattern = new RegExp(setting.constraints.pattern)
    } catch {
      return null
    }
    if (!pattern.test(value)) return 'pattern'
  }
  return null
}

/** True when saving this draft needs a confirm step. The value has not been sent yet. */
export function isRiskyChange(setting: SettingShape, previous: string, next: string): boolean {
  if (previous === next) return false
  if (RISKY_WHEN_CHANGED.has(setting.key)) return true
  return setting.type === 'BOOLEAN' && RISKY_WHEN_OFF.has(setting.key) && next === 'false'
}

export function groupSettings<T extends { category: string }>(settings: readonly T[]): { category: string; settings: T[] }[] {
  const known = new Set<string>(SETTING_CATEGORIES)
  const extras = settings.map((s) => s.category).filter((c) => !known.has(c))
  const order = [...new Set<string>([...SETTING_CATEGORIES, ...extras])]
  return order
    .map((category) => ({ category, settings: settings.filter((s) => s.category === category) }))
    .filter((group) => group.settings.length > 0)
}
