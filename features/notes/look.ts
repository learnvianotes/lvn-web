/**
 * The small things that make the notes app feel alive and personal: an accent colour per note (stable, from its id),
 * a greeting for the time of day, and reading time.
 */

/**
 * Flat note colours from the study desk (ADR-0114, unslop): pen ink, teal, moss, clay, umber, graphite. Each carries white
 * text at 4.5:1 or more. `to` equals `from`: notes get one solid colour, never a gradient.
 */
export const ACCENTS = [
  { name: 'ink', from: '#1e40af', to: '#1e40af', tint: 'rgb(40 71 168 / 0.08)' },
  { name: 'teal', from: '#0c5c66', to: '#0c5c66', tint: 'rgb(12 92 102 / 0.08)' },
  { name: 'moss', from: '#3d6b2c', to: '#3d6b2c', tint: 'rgb(61 107 44 / 0.08)' },
  { name: 'clay', from: '#9a4a2b', to: '#9a4a2b', tint: 'rgb(154 74 43 / 0.08)' },
  { name: 'umber', from: '#7a5a12', to: '#7a5a12', tint: 'rgb(122 90 18 / 0.08)' },
  { name: 'graphite', from: '#4a4740', to: '#4a4740', tint: 'rgb(74 71 64 / 0.08)' },
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
