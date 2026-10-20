/* ============================================================
   AGE — accounts are for adults (18+).

   • The date of birth is asked neutrally (day, month, year; no
     defaults, no hint of the cut-off) and used once: only the
     fact that the person confirmed they are an adult, and when,
     is stored with the account (users/{uid}.adultConfirmedAt).
   • A refusal is remembered on the device for a day, so going
     back and answering again doesn't open sign-up.
   ============================================================ */

import { get, remove, set } from '@/services/storage'

export const ADULT_AGE = 18
const REFUSED_KEY = 'age-refused'
const REFUSED_FOR_MS = 24 * 60 * 60 * 1000

export interface BirthDate {
  year: number
  /** 1–12 */
  month: number
  day: number
}

/** A real calendar date, not in the future and not absurdly old. */
export function isValidBirthDate(d: Partial<BirthDate>, today = new Date()): d is BirthDate {
  const { year, month, day } = d
  if (!Number.isInteger(year) || !Number.isInteger(month) || !Number.isInteger(day)) return false
  if (month! < 1 || month! > 12 || day! < 1 || day! > 31) return false
  const date = new Date(year!, month! - 1, day!)
  if (date.getFullYear() !== year || date.getMonth() !== month! - 1 || date.getDate() !== day) return false // 31 April, 29 Feb 2023…
  return year! > today.getFullYear() - 120 && date <= today
}

/** Whole years between the birth date and `today` (local calendar dates). */
export function ageOn(d: BirthDate, today = new Date()): number {
  let age = today.getFullYear() - d.year
  const m = today.getMonth() + 1
  if (m < d.month || (m === d.month && today.getDate() < d.day)) age--
  return age
}

export function isAdult(d: BirthDate, today = new Date()): boolean {
  return ageOn(d, today) >= ADULT_AGE
}

/* ── refusal, remembered on this device ─────────────────── */

interface Refusal { at: number; uid?: string }

export function markRefused(uid?: string) {
  set<Refusal>(REFUSED_KEY, { at: Date.now(), ...(uid ? { uid } : {}) })
}

/** The refusal still in force on this device, if any. */
export function activeRefusal(now = Date.now()): Refusal | null {
  const r = get<Refusal>(REFUSED_KEY)
  if (!r || typeof r.at !== 'number') return null
  if (now - r.at > REFUSED_FOR_MS) {
    remove(REFUSED_KEY)
    return null
  }
  return r
}
