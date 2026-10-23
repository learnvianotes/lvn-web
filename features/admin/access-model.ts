/** Emails pasted into the beta allowlist: one address, or many split on commas, spaces and new lines. */

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

export function parseAllowlistEmails(raw: string): { ok: string[]; invalid: string[] } {
  const ok: string[] = []
  const invalid: string[] = []
  const seen = new Set<string>()
  for (const part of raw.split(/[\s,;]+/)) {
    const trimmed = part.trim()
    if (!trimmed) continue
    const email = trimmed.toLowerCase()
    if (!EMAIL.test(email) || email.length > 320) {
      invalid.push(trimmed)
      continue
    }
    if (seen.has(email)) continue
    seen.add(email)
    ok.push(email)
  }
  return { ok, invalid }
}

export function formatAddedOn(iso: string): string {
  const date = new Date(iso)
  if (Number.isNaN(date.getTime())) return iso
  return new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium' }).format(date)
}
