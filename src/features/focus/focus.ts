/* ============================================================
   FOCUS TIMER — a Pomodoro-style countdown. Survives reloads
   (the end time is stored). Completed focus sessions are added
   to today's activity and count toward the streak; breaks don't.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import { get, set } from '@/services/storage'
import { addFocusTime } from '@/features/progress/activity'
import { track } from '@/features/telemetry/track'

export type FocusKind = 'focus' | 'break'

export interface FocusState {
  phase: 'idle' | 'running' | 'paused' | 'done'
  kind: FocusKind
  /** total length in seconds */
  duration: number
  /** epoch ms when a running timer ends */
  endsAt: number
  /** seconds left when paused */
  remaining: number
  /** seconds already credited to today's activity */
  credited: number
  sound: boolean
}

const KEY = 'focus'
const initial: FocusState = { phase: 'idle', kind: 'focus', duration: 25 * 60, endsAt: 0, remaining: 0, credited: 0, sound: true }

let state: FocusState = { ...initial, ...(get<Partial<FocusState>>(KEY) ?? {}) }
const listeners = new Set<() => void>()

function setState(next: FocusState) {
  state = next
  set(KEY, state)
  listeners.forEach((l) => l())
}

export function useFocus(): FocusState {
  return useSyncExternalStore((l) => { listeners.add(l); return () => { listeners.delete(l) } }, () => state)
}

export function secondsLeft(s: FocusState, now = Date.now()) {
  if (s.phase === 'running') return Math.max(0, Math.round((s.endsAt - now) / 1000))
  if (s.phase === 'paused') return s.remaining
  if (s.phase === 'done') return 0
  return s.duration
}

/** Credit focus minutes as they happen (so an abandoned session still counts what was done). */
function credit(s: FocusState): FocusState {
  if (s.kind !== 'focus') return s
  const elapsed = s.duration - secondsLeft(s)
  const add = elapsed - s.credited
  if (add > 0) addFocusTime(add)
  return { ...s, credited: Math.max(s.credited, elapsed) }
}

export function start(minutes: number, kind: FocusKind = 'focus') {
  const duration = Math.round(Math.min(180, Math.max(1, minutes)) * 60)
  unlockAudio()
  setState({ ...state, phase: 'running', kind, duration, endsAt: Date.now() + duration * 1000, remaining: 0, credited: 0 })
}

export function pauseFocus() {
  if (state.phase !== 'running') return
  const s = credit(state)
  setState({ ...s, phase: 'paused', remaining: secondsLeft(state) })
}

export function resumeFocus() {
  if (state.phase !== 'paused') return
  setState({ ...state, phase: 'running', endsAt: Date.now() + state.remaining * 1000 })
}

export function resetFocus() {
  const s = state.phase === 'running' ? credit(state) : state
  setState({ ...initial, sound: s.sound, duration: s.kind === 'focus' ? s.duration : initial.duration })
}

export function toggleSound() {
  setState({ ...state, sound: !state.sound })
}

/** Called every second by the header timer. */
export function tick() {
  if (state.phase !== 'running') return
  if (secondsLeft(state) > 0) {
    // Credit once a minute to keep writes low.
    if (state.kind === 'focus' && state.duration - secondsLeft(state) - state.credited >= 60) setState(credit(state))
    return
  }
  const s = credit(state)
  setState({ ...s, phase: 'done' })
  if (s.kind === 'focus') track('focus_complete', { v: s.duration })
  if (s.sound) chime()
}

/* ── sound ───────────────────────────────────────────────── */

let ctx: AudioContext | null = null
function unlockAudio() {
  try {
    ctx ??= new AudioContext()
    if (ctx.state === 'suspended') void ctx.resume()
  } catch { /* no audio */ }
}

export function chime() {
  try {
    ctx ??= new AudioContext()
    const t = ctx.currentTime
    ;[523.25, 659.25, 783.99].forEach((f, i) => {
      const o = ctx!.createOscillator()
      const g = ctx!.createGain()
      o.type = 'sine'
      o.frequency.value = f
      g.gain.setValueAtTime(0, t + i * 0.18)
      g.gain.linearRampToValueAtTime(0.18, t + i * 0.18 + 0.02)
      g.gain.exponentialRampToValueAtTime(0.001, t + i * 0.18 + 0.9)
      o.connect(g).connect(ctx!.destination)
      o.start(t + i * 0.18)
      o.stop(t + i * 0.18 + 1)
    })
  } catch { /* no audio */ }
}

export function formatClock(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}
