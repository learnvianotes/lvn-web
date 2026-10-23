/** Plan codes, prices and the delete rules. Saving a price charges nobody; that is a server fact the page repeats. */

import type { GlobalRole, LimitKey, PlanInterval } from '@/graphql/generated/graphql'

export const PRICE_MINOR_MAX = 2_000_000_000
export const PLAN_CODE = /^[A-Z][A-Z0-9_]{1,31}$/
export const FREE_PLAN_CODE = 'FREE'

export const LIMIT_KEYS = [
  'AI_TOKENS_DAILY',
  'CLASSROOMS_OWNED',
  'CLASSROOM_MEMBERS',
  'EXPORTS_DAILY',
  'GROUPS_OWNED',
  'GROUP_MEMBERS',
  'IMPORTS_DAILY',
  'ORG_SEATS',
  'PDF_PAGES_MONTHLY',
  'PROJECT_WORKSPACES',
  'STORAGE_BYTES',
] as const satisfies readonly LimitKey[]

export function normalizePlanCode(code: string): string {
  return code.trim().toUpperCase()
}

export function isFreePlan(code: string): boolean {
  return normalizePlanCode(code) === FREE_PLAN_CODE
}

export function planCodeIssue(code: string): 'format' | null {
  return PLAN_CODE.test(normalizePlanCode(code)) ? null : 'format'
}

export function currencyDigits(currency: string): number {
  try {
    return new Intl.NumberFormat('en', { style: 'currency', currency: currency.toUpperCase() }).resolvedOptions().maximumFractionDigits ?? 2
  } catch {
    return 2
  }
}

export function currencyIssue(currency: string): 'currency' | null {
  const code = currency.trim().toUpperCase()
  if (!/^[A-Z]{3}$/.test(code)) return 'currency'
  try {
    new Intl.NumberFormat('en', { style: 'currency', currency: code }).format(0)
    return null
  } catch {
    return 'currency'
  }
}

/** Major units the admin typed ("499" or "499.50") as minor units, or null when the text is not that currency's money. */
export function majorToMinor(major: string, currency: string): number | null {
  const trimmed = major.trim()
  if (!/^\d+(\.\d+)?$/.test(trimmed)) return null
  const digits = currencyDigits(currency)
  const [whole, frac = ''] = trimmed.split('.')
  if (frac.length > digits) return null
  const combined = `${whole}${frac.padEnd(digits, '0')}`.replace(/^0+(?=\d)/, '')
  const n = Number(combined)
  if (!Number.isSafeInteger(n)) return null
  return n
}

export function minorToMajor(minor: number, currency: string): number {
  return minor / 10 ** currencyDigits(currency)
}

/** Major-unit text for an edit field: 49900 INR is "499", 49950 INR is "499.5". */
export function minorUnitsText(minor: number, currency: string): string {
  const digits = currencyDigits(currency)
  return minorToMajor(minor, currency)
    .toFixed(digits)
    .replace(/\.0+$/, '')
    .replace(/(\.\d*[1-9])0+$/, '$1')
}

export function priceMinorIssue(minor: number | null): 'price' | 'range' | null {
  if (minor == null || minor < 0) return 'price'
  if (minor > PRICE_MINOR_MAX) return 'range'
  return null
}

/** ₹499/month from 49900 minor units of INR. The suffix is the untranslated unit word ("month"). */
export function formatPlanPrice(minor: number, currency: string, interval: PlanInterval, per: { month: string; year: string }): string {
  const code = currency.trim().toUpperCase()
  let amount: string
  try {
    amount = new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: code,
      minimumFractionDigits: 0,
      maximumFractionDigits: currencyDigits(code),
    }).format(minorToMajor(minor, code))
  } catch {
    amount = `${minor} ${code}`
  }
  if (interval === 'MONTH') return `${amount}/${per.month}`
  if (interval === 'YEAR') return `${amount}/${per.year}`
  return amount
}

export type DeleteChoice = 'delete' | 'deactivate' | 'blocked'

/** FREE stays. A plan people are on is deactivated, not deleted. */
export function deleteChoice(plan: { code: string; subscriberCount: number }): DeleteChoice {
  if (isFreePlan(plan.code)) return 'blocked'
  if (plan.subscriberCount > 0) return 'deactivate'
  return 'delete'
}

export function canDeactivate(plan: { code: string }): boolean {
  return !isFreePlan(plan.code)
}

export function entitlementLimitIssue(limit: string): 'limit' | null {
  const trimmed = limit.trim()
  if (!trimmed) return null
  return /^\d+(\.\d+)?$/.test(trimmed) ? null : 'limit'
}

export type EntitlementDraft = { key: LimitKey | ''; limit: string; role: GlobalRole | '' }

export function entitlementIssues(rows: readonly EntitlementDraft[]): 'key' | 'limit' | 'duplicate' | null {
  const seen = new Set<string>()
  for (const row of rows) {
    if (!row.key) return 'key'
    if (seen.has(row.key)) return 'duplicate'
    seen.add(row.key)
    if (entitlementLimitIssue(row.limit)) return 'limit'
  }
  return null
}
