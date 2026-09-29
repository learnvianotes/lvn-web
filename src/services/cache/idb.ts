/* ============================================================
   A tiny IndexedDB key–value store (one database, one object
   store). Used to keep study content on the device. Every call
   fails soft: if IndexedDB is unavailable (private mode, blocked),
   reads return undefined and writes are skipped.
   ============================================================ */

const DB_NAME = 'lvn-cache'
const STORE = 'kv'

let dbp: Promise<IDBDatabase | null> | null = null

function open(): Promise<IDBDatabase | null> {
  dbp ??= new Promise((resolve) => {
    try {
      const req = indexedDB.open(DB_NAME, 1)
      req.onupgradeneeded = () => req.result.createObjectStore(STORE)
      req.onsuccess = () => resolve(req.result)
      req.onerror = () => resolve(null)
      req.onblocked = () => resolve(null)
    } catch {
      resolve(null)
    }
  })
  return dbp
}

function run<T>(mode: IDBTransactionMode, fn: (s: IDBObjectStore) => IDBRequest<T> | void): Promise<T | undefined> {
  return open().then((db) => new Promise<T | undefined>((resolve) => {
    if (!db) return resolve(undefined)
    try {
      const tx = db.transaction(STORE, mode)
      const req = fn(tx.objectStore(STORE))
      tx.oncomplete = () => resolve(req ? req.result : undefined)
      tx.onerror = () => resolve(undefined)
      tx.onabort = () => resolve(undefined)
    } catch {
      resolve(undefined)
    }
  }))
}

export const idbGet = <T>(key: string) => run<T>('readonly', (s) => s.get(key) as IDBRequest<T>)
export const idbSet = (key: string, value: unknown) => run('readwrite', (s) => { s.put(value, key) }).then(() => undefined)
export const idbClear = () => run('readwrite', (s) => { s.clear() }).then(() => undefined)
