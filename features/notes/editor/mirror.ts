'use client'

import type { JSONContent } from '@tiptap/core'
import type { SavedState } from '../model/save'

/**
 * The local mirror of drafts (lvn-backend §4.3, §12.2): every edit is written to IndexedDB at once and removed when the
 * server has acknowledged it, so a closed tab, a crash or a lost connection never loses a draft. Entries are per user
 * and are all deleted on sign-out (clearDraftMirrors).
 */

export interface MirrorEntry {
  title: string
  doc: JSONContent
  saved: { title: string; cards: [string, SavedState['cards'] extends Map<string, infer V> ? V : never][] }
  at: number
}

const DB = 'lvn-notes'
const STORE = 'drafts'

function open(): Promise<IDBDatabase | null> {
  if (typeof indexedDB === 'undefined') return Promise.resolve(null)
  return new Promise((resolve) => {
    const req = indexedDB.open(DB, 1)
    req.onupgradeneeded = () => req.result.createObjectStore(STORE)
    req.onsuccess = () => resolve(req.result)
    // Private browsing or blocked storage: autosave still works, only the offline copy is missing.
    req.onerror = () => resolve(null)
  })
}

async function run<T>(mode: IDBTransactionMode, fn: (store: IDBObjectStore) => IDBRequest<T>): Promise<T | null> {
  const db = await open()
  if (!db) return null
  return new Promise((resolve) => {
    const tx = db.transaction(STORE, mode)
    const req = fn(tx.objectStore(STORE))
    tx.oncomplete = () => {
      db.close()
      resolve(req.result ?? null)
    }
    tx.onerror = () => {
      db.close()
      resolve(null)
    }
  })
}

const key = (userId: string, noteId: string) => `${userId}:${noteId}`

export const toMirror = (title: string, doc: JSONContent, saved: SavedState): MirrorEntry => ({ title, doc, saved: { title: saved.title, cards: [...saved.cards.entries()] }, at: Date.now() })
export const savedFromMirror = (m: MirrorEntry): SavedState => ({ title: m.saved.title, cards: new Map(m.saved.cards) })

export const writeMirror = (userId: string, noteId: string, entry: MirrorEntry) => run('readwrite', (s) => s.put(entry, key(userId, noteId)))
export const readMirror = (userId: string, noteId: string) => run<MirrorEntry | undefined>('readonly', (s) => s.get(key(userId, noteId))).then((e) => e ?? null)
export const removeMirror = (userId: string, noteId: string) => run('readwrite', (s) => s.delete(key(userId, noteId)))

/** How many drafts this browser still holds that the server has not acknowledged. */
export const countDraftMirrors = () => run<number>('readonly', (s) => s.count()).then((n) => n ?? 0)

/** Removes every mirrored draft of this browser (sign-out: notes stay private on shared computers). */
export async function clearDraftMirrors(): Promise<void> {
  if (typeof indexedDB === 'undefined') return
  await new Promise<void>((resolve) => {
    const req = indexedDB.deleteDatabase(DB)
    req.onsuccess = req.onerror = req.onblocked = () => resolve()
  })
}
