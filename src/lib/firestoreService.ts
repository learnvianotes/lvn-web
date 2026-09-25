/* ============================================================
   FIRESTORE SERVICE — C-NOTE
   All Firestore reads/writes go through this module.

   Collections:
     /userProgress/{userId}/subjects/{subjectId}  → SubjectProgress
     /userProgress/{userId}/topics/{topicId}       → TopicProgress
     /userProgress/{userId}/questions/{questionId} → QuestionProgress
     /userProgress/{userId}/settings/preferences   → UserPreferences

   Anonymous auth is used so no login is required from the user.
   ============================================================ */

import {
  doc,
  getDoc,
  setDoc,
  collection,
  getDocs,
  query,
  where,
  writeBatch,
  onSnapshot,
  serverTimestamp,
  type DocumentReference,
  type Unsubscribe,
} from 'firebase/firestore'
import { signInAnonymously, onAuthStateChanged, type User } from 'firebase/auth'
import { db, auth } from './firebase'

/* ── Auth helpers ────────────────────────────────────────── */

/** Current authenticated user (or null before auth resolves) */
let currentUser: User | null = null

/** Promise that resolves once anonymous auth is established */
export const authReady: Promise<User> = new Promise((resolve) => {
  onAuthStateChanged(auth, async (user) => {
    if (user) {
      currentUser = user
      resolve(user)
    } else {
      try {
        const cred = await signInAnonymously(auth)
        currentUser = cred.user
        resolve(cred.user)
      } catch (e) {
        console.warn('[C-Note] Firebase anonymous auth failed:', e)
      }
    }
  })
})

export function getCurrentUser(): User | null {
  return currentUser
}

/* ── Document helpers ────────────────────────────────────── */

function subjectProgressRef(userId: string, subjectId: string): DocumentReference {
  return doc(db, 'userProgress', userId, 'subjects', subjectId)
}

function questionProgressRef(userId: string, questionId: string): DocumentReference {
  return doc(db, 'userProgress', userId, 'questions', questionId)
}

function preferencesRef(userId: string): DocumentReference {
  return doc(db, 'userProgress', userId, 'settings', 'preferences')
}

/* ── Subject Progress ────────────────────────────────────── */

export interface SubjectProgress {
  subjectId: string
  lastTopicId?: string
  lastTopicTitle?: string
  completedTopics?: string[]
  updatedAt?: ReturnType<typeof serverTimestamp>
}

export async function saveSubjectProgress(
  subjectId: string,
  data: Omit<SubjectProgress, 'subjectId' | 'updatedAt'>
): Promise<void> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return

  const ref = subjectProgressRef(uid, subjectId)
  await setDoc(
    ref,
    { subjectId, ...data, updatedAt: serverTimestamp() },
    { merge: true }
  )
}

export async function getSubjectProgress(subjectId: string): Promise<SubjectProgress | null> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return null

  const snap = await getDoc(subjectProgressRef(uid, subjectId))
  return snap.exists() ? (snap.data() as SubjectProgress) : null
}

/* ── Question Progress ───────────────────────────────────── */

export type QuestionStatus = 'unsolved' | 'solved' | 'revisit'

export interface QuestionProgressDoc {
  questionId: string
  subjectId: string
  topicId: string
  status: QuestionStatus
  notes?: string
  updatedAt?: ReturnType<typeof serverTimestamp>
}

export async function saveQuestionProgress(
  data: Omit<QuestionProgressDoc, 'updatedAt'>
): Promise<void> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return

  const ref = questionProgressRef(uid, data.questionId)
  await setDoc(ref, { ...data, updatedAt: serverTimestamp() }, { merge: true })
}

export async function getQuestionProgress(
  questionId: string
): Promise<QuestionProgressDoc | null> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return null

  const snap = await getDoc(questionProgressRef(uid, questionId))
  return snap.exists() ? (snap.data() as QuestionProgressDoc) : null
}

/** Get all questions progress for current user (optionally filtered by subjectId) */
export async function getAllQuestionsProgress(
  subjectId?: string
): Promise<Record<string, QuestionProgressDoc>> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return {}

  try {
    const qCol = collection(db, 'userProgress', uid, 'questions')
    const qRef = subjectId ? query(qCol, where('subjectId', '==', subjectId)) : qCol
    const snap = await getDocs(qRef)
    const result: Record<string, QuestionProgressDoc> = {}
    snap.forEach((docSnap) => {
      const data = docSnap.data() as QuestionProgressDoc
      result[data.questionId] = data
    })
    return result
  } catch (err) {
    console.warn('[C-Note] Error fetching all questions progress from Firestore:', err)
    return {}
  }
}

/* ── Sheet 150 Problems Catalog (Stored in Firestore) ────── */

export interface Sheet150QuestionDoc {
  id: string                    // e.g. "lc-217"
  slug?: string                 // e.g. "contains-duplicate"
  lcNumber: number              // e.g. 217
  title: string                 // e.g. "Contains Duplicate"
  difficulty: 'Easy' | 'Medium' | 'Hard'
  topic: string                 // e.g. "Arrays & Hashing"
  category?: string             // e.g. "arrays-hashing"
  order?: number                // e.g. 1
  tags?: string[]
  moduleNumber: number          // e.g. 1
  problemStatement: string
  inputOutput?: {
    input?: string
    output?: string
    examples?: { in: string; out: string; comment?: string }[]
  }
  constraints?: string[]
  keyInsight?: string
  naiveSolution?: {
    title: string
    explanation?: string
    approach?: string[]
    complexityTime: string
    complexitySpace: string
    code: { py?: string; cpp?: string; java?: string; js?: string }
  }
  optimalSolution?: {
    title: string
    explanation?: string
    approach?: string[]
    complexityTime: string
    complexitySpace: string
    code: { py?: string; cpp?: string; java?: string; js?: string }
  }
  leetcodeUrl?: string
  similarQuestions?: { slug?: string; title: string; lc: number; difficulty: string }[]
  updatedAt?: ReturnType<typeof serverTimestamp>
}

export async function saveSheet150Problem(problem: Sheet150QuestionDoc): Promise<void> {
  const pRef = doc(db, 'subjects', 'sheet-150', 'questions', problem.id)
  await setDoc(pRef, { ...problem, updatedAt: serverTimestamp() }, { merge: true })
}

export async function getSheet150Problem(questionId: string): Promise<Sheet150QuestionDoc | null> {
  const pRef = doc(db, 'subjects', 'sheet-150', 'questions', questionId)
  const snap = await getDoc(pRef)
  return snap.exists() ? (snap.data() as Sheet150QuestionDoc) : null
}

export async function getAllSheet150Problems(): Promise<Sheet150QuestionDoc[]> {
  try {
    const pCol = collection(db, 'subjects', 'sheet-150', 'questions')
    const snap = await getDocs(pCol)
    const list: Sheet150QuestionDoc[] = []
    snap.forEach((docSnap) => list.push(docSnap.data() as Sheet150QuestionDoc))
    return list
  } catch (err) {
    console.warn('[C-Note] Error fetching Sheet 150 problems from Firestore:', err)
    return []
  }
}

export async function batchSeedSheet150Problems(problems: Sheet150QuestionDoc[]): Promise<void> {
  try {
    const batch = writeBatch(db)
    problems.forEach((p) => {
      const ref = doc(db, 'subjects', 'sheet-150', 'questions', p.id)
      batch.set(ref, { ...p, updatedAt: serverTimestamp() }, { merge: true })
    })
    await batch.commit()
    console.log(`[C-Note] Successfully seeded ${problems.length} Sheet 150 problems to Firestore!`)
  } catch (err) {
    console.warn('[C-Note] Failed to batch seed Sheet 150 problems to Firestore:', err)
  }
}

/* ── User Preferences ────────────────────────────────────── */

export interface UserPreferences {
  theme?: 'dark' | 'light'
  gridOrder?: string[]
  selectedCategory?: string
  updatedAt?: ReturnType<typeof serverTimestamp>
}

export async function savePreferences(data: Omit<UserPreferences, 'updatedAt'>): Promise<void> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return

  await setDoc(preferencesRef(uid), { ...data, updatedAt: serverTimestamp() }, { merge: true })
}

export async function getPreferences(): Promise<UserPreferences | null> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return null

  const snap = await getDoc(preferencesRef(uid))
  return snap.exists() ? (snap.data() as UserPreferences) : null
}

/* ── Continue Learning ───────────────────────────────────── */

export interface ContinueLearningData {
  subjectId: string
  subjectTitle: string
  topicTitle: string
  path: string
  color: string
  updatedAt?: ReturnType<typeof serverTimestamp>
}

export async function saveContinueLearning(
  data: Omit<ContinueLearningData, 'updatedAt'>
): Promise<void> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return

  const ref = doc(db, 'userProgress', uid, 'settings', 'continueLearning')
  await setDoc(ref, { ...data, updatedAt: serverTimestamp() }, { merge: true })
}

export async function getContinueLearning(): Promise<ContinueLearningData | null> {
  await authReady
  const uid = currentUser?.uid
  if (!uid) return null

  const ref = doc(db, 'userProgress', uid, 'settings', 'continueLearning')
  const snap = await getDoc(ref)
  return snap.exists() ? (snap.data() as ContinueLearningData) : null
}

/** Subscribe to real-time updates for continue learning */
export function subscribeContinueLearning(
  callback: (data: ContinueLearningData | null) => void
): Promise<Unsubscribe> {
  return authReady.then((user) => {
    const ref = doc(db, 'userProgress', user.uid, 'settings', 'continueLearning')
    return onSnapshot(ref, (snap) => {
      callback(snap.exists() ? (snap.data() as ContinueLearningData) : null)
    })
  })
}
