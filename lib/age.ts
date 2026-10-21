/**
 * Accounts are for adults (lvn-backend ADR-0091). The API decides — the forms never name the cut-off — and this module
 * keeps what the browser needs:
 * - a refusal is remembered on this device for a day, so going back and answering again doesn't reopen sign-up. It
 *   closes the sign-up forms here and nothing else: it never deletes or signs out anyone;
 * - the date of birth in words, for the "Is this right?" step every answer goes through.
 */

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

/** "14 March 2001" — so a mis-picked day, month or year is easy to see. Empty for anything that isn't a real date. */
export function birthDateInWords(iso: string): string {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return ''
  const d = new Date(`${iso}T00:00:00Z`)
  if (Number.isNaN(d.getTime()) || d.toISOString().slice(0, 10) !== iso) return ''
  return new Intl.DateTimeFormat('en-IN', { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }).format(d)
}
