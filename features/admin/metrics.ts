/** Figures on the admin overview. Costs arrive as micro-USD; storage as a decimal byte string. */

export const AI_RANGE_MAX_DAYS = 366

export type AiRangeIssue = 'incomplete' | 'order' | 'span'

const DAY = /^\d{4}-\d{2}-\d{2}$/

/** Empty inputs mean the API's default window (the last 30 days). A chosen window is at most 366 days. */
export function aiRangeIssue(from: string, to: string): AiRangeIssue | null {
  if (!from && !to) return null
  if (!DAY.test(from) || !DAY.test(to)) return 'incomplete'
  if (from > to) return 'order'
  const start = Date.parse(`${from}T00:00:00.000Z`)
  const end = Date.parse(`${to}T00:00:00.000Z`)
  if (Number.isNaN(start) || Number.isNaN(end)) return 'incomplete'
  const days = Math.round((end - start) / 86_400_000) + 1
  if (days > AI_RANGE_MAX_DAYS) return 'span'
  return null
}

/** GraphQL DateTime bounds for a valid day window. Empty when the default window should be used. */
export function aiRangeVariables(from: string, to: string): { from: string; to: string } | undefined {
  if (aiRangeIssue(from, to) || !from || !to) return undefined
  return { from: `${from}T00:00:00.000Z`, to: `${to}T23:59:59.999Z` }
}

/** Failures divided by tasks. Zero when nothing ran, so the rate is never invented from an empty window. */
export function failureRate(failures: number, tasks: number): number {
  if (tasks <= 0) return 0
  return failures / tasks
}

/** Group a decimal string (token totals) without passing it through a float. */
export function formatDecimal(value: string): string {
  const trimmed = value.trim()
  if (!/^-?\d+(\.\d+)?$/.test(trimmed)) return value
  const negative = trimmed.startsWith('-')
  const [int, frac] = trimmed.replace(/^-/, '').split('.')
  const grouped = int!.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const body = frac !== undefined ? `${grouped}.${frac}` : grouped
  return negative ? `-${body}` : body
}

/** micro-USD (1e-6 USD) as a number of dollars, or null when the string is not a decimal. */
export function microUsdToUsd(micro: string): number | null {
  const trimmed = micro.trim()
  if (!/^-?\d+(\.\d+)?$/.test(trimmed)) return null
  const n = Number(trimmed)
  if (!Number.isFinite(n)) return null
  return n / 1_000_000
}

const BYTE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

/** A decimal byte string as a short size, in steps of 1024. */
export function formatBytes(raw: string): string {
  if (!/^\d+$/.test(raw)) return raw
  let n = BigInt(raw)
  let i = 0
  while (n >= 1024n && i < BYTE_UNITS.length - 1) {
    const next = n / 1024n
    if (next < 1024n || i === BYTE_UNITS.length - 2) {
      const scaled = (n * 10n) / 1024n
      const whole = scaled / 10n
      const frac = scaled % 10n
      const unit = BYTE_UNITS[i + 1]
      return frac === 0n ? `${whole} ${unit}` : `${whole}.${frac} ${unit}`
    }
    n = next
    i += 1
  }
  return `${n} ${BYTE_UNITS[i]}`
}

/** ALL CAPS provider ids read as a name; mixed-case ids are already a name. */
export function providerLabel(provider: string): string {
  if (!provider || provider !== provider.toUpperCase()) return provider
  return provider.charAt(0) + provider.slice(1).toLowerCase()
}
