/* ============================================================
   FIRESTORE CONTENT SOURCE
   Document layout is defined by scripts/content/seed-firestore.mjs.
   ============================================================ */

import { collection, doc, getDoc, getDocs, query, where } from 'firebase/firestore/lite'
import { db, firebaseConfigured } from '@/lib/firebase'
import { NotFoundError, type ContentSource } from './source'
import type { Catalog, Problem, TopicDoc } from './types'

function ensureConfigured() {
  if (!firebaseConfigured) throw new Error('Firebase is not configured — set the VITE_FIREBASE_* variables in .env.local.')
}

export const firestoreSource: ContentSource = {
  async catalog() {
    ensureConfigured()
    const snap = await getDoc(doc(db, 'catalog', 'current'))
    if (!snap.exists()) throw new NotFoundError('catalog/current — has the database been seeded?')
    return snap.data() as Catalog
  },

  async topic(subjectId, topicId) {
    ensureConfigured()
    const ref = doc(db, 'subjects', subjectId, 'topics', topicId)
    const snap = await getDoc(ref)
    if (!snap.exists()) throw new NotFoundError(ref.path)
    const data = snap.data() as TopicDoc & { chunks?: number }
    // Large topics are split across a `chunks` subcollection (1 MiB doc limit).
    if ((data.chunks ?? 1) > 1) {
      const rest = await Promise.all(
        Array.from({ length: data.chunks! - 1 }, (_, i) => getDoc(doc(ref, 'chunks', String(i + 1)))),
      )
      data.html += rest.map((s) => (s.data()?.html as string) ?? '').join('')
    }
    return data
  },

  async problems(subjectId, categoryId) {
    ensureConfigured()
    const q = query(collection(db, 'subjects', subjectId, 'problems'), where('category', '==', categoryId))
    const snap = await getDocs(q)
    if (snap.empty) throw new NotFoundError(`${subjectId}/problems?category=${categoryId}`)
    return snap.docs.map((d) => d.data() as Problem).sort((a, b) => a.order - b.order)
  },
}
