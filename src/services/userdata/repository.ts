/* ============================================================
   USER DATA REPOSITORY — the only way the app reads or writes a
   learner's server-side data. Today it's backed by Firestore
   (firestoreRepository.ts); moving to another backend (a REST
   API + Postgres, say) means implementing this interface, with
   no changes to the features that use it.

   The implementation is loaded on demand, so the Firestore SDK
   is only downloaded once someone signs in.
   ============================================================ */

import type { DayDoc, EventBatchDoc, NoteDoc, Prefs, ProgressData, TrendingDoc } from '@schema/firestore'

export interface RemoteSnapshot {
  progress: Partial<ProgressData> | undefined
  prefs: Prefs | undefined
  /** day → log */
  days: Record<string, Omit<DayDoc, 'updatedAt'>>
  /** note key → note */
  notes: Map<string, NoteDoc>
}

export interface UserWrites {
  progress?: ProgressData
  prefs?: Prefs
  days: [day: string, log: Omit<DayDoc, 'updatedAt'>][]
  /** `undefined` or empty text deletes the note */
  notes: [key: string, note: Omit<NoteDoc, 'key'> | undefined][]
}

export interface UserDataRepository {
  fetchAll(uid: string): Promise<RemoteSnapshot>
  commit(uid: string, writes: UserWrites): Promise<void>
  appendEvents(uid: string, batch: EventBatchDoc): Promise<void>
  deleteAll(uid: string): Promise<void>
  trending(): Promise<TrendingDoc | null>
}

let repo: Promise<UserDataRepository> | null = null

export function userData(): Promise<UserDataRepository> {
  repo ??= import('./firestoreRepository').then((m) => m.firestoreRepository)
  return repo
}
