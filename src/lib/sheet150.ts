/* ============================================================
   SHEET 150 — DATA ACCESS LAYER
   All Firestore reads for Sheet 150 go through this module.
   Presentation components must NOT import from firebase/firestore
   directly — import from here instead.

   Firestore path:
     subjects/sheet-150/questions/{id}   → Sheet150Problem
     subjects/sheet-150                  → { categories: Sheet150Category[] }
   ============================================================ */

import {
  doc,
  getDoc,
  collection,
  getDocs,
  query,
  where,
  writeBatch,
  serverTimestamp,
  type DocumentData,
} from 'firebase/firestore'
import { db } from './firebase'
import type { Sheet150Problem, Sheet150Category } from '@/types/sheet150'
import { SHEET_150_CORE_PROBLEMS } from '@/data/sheet150Problems'

/* ── Collection references ──────────────────────────────────── */

const SUBJECT_DOC_PATH = 'subjects/sheet-150'
const QUESTIONS_COL = 'subjects/sheet-150/questions'

/* ── Slug to ID mapping ─────────────────────────────────────── */

export const SLUG_TO_ID: Record<string, string> = {
  'contains-duplicate': 'lc-217',
  'valid-anagram': 'lc-242',
  'two-sum': 'lc-1',
  'group-anagrams': 'lc-49',
  'binary-search': 'lc-704',
}

/* ── Default categories list ────────────────────────────────── */

export const DEFAULT_CATEGORIES: Sheet150Category[] = [
  { id: 'arrays-hashing', label: 'Arrays & Hashing', order: 1, problemCount: 4 },
  { id: 'binary-search', label: 'Binary Search', order: 2, problemCount: 1 },
]

/* ── Type guard / normalizer ────────────────────────────────── */

function normalizeProblem(data: DocumentData): Sheet150Problem {
  const p = data as Sheet150Problem
  if (!p.slug && p.id) {
    const slugEntry = Object.entries(SLUG_TO_ID).find(([, id]) => id === p.id)
    if (slugEntry) p.slug = slugEntry[0]
  }
  return p
}

/* ── Public API ─────────────────────────────────────────────── */

/**
 * Fetch a single problem by its URL slug (e.g. "two-sum").
 *
 * 1. Checks Firestore using where('slug', '==', slug)
 * 2. If not found or empty, checks direct ID lookup using SLUG_TO_ID
 * 3. Falls back to local core problems catalog if offline or missing
 */
export async function getProblemBySlug(slug: string): Promise<Sheet150Problem | null> {
  try {
    const q = query(
      collection(db, QUESTIONS_COL),
      where('slug', '==', slug)
    )
    const snap = await getDocs(q)
    if (!snap.empty) {
      return normalizeProblem(snap.docs[0].data())
    }

    // Try direct ID lookup if slug query had no results
    const id = SLUG_TO_ID[slug]
    if (id) {
      const byId = await getProblemById(id)
      if (byId) return normalizeProblem({ ...byId, slug })
    }
  } catch (err) {
    console.warn('[Sheet 150] Firestore read failed, checking local catalog:', err)
  }

  // Graceful local fallback (ensures offline and preview work reliably)
  const localMatch = SHEET_150_CORE_PROBLEMS.find(
    (p) => p.slug === slug || (p.id && SLUG_TO_ID[slug] === p.id)
  )
  if (localMatch) {
    return normalizeProblem({
      ...localMatch,
      slug: localMatch.slug || slug,
      category: localMatch.category || 'arrays-hashing',
    })
  }

  return null
}

/**
 * Fetch a single problem by its Firestore document ID (e.g. "lc-1").
 */
export async function getProblemById(id: string): Promise<Sheet150Problem | null> {
  try {
    const ref = doc(db, QUESTIONS_COL, id)
    const snap = await getDoc(ref)
    if (snap.exists()) {
      return normalizeProblem(snap.data())
    }
  } catch (err) {
    console.warn('[Sheet 150] getProblemById error:', err)
  }

  const localMatch = SHEET_150_CORE_PROBLEMS.find((p) => p.id === id)
  return localMatch ? normalizeProblem(localMatch) : null
}

/**
 * Fetch all problems in a specific category, ordered by `order` field.
 * Sorted client-side to avoid requiring composite Firestore indexes.
 */
export async function getProblemsByCategory(categoryId: string): Promise<Sheet150Problem[]> {
  try {
    const q = query(
      collection(db, QUESTIONS_COL),
      where('category', '==', categoryId)
    )
    const snap = await getDocs(q)
    if (!snap.empty) {
      const list = snap.docs.map((d) => normalizeProblem(d.data()))
      return list.sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
    }
  } catch (err) {
    console.warn('[Sheet 150] getProblemsByCategory error:', err)
  }

  // Fallback to local catalog
  const localList = SHEET_150_CORE_PROBLEMS.filter(
    (p) => p.category === categoryId
  ).map((p) => normalizeProblem(p))
  return localList.sort((a, b) => (a.order ?? 0) - (b.order ?? 0))
}

/**
 * Fetch ALL Sheet 150 problems.
 */
export async function getAllProblems(): Promise<Sheet150Problem[]> {
  try {
    const snap = await getDocs(collection(db, QUESTIONS_COL))
    if (!snap.empty) {
      return snap.docs.map((d) => normalizeProblem(d.data()))
    }
  } catch (err) {
    console.warn('[Sheet 150] getAllProblems error:', err)
  }
  return SHEET_150_CORE_PROBLEMS.map((p) => normalizeProblem(p))
}

/**
 * Fetch the categories list from the subjects/sheet-150 document.
 */
export async function getCategories(): Promise<Sheet150Category[]> {
  try {
    const ref = doc(db, SUBJECT_DOC_PATH)
    const snap = await getDoc(ref)
    if (snap.exists()) {
      const data = snap.data()
      const cats: Sheet150Category[] = data?.categories ?? []
      if (cats.length > 0) {
        return [...cats].sort((a, b) => a.order - b.order)
      }
    }
  } catch (err) {
    console.warn('[Sheet 150] getCategories error:', err)
  }
  return DEFAULT_CATEGORIES
}

/**
 * Seed or update Sheet 150 metadata and problems to Firestore.
 */
export async function seedSheet150Problems(): Promise<void> {
  try {
    const batch = writeBatch(db)

    // Seed subject metadata document with categories
    const metaRef = doc(db, SUBJECT_DOC_PATH)
    batch.set(
      metaRef,
      {
        id: 'sheet-150',
        title: 'Sheet 150',
        description: '150 curated DSA coding problems for technical interviews.',
        totalProblems: SHEET_150_CORE_PROBLEMS.length,
        categories: DEFAULT_CATEGORIES,
        updatedAt: serverTimestamp(),
      },
      { merge: true }
    )

    // Seed questions
    SHEET_150_CORE_PROBLEMS.forEach((p) => {
      const qRef = doc(db, QUESTIONS_COL, p.id)
      batch.set(
        qRef,
        {
          ...p,
          updatedAt: serverTimestamp(),
        },
        { merge: true }
      )
    })

    await batch.commit()
    console.log(`[Sheet 150] Successfully seeded ${SHEET_150_CORE_PROBLEMS.length} problems to Firestore!`)
  } catch (err) {
    console.warn('[Sheet 150] Failed to seed problems to Firestore:', err)
  }
}
