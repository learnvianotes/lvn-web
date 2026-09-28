/* ============================================================
   SYNC — keeps the local stores (progress, activity, notes,
   prefs) and the signed-in learner's server data in step,
   through the UserDataRepository (services/userdata).

   • First sync after signing in merges anything on this device
     into the account.
   • Local changes upload ~2 s later, and at once when the tab
     is hidden or the connection returns.
   • Coming back to the tab pulls changes from other devices.
   • Signing out uploads pending changes, then wipes the local
     copy — nothing is left behind on a shared computer.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import { getAuthState, onBeforeSignOut, subscribeAuth } from '@/features/auth/auth'
import { firebaseConfigured } from '@/services/firebase/app'
import { get, remove, set } from '@/services/storage'
import { userData } from '@/services/userdata/repository'
import { emptyProgress, getProgress, onLocalProgressChange, replaceProgress, type ProgressState } from './store'
import { getActivity, onLocalActivityChange, replaceActivity, type Activity, type DayLog } from './activity'
import { getNotes, onLocalNoteChange, replaceNotes, type Notes } from './notes'
import { defaultPrefs, getPrefs, onLocalPrefsChange, replacePrefs } from './prefs'

/* ── status (shown in the account menu) ─────────────────── */

export type SyncStatus = 'off' | 'syncing' | 'synced' | 'error'
let status: SyncStatus = 'off'
const statusListeners = new Set<() => void>()
function setStatus(s: SyncStatus) {
  status = s
  statusListeners.forEach((l) => l())
}
export function useSyncStatus() {
  return useSyncExternalStore((l) => { statusListeners.add(l); return () => { statusListeners.delete(l) } }, () => status)
}

/* ── state ───────────────────────────────────────────────── */

const OWNER = 'owner' // uid the local data belongs to
const DEBOUNCE_MS = 2000
const REFRESH_EVERY_MS = 60_000

let uid: string | null = null
let timer = 0
let lastPull = 0
const dirty = { progress: false, prefs: false, days: new Set<string>(), notes: new Set<string>() }

/* ── merging ─────────────────────────────────────────────── */

function mergeProgress(local: ProgressState, remote: ProgressState): ProgressState {
  const studied = { ...remote.studied }
  for (const [day, n] of Object.entries(local.studied)) studied[day] = Math.max(n, studied[day] ?? 0)
  return {
    problems: { ...remote.problems, ...local.problems },
    topics: { ...remote.topics, ...local.topics },
    revisitTopics: { ...remote.revisitTopics, ...local.revisitTopics },
    studied,
  }
}

function mergeDay(a: DayLog | undefined, b: DayLog | undefined): DayLog {
  const topics = { ...(b?.topics ?? {}) }
  for (const [key, v] of Object.entries(a?.topics ?? {})) {
    const o = topics[key]
    topics[key] = o
      ? { ...(v.last >= o.last ? v : o), sec: Math.max(v.sec, o.sec), visits: Math.max(v.visits, o.visits), last: Math.max(v.last, o.last) }
      : v
  }
  return { topics, focus: Math.max(a?.focus ?? 0, b?.focus ?? 0) }
}

const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b)

/* ── pull + merge ────────────────────────────────────────── */

async function pull(id: string, firstSync: boolean) {
  setStatus('syncing')
  const r = await (await userData()).fetchAll(id)
  if (uid !== id) return // signed out meanwhile

  // Progress: union on first sync or with unsent local changes; otherwise the account is the truth.
  const remoteProgress: ProgressState = { ...emptyProgress(), ...(r.progress ?? {}) }
  const progress = firstSync || dirty.progress ? mergeProgress(getProgress(), remoteProgress) : remoteProgress
  if (!same(progress, getProgress())) replaceProgress(progress)
  if (!same(progress, remoteProgress)) dirty.progress = true

  // Prefs: the newer edit wins.
  const localPrefs = getPrefs()
  const remotePrefs = { ...defaultPrefs(), ...(r.prefs ?? {}) }
  if (remotePrefs.updatedAt > localPrefs.updatedAt) replacePrefs(remotePrefs)
  else if (localPrefs.updatedAt > remotePrefs.updatedAt) dirty.prefs = true

  // Activity: per-topic maxima never lose time.
  const local = getActivity()
  const activity: Activity = {}
  for (const day of new Set([...Object.keys(local), ...Object.keys(r.days)])) {
    activity[day] = mergeDay(local[day], r.days[day])
    if (!same(activity[day], r.days[day])) dirty.days.add(day)
  }
  replaceActivity(activity)

  // Notes: the newer edit wins.
  const notes: Notes = { ...getNotes() }
  for (const [key, n] of r.notes) if (!notes[key] || notes[key].updatedAt < n.updatedAt) notes[key] = { text: n.text, updatedAt: n.updatedAt }
  for (const [key, n] of Object.entries(notes)) {
    const rn = r.notes.get(key)
    if ((!rn && n.text) || (rn && rn.updatedAt < n.updatedAt)) dirty.notes.add(key)
  }
  replaceNotes(notes)

  set(OWNER, id)
  lastPull = Date.now()
  await flush()
}

/* ── upload ──────────────────────────────────────────────── */

async function flush() {
  window.clearTimeout(timer)
  const id = uid
  if (!id) return
  if (!dirty.progress && !dirty.prefs && !dirty.days.size && !dirty.notes.size) {
    setStatus('synced')
    return
  }
  const activity = getActivity()
  const notes = getNotes()
  const sent = { progress: dirty.progress, prefs: dirty.prefs, days: [...dirty.days], notes: [...dirty.notes] }
  dirty.progress = false
  dirty.prefs = false
  dirty.days.clear()
  dirty.notes.clear()

  setStatus('syncing')
  try {
    await (await userData()).commit(id, {
      progress: sent.progress ? getProgress() : undefined,
      prefs: sent.prefs ? getPrefs() : undefined,
      days: sent.days.filter((d) => activity[d]).map((d) => [d, activity[d]]),
      notes: sent.notes.map((k) => [k, notes[k]]),
    })
    setStatus('synced')
  } catch {
    // Keep the changes for the next attempt.
    dirty.progress ||= sent.progress
    dirty.prefs ||= sent.prefs
    sent.days.forEach((d) => dirty.days.add(d))
    sent.notes.forEach((k) => dirty.notes.add(k))
    setStatus('error')
  }
}

function schedule() {
  if (!uid) return
  window.clearTimeout(timer)
  timer = window.setTimeout(() => void flush(), DEBOUNCE_MS)
}

/* ── local data lifecycle ────────────────────────────────── */

function clearLocal() {
  replaceProgress(emptyProgress())
  replaceActivity({})
  replaceNotes({})
  replacePrefs(defaultPrefs())
  remove(OWNER)
  dirty.progress = false
  dirty.prefs = false
  dirty.days.clear()
  dirty.notes.clear()
}

/** Pull + upload right away (Settings → "Sync now"). */
export async function syncNow() {
  if (!uid) return
  await flush()
  await pull(uid, false).catch(() => setStatus('error'))
}

/** Deletes everything stored for the signed-in learner (account deletion). */
export async function deleteMyData() {
  const id = uid
  if (!id) return
  await (await userData()).deleteAll(id)
  uid = null
  clearLocal()
  setStatus('off')
}

export function initSync() {
  if (!firebaseConfigured) return

  subscribeAuth(() => {
    const s = getAuthState()
    if (s.status === 'signed-in' && s.user.uid !== uid) {
      const owner = get<string>(OWNER)
      if (owner && owner !== s.user.uid) clearLocal() // another account's leftovers
      uid = s.user.uid
      pull(uid, true).catch(() => setStatus('error'))
    } else if (s.status === 'signed-out') {
      // Also covers sessions that ended elsewhere (expired / revoked).
      if (uid || get<string>(OWNER)) clearLocal()
      uid = null
      setStatus('off')
    }
  })

  onLocalProgressChange(() => { dirty.progress = true; schedule() })
  onLocalPrefsChange(() => { dirty.prefs = true; schedule() })
  onLocalActivityChange((day) => { dirty.days.add(day); schedule() })
  onLocalNoteChange((key) => { dirty.notes.add(key); schedule() })

  onBeforeSignOut(async () => {
    await flush()
    const id = uid
    uid = null
    if (id) clearLocal()
    setStatus('off')
  })

  document.addEventListener('visibilitychange', () => {
    if (!uid) return
    if (document.visibilityState === 'hidden') void flush()
    else if (Date.now() - lastPull > REFRESH_EVERY_MS) pull(uid, false).catch(() => setStatus('error'))
  })
  window.addEventListener('online', () => { if (uid) void flush() })
}
