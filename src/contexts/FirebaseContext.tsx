/* ============================================================
   FirebaseContext — React context for Firebase / Firestore
   Provides the current Firebase user (anonymous) and Firestore
   db instance app-wide. Uses anonymous sign-in so no login
   prompt is shown to the user.
   ============================================================ */

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import type { User } from 'firebase/auth'
import { db, auth } from '@/lib/firebase'
import { onAuthStateChanged, signInAnonymously } from 'firebase/auth'
import type { Firestore } from 'firebase/firestore'

interface FirebaseContextValue {
  user: User | null
  /** true while auth state is resolving */
  authLoading: boolean
  db: Firestore
}

const FirebaseContext = createContext<FirebaseContextValue>({
  user: null,
  authLoading: true,
  db,
})

export function FirebaseProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [authLoading, setAuthLoading] = useState(true)

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser)
        setAuthLoading(false)
      } else {
        try {
          const cred = await signInAnonymously(auth)
          setUser(cred.user)
        } catch (err) {
          console.warn('[C-Note] Anonymous sign-in failed:', err)
          setUser(null)
        } finally {
          setAuthLoading(false)
        }
      }
    })

    return () => unsubscribe()
  }, [])

  return (
    <FirebaseContext.Provider value={{ user, authLoading, db }}>
      {children}
    </FirebaseContext.Provider>
  )
}

/** Hook — consume Firebase user and db anywhere */
export function useFirebase() {
  return useContext(FirebaseContext)
}
