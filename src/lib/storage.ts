/* ============================================================
   C-NOTE STORAGE ABSTRACTION
   Single point of access to client-side persistence.

   Currently backed by localStorage. The interface is designed
   so the implementation can be swapped (IndexedDB, Firebase)
   without touching any consumer code.
   ============================================================ */

const PREFIX = 'cnote:'

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

/**
 * Clear all C-NOTE keys from storage.
 * Does not clear unrelated third-party keys.
 */
export function clearAll(): void {
  try {
    Object.keys(localStorage)
      .filter((k) => k.startsWith(PREFIX))
      .forEach((k) => localStorage.removeItem(k))
  } catch {
    // Fail silently
  }
}

/* ── Storage keys registry ────────────────────────────────── */
/**
 * Centralized key names to avoid typos across the app.
 * Extend this object when new features need persistence.
 */
export const STORAGE_KEYS = {
  THEME: 'theme',
  LAST_VISITED_SUBJECT: 'last-visited-subject',
  LAST_VISITED_QUESTION: 'last-visited-question',
  PROGRESS_PREFIX: 'progress:',
} as const
