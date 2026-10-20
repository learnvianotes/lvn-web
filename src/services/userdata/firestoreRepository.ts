/* ============================================================
   Firestore implementation of UserDataRepository.
   Document shapes: schema/firestore.ts · access: firestore.rules
   ============================================================ */

import { collection, deleteDoc, doc, getDoc, getDocs, setDoc, writeBatch, type WriteBatch } from 'firebase/firestore/lite'
import { db } from '@/services/firebase/firestore'
import { SCHEMA_VERSION, docId, type EventBatchDoc, type NoteDoc, type TrendingDoc, type UserDoc } from '@schema/firestore'
import type { RemoteSnapshot, UserDataRepository, UserWrites } from './repository'

const userRef = (uid: string) => doc(db(), 'users', uid)
/** Firestore batches hold at most 500 writes. */
const BATCH_LIMIT = 450

export const firestoreRepository: UserDataRepository = {
  async adultConfirmedAt(uid) {
    const at = (await getDoc(userRef(uid))).get('adultConfirmedAt')
    return typeof at === 'number' ? at : null
  },

  async confirmAdult(uid, termsVersion) {
    const now = Date.now()
    await setDoc(userRef(uid), { adultConfirmedAt: now, termsVersion, updatedAt: now }, { merge: true })
  },

  async serverOnly(uid) {
    const ref = userRef(uid)
    const [user, events] = await Promise.all([getDoc(ref), getDocs(collection(ref, 'events'))])
    const at = user.get('adultConfirmedAt')
    const version = user.get('termsVersion')
    return {
      adultConfirmedAt: typeof at === 'number' ? at : null,
      termsVersion: typeof version === 'string' ? version : null,
      events: events.docs.map((d) => d.data() as EventBatchDoc).sort((a, b) => a.createdAt - b.createdAt),
    }
  },

  async fetchAll(uid) {
    const ref = userRef(uid)
    const [user, days, notes] = await Promise.all([
      getDoc(ref),
      getDocs(collection(ref, 'days')),
      getDocs(collection(ref, 'notes')),
    ])
    const data = user.data() as Partial<UserDoc> | undefined
    const out: RemoteSnapshot = { progress: data?.progress, prefs: data?.prefs, days: {}, notes: new Map() }
    days.forEach((d) => { out.days[d.id] = { topics: d.data().topics ?? {}, focus: d.data().focus ?? 0 } })
    notes.forEach((d) => {
      const n = d.data() as NoteDoc
      out.notes.set(n.key, n)
    })
    return out
  },

  async commit(uid, w: UserWrites) {
    const ref = userRef(uid)
    const now = Date.now()
    const ops: ((b: WriteBatch) => void)[] = []

    if (w.progress || w.prefs) {
      const fields: Partial<UserDoc> = { schema: SCHEMA_VERSION, updatedAt: now }
      if (w.progress) fields.progress = w.progress
      if (w.prefs) fields.prefs = w.prefs
      // mergeFields replaces those fields wholesale (so removed map keys disappear) and keeps the rest.
      ops.push((b) => b.set(ref, fields, { mergeFields: Object.keys(fields) }))
    }
    for (const [day, log] of w.days) {
      ops.push((b) => b.set(doc(ref, 'days', day), { topics: log.topics, focus: log.focus, updatedAt: now }))
    }
    for (const [key, n] of w.notes) {
      const nref = doc(ref, 'notes', docId(key))
      ops.push((b) => (n?.text ? b.set(nref, { key, text: n.text, updatedAt: n.updatedAt }) : b.delete(nref)))
    }

    for (let i = 0; i < ops.length; i += BATCH_LIMIT) {
      const batch = writeBatch(db())
      ops.slice(i, i + BATCH_LIMIT).forEach((op) => op(batch))
      await batch.commit()
    }
  },

  async appendEvents(uid, batch) {
    await setDoc(doc(collection(userRef(uid), 'events')), batch)
  },

  async deleteAll(uid) {
    const ref = userRef(uid)
    const subs = await Promise.all(['days', 'notes', 'events'].map((c) => getDocs(collection(ref, c))))
    const refs = subs.flatMap((s) => s.docs.map((d) => d.ref))
    for (let i = 0; i < refs.length; i += BATCH_LIMIT) {
      const batch = writeBatch(db())
      refs.slice(i, i + BATCH_LIMIT).forEach((r) => batch.delete(r))
      await batch.commit()
    }
    await deleteDoc(ref)
  },

  async trending() {
    const snap = await getDoc(doc(db(), 'trending', 'current'))
    return snap.exists() ? (snap.data() as TrendingDoc) : null
  },
}
