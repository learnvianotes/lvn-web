/* ============================================================
   SPEECH — read-aloud built on the browser's Web Speech API
   (no network, no cost). Text is spoken one segment at a time,
   so the current paragraph can be highlighted and followed, and
   long pages never hit Chrome's ~15 s utterance cut-off.
   ============================================================ */

import { useSyncExternalStore } from 'react'
import { get, set } from '@/services/storage'
import { track } from '@/features/telemetry/track'

export interface Segment {
  text: string
  /** element highlighted while this segment is read */
  el?: HTMLElement | null
}

export interface SpeechState {
  status: 'idle' | 'playing' | 'paused'
  title: string
  index: number
  total: number
  rate: number
  voiceURI: string
}

export const speechSupported = typeof window !== 'undefined' && 'speechSynthesis' in window
export const RATES = [0.75, 1, 1.25, 1.5, 1.75, 2]

let segments: Segment[] = []
let state: SpeechState = {
  status: 'idle',
  title: '',
  index: 0,
  total: 0,
  rate: get<number>('speech-rate') ?? 1,
  voiceURI: get<string>('speech-voice') ?? '',
}
const listeners = new Set<() => void>()
let highlighted: HTMLElement | null = null
/** bumped on every start/stop so callbacks of cancelled utterances are ignored */
let run = 0

function setState(patch: Partial<SpeechState>) {
  state = { ...state, ...patch }
  document.documentElement.dataset.speaking = String(state.status === 'playing')
  listeners.forEach((l) => l())
}

export function useSpeech(): SpeechState {
  return useSyncExternalStore((l) => { listeners.add(l); return () => { listeners.delete(l) } }, () => state)
}

/* ── voices ──────────────────────────────────────────────── */

let voices: SpeechSynthesisVoice[] = []
const voiceListeners = new Set<() => void>()
if (speechSupported) {
  const loadVoices = () => {
    const lang = navigator.language.slice(0, 2)
    voices = speechSynthesis.getVoices().filter((v) => v.lang.startsWith('en') || v.lang.startsWith(lang))
    voiceListeners.forEach((l) => l())
  }
  loadVoices()
  speechSynthesis.addEventListener?.('voiceschanged', loadVoices)
}
export function useVoices() {
  return useSyncExternalStore((l) => { voiceListeners.add(l); return () => { voiceListeners.delete(l) } }, () => voices)
}

function pickVoice(): SpeechSynthesisVoice | undefined {
  const chosen = voices.find((v) => v.voiceURI === state.voiceURI)
  if (chosen) return chosen
  const en = voices.filter((v) => v.lang.startsWith('en'))
  return (
    en.find((v) => /natural|neural|enhanced|premium/i.test(v.name)) ??
    en.find((v) => /google|samantha|daniel|karen|aria|jenny/i.test(v.name)) ??
    en.find((v) => v.default) ??
    en[0]
  )
}

/* ── playback ────────────────────────────────────────────── */

function highlight(el: HTMLElement | null | undefined) {
  highlighted?.classList.remove('is-speaking')
  highlighted = el ?? null
  if (!el) return
  el.classList.add('is-speaking')
  const r = el.getBoundingClientRect()
  if (r.top < 80 || r.bottom > window.innerHeight - 120) el.scrollIntoView({ block: 'center', behavior: 'smooth' })
}

function speakAt(i: number) {
  const id = ++run
  speechSynthesis.cancel()
  if (i < 0 || i >= segments.length) return stop()
  const seg = segments[i]
  highlight(seg.el)
  setState({ status: 'playing', index: i })
  const u = new SpeechSynthesisUtterance(seg.text)
  u.rate = state.rate
  const voice = pickVoice()
  if (voice) { u.voice = voice; u.lang = voice.lang }
  u.onend = () => { if (id === run) speakAt(i + 1) }
  u.onerror = (e) => { if (id === run && e.error !== 'interrupted' && e.error !== 'canceled') speakAt(i + 1) }
  speechSynthesis.speak(u)
}

export function speak(title: string, segs: Segment[]) {
  if (!speechSupported) return
  segments = segs.filter((s) => s.text.trim())
  setState({ title, total: segments.length })
  track('listen', { i: location.pathname, l: title, v: segments.length })
  speakAt(0)
}

/** Pausing cancels and resumes from the same segment (reliable on every browser). */
export function pause() {
  run++
  speechSynthesis.cancel()
  setState({ status: 'paused' })
}
export const resume = () => speakAt(state.index)
export const next = () => speakAt(Math.min(state.index + 1, segments.length - 1))
export const previous = () => speakAt(Math.max(state.index - 1, 0))

export function stop() {
  run++
  if (speechSupported) speechSynthesis.cancel()
  highlight(null)
  segments = []
  setState({ status: 'idle', index: 0, total: 0, title: '' })
}

export function setRate(rate: number) {
  set('speech-rate', rate)
  setState({ rate })
  if (state.status === 'playing') speakAt(state.index)
}

export function setVoice(voiceURI: string) {
  set('speech-voice', voiceURI)
  setState({ voiceURI })
  if (state.status === 'playing') speakAt(state.index)
}

/* ── turning page content into segments ──────────────────── */

const READABLE = 'h2, h3, h4, p, li, tr, dt, dd, .callout-label, .flow-node, .step-title, .step-desc, .chip, .formula'
const SKIP = 'figure.code, pre, .copy-btn, .tab-bar, .gantt, .bits, button, [aria-hidden="true"], .pc-actions, .code-tabs, .study-kit'

export function cleanText(text: string) {
  return text
    .replace(/\s+/g, ' ')
    .replace(/→|⟶|->/g, ' to ')
    .replace(/←|<-/g, ' from ')
    .replace(/≤/g, ' less than or equal to ')
    .replace(/≥/g, ' greater than or equal to ')
    .replace(/≠/g, ' not equal to ')
    .replace(/[•·]/g, ', ')
    .trim()
}

/** Splits long text at sentence ends so each utterance stays short. */
function chunks(text: string, max = 240): string[] {
  if (text.length <= max) return [text]
  const out: string[] = []
  let cur = ''
  for (const s of text.split(/(?<=[.!?;:])\s+/)) {
    if (cur && (cur + ' ' + s).length > max) { out.push(cur); cur = s }
    else cur = cur ? `${cur} ${s}` : s
  }
  if (cur) out.push(cur)
  return out
}

/** Readable blocks of a rendered page, in reading order, without code. */
export function segmentsFrom(root: HTMLElement): Segment[] {
  const picked = new Set<Element>()
  const out: Segment[] = []
  for (const el of root.querySelectorAll<HTMLElement>(READABLE)) {
    if (el.closest(SKIP)) continue
    let a = el.parentElement
    let nested = false
    while (a && a !== root) { if (picked.has(a)) { nested = true; break } a = a.parentElement }
    if (nested) continue
    picked.add(el)
    const text = el.tagName === 'TR'
      ? [...el.children].map((c) => c.textContent?.trim()).filter(Boolean).join(', ')
      : el.textContent ?? ''
    const clean = cleanText(text)
    if (clean.length < 2) continue
    const isHeading = /^H[2-4]$/.test(el.tagName)
    for (const c of chunks(isHeading ? `${clean}.` : clean)) out.push({ text: c, el })
  }
  return out
}
