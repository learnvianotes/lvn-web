/**
 * Data shaping for the admin usage dashboard (/admin/usage). Everything here works on the aggregates the API returns
 * (lvn-backend ADR-0105, ADR-0106): no per-person rows, nothing re-identifying. Days are India Standard Time, the
 * time zone the API buckets in.
 */
import { aiRangeIssue, type AiRangeIssue } from '@/features/admin/metrics'

export const USAGE_TIME_ZONE = 'Asia/Kolkata'
const IST_OFFSET = '+05:30'
const DAY = /^\d{4}-\d{2}-\d{2}$/

export type DayRange = { from: string; to: string }
export type RangeIssue = AiRangeIssue

/** Today's date in IST, YYYY-MM-DD. */
export function istToday(now: Date = new Date()): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: USAGE_TIME_ZONE, year: 'numeric', month: '2-digit', day: '2-digit' }).format(now)
}

/** A YYYY-MM-DD day moved by `days` (calendar arithmetic, no time zone involved). */
export function addDays(day: string, days: number): string {
  const t = Date.parse(`${day}T00:00:00.000Z`) + days * 86_400_000
  return new Date(t).toISOString().slice(0, 10)
}

/** The last `days` IST days, today included. */
export function lastDays(days: number, now: Date = new Date()): DayRange {
  const to = istToday(now)
  return { from: addDays(to, -(days - 1)), to }
}

/** Both days filled, in order, and at most 366 days (the API's limit). */
export function rangeIssue(range: DayRange): RangeIssue | null {
  if (!range.from || !range.to) return 'incomplete'
  return aiRangeIssue(range.from, range.to)
}

/** GraphQL DateTime bounds for whole IST days: from 00:00 on the first day to the last millisecond of the last. */
export function rangeVariables(range: DayRange): { from: string; to: string } {
  if (!DAY.test(range.from) || !DAY.test(range.to)) throw new Error(`Not a day range: ${range.from}..${range.to}`)
  return {
    from: new Date(`${range.from}T00:00:00.000${IST_OFFSET}`).toISOString(),
    to: new Date(`${range.to}T23:59:59.999${IST_OFFSET}`).toISOString(),
  }
}

/** a / b, or null when b is 0 so an empty window never shows 0 %. */
export function share(part: number, whole: number): number | null {
  if (!whole || whole <= 0) return null
  return part / whole
}

/** The value of the bucket that starts on `day`, 0 when the series has none. */
export function valueOn<T extends { date: string }>(series: readonly T[], day: string, pick: (point: T) => number): number {
  const point = series.find((p) => p.date === day)
  return point ? pick(point) : 0
}

/** Sum of the buckets whose first day is on or after `fromDay`. */
export function sumSince<T extends { date: string }>(series: readonly T[], fromDay: string, pick: (point: T) => number): number {
  return series.reduce((total, p) => (p.date >= fromDay ? total + pick(p) : total), 0)
}

/** Rows with each one's share of the total, largest first. */
export function withShares<T>(rows: readonly T[], pick: (row: T) => number): { row: T; value: number; share: number | null }[] {
  const total = rows.reduce((sum, r) => sum + pick(r), 0)
  return [...rows].map((row) => ({ row, value: pick(row), share: share(pick(row), total) })).sort((a, b) => b.value - a.value)
}

export type FunnelRow = { name: string; users: number; ofFirst: number | null; ofPrevious: number | null }

/** Each step with its conversion from the first step and from the step before it. */
export function funnelRows(steps: readonly { name: string; users: number }[]): FunnelRow[] {
  const first = steps[0]?.users ?? 0
  return steps.map((step, i) => ({
    name: step.name,
    users: step.users,
    ofFirst: share(step.users, first),
    ofPrevious: i === 0 ? null : share(step.users, steps[i - 1]!.users),
  }))
}

/** A rounded-up axis maximum (1, 2 or 5 times a power of ten) so gridlines land on round numbers. */
export function niceMax(max: number): number {
  if (!Number.isFinite(max) || max <= 0) return 1
  const power = 10 ** Math.floor(Math.log10(max))
  for (const step of [1, 2, 5, 10]) if (max <= step * power) return step * power
  return 10 * power
}

/** SVG polyline points for values spread across `width`, 0 at the bottom of `height`. */
export function linePoints(values: readonly number[], width: number, height: number, max: number): string {
  if (!values.length) return ''
  const top = max > 0 ? max : 1
  const step = values.length > 1 ? width / (values.length - 1) : 0
  return values
    .map((v, i) => {
      const x = values.length > 1 ? i * step : width / 2
      const y = height - (Math.max(0, v) / top) * height
      return `${round(x)},${round(y)}`
    })
    .join(' ')
}

const round = (n: number) => Math.round(n * 10) / 10

/** Heatmap cell strength (0 to 1) for a retention share; out-of-range values are clamped. */
export function heat(value: number): number {
  if (!Number.isFinite(value)) return 0
  return Math.min(1, Math.max(0, value))
}

/** The widest retention row, so every cohort row has the same number of columns. */
export function retentionWidth(cohorts: readonly { returned: readonly number[] }[]): number {
  return cohorts.reduce((max, c) => Math.max(max, c.returned.length), 0)
}

// --- CSV (client-side, aggregates only) -------------------------------------------------------------------------

export type CsvCell = string | number | null | undefined
export type CsvTable = { name: string; header: string[]; rows: CsvCell[][] }

/**
 * One RFC 4180 cell. Text that a spreadsheet would run as a formula (= + - @ tab or CR first) is prefixed with an
 * apostrophe, since subject titles come from users. Numbers are written as they are.
 */
export function csvCell(value: CsvCell): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') return Number.isFinite(value) ? String(value) : ''
  const text = /^[=+\-@\t\r]/.test(value) ? `'${value}` : value
  return /[",\r\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text
}

/** A CSV document: one table, or several separated by a blank line and each headed by its name. */
export function toCsv(tables: CsvTable | readonly CsvTable[]): string {
  const list = Array.isArray(tables) ? (tables as readonly CsvTable[]) : [tables as CsvTable]
  const blocks = list.map((table) => {
    const lines = [table.header, ...table.rows].map((row) => row.map(csvCell).join(','))
    return list.length > 1 ? [csvCell(table.name), ...lines].join('\r\n') : lines.join('\r\n')
  })
  return `${blocks.join('\r\n\r\n')}\r\n`
}

/** lvn-usage-<tab>-<from>_<to>.csv */
export function csvFileName(tab: string, range?: DayRange): string {
  const safe = tab.replace(/[^a-z0-9-]+/gi, '-').toLowerCase()
  return range ? `lvn-usage-${safe}-${range.from}_${range.to}.csv` : `lvn-usage-${safe}.csv`
}

/** Save the CSV in the browser. Nothing is sent anywhere. */
export function downloadCsv(fileName: string, csv: string): void {
  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  setTimeout(() => URL.revokeObjectURL(url), 0)
}
