/** How a verification file is shown, and how an AI ID-card reading lines up with the profile. */

export function proofKind(mime: string, name: string): 'image' | 'pdf' | 'file' {
  const type = mime.toLowerCase()
  if (type.startsWith('image/')) return 'image'
  if (type === 'application/pdf' || name.toLowerCase().endsWith('.pdf')) return 'pdf'
  return 'file'
}

/** Confidence may arrive as 0–1 or as a percent. */
export function confidencePercent(value: number | null | undefined): number | null {
  if (value == null || !Number.isFinite(value)) return null
  const pct = value <= 1 ? value * 100 : value
  return Math.round(Math.min(100, Math.max(0, pct)))
}

export type FieldMatch = 'same' | 'different' | 'unknown'

export function fieldsAgree(extracted: string | null | undefined, profile: string | null | undefined): FieldMatch {
  const norm = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim()
  const left = extracted ? norm(extracted) : ''
  const right = profile ? norm(profile) : ''
  if (!left || !right) return 'unknown'
  if (left === right || left.includes(right) || right.includes(left)) return 'same'
  return 'different'
}

export function verdictTone(verdict: string): 'good' | 'bad' | 'pending' {
  const value = verdict.toUpperCase()
  if (/(DECLINE|REJECT|MISMATCH|FAIL)/.test(value)) return 'bad'
  if (/(APPROVE|MATCH|PASS|ACCEPT)/.test(value)) return 'good'
  return 'pending'
}
