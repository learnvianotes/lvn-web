/* ============================================================
   PROGRESS STORE
   Everything the learner does is kept in this browser
   (localStorage) — no accounts, no server.

     problems  problemId → 'solved' | 'revisit'
     topics    'subjectId/topicId' → true   (read to the end)
     studied   'YYYY-MM-DD' → things completed that day
               (a topic read to the end, or a problem solved).
               A day with ≥ 1 counts toward the streak.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import { get, set } from '@/lib/storage'

export type ProblemStatus = 'todo' | 'solved' | 'revisit'

export interface ProgressState {
  problems: Record<string, Exclude<ProblemStatus, 'todo'>>
  topics: Record<string, true>
  studied: Record<string, number>
}

const KEY = 'progress'
const empty: ProgressState = { problems: {}, topics: {}, studied: {} }

function load(): ProgressState {
  const saved = get<Partial<ProgressState>>(KEY) ?? {}
  return { problems: saved.problems ?? {}, topics: saved.topics ?? {}, studied: saved.studied ?? {} }
}

let state: ProgressState = { ...empty, ...load() }
const listeners = new Set<() => void>()

function update(next: ProgressState) {
  state = next
  set(KEY, state)
  listeners.forEach((l) => l())
}

// Keep multiple tabs in sync.
window.addEventListener('storage', (e) => {
  if (e.key?.endsWith(KEY)) {
    state = load()
    listeners.forEach((l) => l())
  }
})

function subscribe(listener: () => void) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function useProgress(): ProgressState {
  return useSyncExternalStore(subscribe, () => state)
}

export function dayKey(d = new Date()) {
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${d.getFullYear()}-${m}-${day}`
}

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
}

export const topicKey = (subjectId: string, topicId: string) => `${subjectId}/${topicId}`

/** Called when a topic has genuinely been read to the end. */
export function completeTopic(subjectId: string, topicId: string) {
  const key = topicKey(subjectId, topicId)
  if (state.topics[key]) return
  update(withStudied({ ...state, topics: { ...state.topics, [key]: true } }))
}

export function uncompleteTopic(subjectId: string, topicId: string) {
  const topics = { ...state.topics }
  delete topics[topicKey(subjectId, topicId)]
  update({ ...state, topics })
}
