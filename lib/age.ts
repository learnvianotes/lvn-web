/**
 * Accounts are for adults (lvn-backend ADR-0091). The API decides — the forms never name the cut-off — and this module
 * keeps what the browser needs:
 * - a refusal is remembered on this device for a day, so going back and answering again doesn't reopen sign-up. It
 *   closes the sign-up forms here and turns Google Analytics off on the device (no tracking of children, ADR-0092), and
 *   nothing else: it never deletes or signs out anyone;
 * - the age typed in whole years (lvn-backend ADR-0104), checked before the "Is this right?" step every answer goes
 *   through. The API checks it again.
 */

import { setAnalyticsConsent } from './consent'

const KEY = 'lvn.age-refused'
export const REFUSED_FOR_MS = 24 * 60 * 60 * 1000

type Store = Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>
const browserStore = (): Store | null => {
  try {
    return typeof window === 'undefined' ? null : window.localStorage
  } catch {
    return null
  }
}

const listeners = new Set<() => void>()
const emit = () => listeners.forEach((l) => l())

/** Remembers a refusal on this device. */
export function markAgeRefused(now = Date.now(), store: Store | null = browserStore()): void {
  try {
    store?.setItem(KEY, JSON.stringify({ at: now }))
  } catch {
    // Private mode or a full disk: the API still refuses each attempt.
  }
  setAnalyticsConsent('denied', store)
  emit()
}

/** When this device was refused, while that is under a day ago; otherwise null (and an old record is cleared). */
export function ageRefusedAt(now = Date.now(), store: Store | null = browserStore()): number | null {
  try {
    const at = (JSON.parse(store?.getItem(KEY) ?? 'null') as { at?: unknown } | null)?.at
    if (typeof at !== 'number') return null
    if (now - at < REFUSED_FOR_MS && at <= now) return at
    store?.removeItem(KEY)
    return null
  } catch {
    return null
  }
}

/** For useSyncExternalStore: this tab's changes and other tabs' (the storage event). */
export function subscribeAgeRefusal(listener: () => void): () => void {
  listeners.add(listener)
  const onStorage = (e: StorageEvent) => (e.key === null || e.key === KEY) && listener()
  window.addEventListener('storage', onStorage)
  return () => {
    listeners.delete(listener)
    window.removeEventListener('storage', onStorage)
  }
}

/** The ages the API accepts, in whole years (lvn-backend ADR-0104). The minimum age for an account is the API's alone. */
export const AGE_MIN = 1
export const AGE_MAX = 120

/** Why an age field's text is not an age: empty, not a whole number, or outside AGE_MIN–AGE_MAX. */
export type AgeProblem = 'required' | 'whole' | 'range'

/**
 * The age field's text as whole years, or why it is not one. Digits only, so "17.5", "1e2" or "18 years" are 'whole';
 * a whole number below AGE_MIN or above AGE_MAX ("0", "-3", "121") is 'range'.
 */
export function parseAge(text: string): { age: number } | { problem: AgeProblem } {
  const value = text.trim()
  if (!value) return { problem: 'required' }
  if (!/^-?\d+$/.test(value)) return { problem: 'whole' }
  const age = Number(value)
  if (age < AGE_MIN || age > AGE_MAX) return { problem: 'range' }
  return { age }
}

/**
 * An age input's props: a text box with the phone's number pad, since type="number" rounds, steps on a scroll and
 * takes "1e2". No `pattern`: the browser's own check would block the form before parseAge can say what is wrong.
 * There is no autofill token for an age.
 */
export const AGE_INPUT = { type: 'text', inputMode: 'numeric', autoComplete: 'off', spellCheck: false } as const
