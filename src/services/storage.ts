/* ============================================================
   STORAGE — the single point of access to localStorage
   Keys keep the historical `cnote:` prefix so progress saved by
   earlier versions of the app is still found.
   ============================================================ */

const PREFIX = 'cnote:'

/** The localStorage key behind `key` (to match `storage` events from other tabs). */
export const storageKey = (key: string) => `${PREFIX}${key}`

/**
 * Retrieve a stored value by key.
 * Returns null if not found or if parsing fails.
 */
export function get<T>(key: string): T | null {
  try {
    const raw = localStorage.getItem(`${PREFIX}${key}`)
    if (raw === null) return null
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}

/**
 * Store a value under a key.
 * Values are JSON-serialized for type safety.
 */
export function set<T>(key: string, value: T): void {
  try {
    localStorage.setItem(`${PREFIX}${key}`, JSON.stringify(value))
  } catch {
    // Quota exceeded or private browsing — fail silently
  }
}

/**
 * Remove a stored value by key.
 */
export function remove(key: string): void {
  try {
    localStorage.removeItem(`${PREFIX}${key}`)
  } catch {
    // Fail silently
  }
}
