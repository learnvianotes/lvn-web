/**
 * The small things that make the notes app feel alive and personal: an accent colour per note (stable, from its id),
 * a greeting for the time of day, and reading time.
 */

/** Soft accents from the brand palette (ui-reference: one blue accent, warm tints for tiles; no purples, ADR-0094). */
export const ACCENTS = [
  { name: 'blue', from: '#3B82F6', to: '#93C5FD', tint: 'rgb(59 130 246 / 0.10)' },
  { name: 'teal', from: '#14B8A6', to: '#5EEAD4', tint: 'rgb(20 184 166 / 0.10)' },
  { name: 'sky', from: '#0EA5E9', to: '#7DD3FC', tint: 'rgb(14 165 233 / 0.10)' },
  { name: 'emerald', from: '#10B981', to: '#6EE7B7', tint: 'rgb(16 185 129 / 0.10)' },
  { name: 'amber', from: '#F59E0B', to: '#FCD34D', tint: 'rgb(245 158 11 / 0.12)' },
  { name: 'rose', from: '#F43F5E', to: '#FDA4AF', tint: 'rgb(244 63 94 / 0.10)' },
] as const

export function accentOf(id: string) {
  let h = 0
  for (const c of id.replace(/-/g, '').slice(-8)) h = (h * 31 + c.charCodeAt(0)) >>> 0
  return ACCENTS[h % ACCENTS.length]!
}

export type Daypart = 'morning' | 'afternoon' | 'evening' | 'night'

export function daypart(date = new Date()): Daypart {
  const h = date.getHours()
  return h < 5 ? 'night' : h < 12 ? 'morning' : h < 17 ? 'afternoon' : h < 22 ? 'evening' : 'night'
}

/** Minutes to read, at 200 words a minute; at least 1 for anything with words. */
export function readingMinutes(text: string): number {
  const words = text.trim().split(/\s+/).filter(Boolean).length
  return words ? Math.max(1, Math.round(words / 200)) : 0
}

/** "edited 5 minutes ago" without a library. */
export function ago(iso: string | null | undefined, locale = 'en'): string {
  if (!iso) return ''
  const seconds = (new Date(iso).getTime() - Date.now()) / 1000
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })
  for (const [unit, size] of [['year', 31536000], ['month', 2592000], ['week', 604800], ['day', 86400], ['hour', 3600], ['minute', 60]] as const) {
    if (Math.abs(seconds) >= size) return rtf.format(Math.round(seconds / size), unit)
  }
  return rtf.format(0, 'minute')
}
