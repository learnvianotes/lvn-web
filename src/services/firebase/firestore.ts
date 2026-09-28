/* Firestore (lite) — import this module lazily. */

import { connectFirestoreEmulator, getFirestore, type Firestore } from 'firebase/firestore/lite'
import { firebaseApp } from './app'

let instance: Firestore | undefined

export function db(): Firestore {
  if (instance) return instance
  instance = getFirestore(firebaseApp())
  const emulator = import.meta.env.DEV ? import.meta.env.VITE_FIRESTORE_EMULATOR : undefined
  if (emulator) {
    const [host, port] = emulator.split(':')
    connectFirestoreEmulator(instance, host, Number(port))
  }
  return instance
}
