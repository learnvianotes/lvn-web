/* ============================================================
   PROGRESS STORE
   Kept in this browser (localStorage). When the learner is signed
   in, progress/sync.ts mirrors it to their Firestore account.

     problems       problemId → 'solved' | 'revisit'
     topics         'subjectId/topicId' → true   (read to the end)
     revisitTopics  'subjectId/topicId' → true   (marked to revisit)
     studied        'YYYY-MM-DD' → things completed that day
                    (a topic read to the end, or a problem solved)
   ============================================================ */

import { useSyncExternalStore } from 'react'
import type { ProblemMark, ProgressData } from '@core-schema/firestore'
import { get, set } from '@core/services/storage'
import { useUser } from '@core/features/auth/auth'
import { dayKey } from '@core/shared/lib/date'
import { track } from '@core/features/telemetry/track'

export type ProblemStatus = 'todo' | ProblemMark
export type ProgressState = ProgressData

const KEY = 'progress'
export const emptyProgress = (): ProgressState => ({ problems: {}, topics: {}, revisitTopics: {}, studied: {} })

function load(): ProgressState {
  const saved = get<Partial<ProgressState>>(KEY) ?? {}
  return { ...emptyProgress(), ...saved }
}

let state: ProgressState = load()
const listeners = new Set<() => void>()
/** Changes made by the learner (not by sync) — sync.ts pushes these. */
const localListeners = new Set<() => void>()

function update(next: ProgressState, fromSync = false) {
  state = next
  set(KEY, state)
  listeners.forEach((l) => l())
  if (!fromSync) localListeners.forEach((l) => l())
}

// Keep multiple tabs in sync.
window.addEventListener('storage', (e) => {
  if (e.key?.endsWith(`:${KEY}`)) {
    state = load()
    listeners.forEach((l) => l())
  }
})

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => { listeners.delete(listener) }
}

const GUEST = emptyProgress()

/** The learner's progress — empty for guests (tracking is a signed-in feature). */
export function useProgress(): ProgressState {
  const user = useUser()
  const s = useSyncExternalStore(subscribe, () => state)
  return user ? s : GUEST
}

export const getProgress = () => state
/** Used by sync: replace everything without triggering another upload. */
export const replaceProgress = (next: ProgressState) => update(next, true)
export function onLocalProgressChange(listener: () => void) {
  localListeners.add(listener)
  return () => { localListeners.delete(listener) }
}

export { dayKey }

function withStudied(s: ProgressState): ProgressState {
  const today = dayKey()
  return { ...s, studied: { ...s.studied, [today]: (s.studied[today] ?? 0) + 1 } }
}

export function setProblemStatus(problemId: string, status: ProblemStatus) {
  const problems = { ...state.problems }
  const newlySolved = status === 'solved' && problems[problemId] !== 'solved'
  if (status === 'todo') delete problems[problemId]
  else problems[problemId] = status
  const next = { ...state, problems }
  update(newlySolved ? withStudied(next) : next)
  track('problem_status', { i: problemId, l: status })
}

export const topicKey = (subjectId: string, topicId: string) => `${subjectId}/${topicId}`

/** Called when a topic has genuinely been read to the end. */
export function completeTopic(subjectId: string, topicId: string) {
  const key = topicKey(subjectId, topicId)
  if (state.topics[key]) return
  update(withStudied({ ...state, topics: { ...state.topics, [key]: true } }))
  track('topic_complete', { s: subjectId, k: topicId })
}

export function uncompleteTopic(subjectId: string, topicId: string) {
  const topics = { ...state.topics }
  delete topics[topicKey(subjectId, topicId)]
  update({ ...state, topics })
}

export function toggleTopicRevisit(subjectId: string, topicId: string) {
  const key = topicKey(subjectId, topicId)
  const revisitTopics = { ...state.revisitTopics }
  if (revisitTopics[key]) delete revisitTopics[key]
  else revisitTopics[key] = true
  update({ ...state, revisitTopics })
  track('topic_revisit', { s: subjectId, k: topicId, v: revisitTopics[key] ? 1 : 0 })
}
