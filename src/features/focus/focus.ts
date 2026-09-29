/* ============================================================
   FOCUS TIMER — a Pomodoro-style countdown. Survives reloads
   (the end time is stored). Completed focus sessions are added
   to today's activity and count toward the streak; breaks don't.

   The end is announced reliably even when the tab is in the
   background (where browsers throttle timers): the chime is
   scheduled on the audio clock for the exact end time when the
   session starts, and a system notification / vibration is used
   when the page isn't visible.
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

/** Shortest and longest session, in seconds. */
export const MIN_SECONDS = 5
export const MAX_SECONDS = 180 * 60

export function start(minutes: number, kind: FocusKind = 'focus') {
  startSeconds(minutes * 60, kind)
}

/** Start a session of `seconds` (called from a click, so audio and notifications can be unlocked). */
export function startSeconds(seconds: number, kind: FocusKind = 'focus') {
  const duration = Math.round(Math.min(MAX_SECONDS, Math.max(MIN_SECONDS, seconds)))
  unlockAudio()
  askNotificationPermission()
  const endsAt = Date.now() + duration * 1000
  setState({ ...state, phase: 'running', kind, duration, endsAt, remaining: 0, credited: 0 })
  scheduleChime(endsAt)
}

export function pauseFocus() {
  if (state.phase !== 'running') return
  cancelChime()
  const s = credit(state)
  setState({ ...s, phase: 'paused', remaining: secondsLeft(state) })
}

export function resumeFocus() {
  if (state.phase !== 'paused') return
  unlockAudio()
  const endsAt = Date.now() + state.remaining * 1000
  setState({ ...state, phase: 'running', endsAt })
  scheduleChime(endsAt)
}

export function resetFocus() {
  cancelChime()
  const s = state.phase === 'running' ? credit(state) : state
  setState({ ...initial, sound: s.sound, duration: s.kind === 'focus' ? s.duration : initial.duration })
}

export function toggleSound() {
  const sound = !state.sound
  setState({ ...state, sound })
  if (!sound) cancelChime()
  else if (state.phase === 'running') { unlockAudio(); scheduleChime(state.endsAt) }
}

/** Checks for the end — called every second by FocusRuntime and whenever the page becomes visible. */
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
  announceEnd(s)
}

function announceEnd(s: FocusState) {
  // The pre-scheduled chime has already played (or is playing) if the audio clock kept running.
  if (s.sound && !(scheduled && ctx?.state === 'running')) chime()
  scheduled = null
  try { navigator.vibrate?.([220, 120, 220]) } catch { /* not supported */ }
  if (document.visibilityState !== 'visible' && 'Notification' in window && Notification.permission === 'granted') {
    try {
      const n = new Notification(s.kind === 'focus' ? 'Focus session complete 🎉' : 'Break’s over', {
        body: s.kind === 'focus' ? `${formatDuration(s.duration)} of focus added to today.` : 'Ready for another round?',
        icon: '/icons/icon-192.png',
        tag: 'lvn-focus',
      })
      n.onclick = () => { window.focus(); n.close() }
    } catch { /* e.g. mobile browsers that only allow notifications from a service worker */ }
  }
}

/* ── sound ───────────────────────────────────────────────── */

let ctx: AudioContext | null = null
let scheduled: { nodes: OscillatorNode[]; endsAt: number } | null = null

function audio(): AudioContext | null {
  try {
    ctx ??= new AudioContext()
    return ctx
  } catch {
    return null
  }
}

/** Must run inside a click: browsers only allow audio that a user gesture started. */
function unlockAudio() {
  const a = audio()
  if (a && a.state !== 'running') void a.resume().catch(() => {})
}

function playNotes(a: AudioContext, at: number): OscillatorNode[] {
  return [523.25, 659.25, 783.99, 1046.5].map((f, i) => {
    const t = at + i * 0.16
    const o = a.createOscillator()
    const g = a.createGain()
    o.type = 'sine'
    o.frequency.value = f
    g.gain.setValueAtTime(0, t)
    g.gain.linearRampToValueAtTime(0.22, t + 0.02)
    g.gain.exponentialRampToValueAtTime(0.001, t + 1.1)
    o.connect(g).connect(a.destination)
    o.start(t)
    o.stop(t + 1.2)
    return o
  })
}

/** Queue the chime on the audio clock for the end of the session (plays even if the tab is throttled). */
function scheduleChime(endsAt: number) {
  cancelChime()
  const a = audio()
  if (!a || !state.sound) return
  const delay = Math.max(0, (endsAt - Date.now()) / 1000)
  scheduled = { nodes: playNotes(a, a.currentTime + delay), endsAt }
}

function cancelChime() {
  for (const o of scheduled?.nodes ?? []) {
    try { o.stop() } catch { /* already stopped */ }
  }
  scheduled = null
}

/**
 * After a page reload the audio has to be unlocked again by a user gesture: call this from the first
 * tap / key press so the end-of-session chime is queued once more.
 */
export function rearmChime() {
  if (state.phase !== 'running' || !state.sound || scheduled) return
  unlockAudio()
  scheduleChime(state.endsAt)
}

/** Play the chime now (end of session, or the "test sound" button). */
export function chime() {
  const a = audio()
  if (!a) return
  const play = () => { playNotes(a, a.currentTime + 0.05) }
  if (a.state === 'running') play()
  else void a.resume().then(play, () => {})
}

/* ── notifications ───────────────────────────────────────── */

const ASKED_KEY = 'focus:notify-asked'

/** Ask once (from the first Start click) so the end can be announced while the tab is in the background. */
function askNotificationPermission() {
  if (!('Notification' in window) || Notification.permission !== 'default' || get<boolean>(ASKED_KEY)) return
  set(ASKED_KEY, true)
  void Notification.requestPermission().catch(() => {})
}

/* ── formatting ──────────────────────────────────────────── */

export function formatClock(seconds: number) {
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h ? `${h}:${mm}:${ss}` : `${mm}:${ss}`
}

/** "25 min", "1 min 30 s", "45 s" */
export function formatDuration(seconds: number) {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  if (!m) return `${s} s`
  return s ? `${m} min ${s} s` : `${m} min`
}
