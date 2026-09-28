/* ============================================================
   NOTES — the learner's own quick notes, one per topic.
   Local first; synced to the account by progress/sync.ts.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import type { NoteDoc } from '@schema/firestore'
import { get, set } from '@/services/storage'

export type Note = Omit<NoteDoc, 'key'>

export type Notes = Record<string, Note>

export const NOTE_MAX = 5000
const KEY = 'notes'

let state: Notes = get<Notes>(KEY) ?? {}
const listeners = new Set<() => void>()
const localListeners = new Set<(key: string) => void>()

window.addEventListener('storage', (e) => {
  if (e.key?.endsWith(`:${KEY}`)) {
    state = get<Notes>(KEY) ?? {}
    listeners.forEach((l) => l())
  }
})

export function useNote(key: string): Note | undefined {
  return useSyncExternalStore(
    (l) => { listeners.add(l); return () => { listeners.delete(l) } },
    () => state[key],
  )
}

export function saveNote(key: string, text: string) {
  const trimmed = text.slice(0, NOTE_MAX)
  const next = { ...state }
  if (trimmed.trim()) next[key] = { text: trimmed, updatedAt: Date.now() }
  else next[key] = { text: '', updatedAt: Date.now() } // keep a tombstone so the deletion syncs
  state = next
  set(KEY, state)
  listeners.forEach((l) => l())
  localListeners.forEach((l) => l(key))
}

export const getNotes = () => state
export function replaceNotes(next: Notes) {
  state = next
  set(KEY, state)
  listeners.forEach((l) => l())
}
export function onLocalNoteChange(listener: (key: string) => void) {
  localListeners.add(listener)
  return () => { localListeners.delete(listener) }
}
