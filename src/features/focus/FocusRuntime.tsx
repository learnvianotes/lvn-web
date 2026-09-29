/* ============================================================
   FocusRuntime — mounted once by the app shell (signed in).
     • drives the countdown (every second, and immediately when
       the page becomes visible again)
     • FocusDock: a small floating timer shown on every page
       while a session runs, so it's always in view
     • FocusComplete: the end-of-session screen with next steps
   ============================================================ */

import './focus.css'
import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Check, ChevronDown, ChevronUp, Coffee, Pause, Play, RotateCcw, Square } from 'lucide-react'
import {
  formatClock, formatDuration, pauseFocus, rearmChime, resetFocus, resumeFocus, secondsLeft, start, startSeconds, tick, useFocus,
} from '@/features/focus/focus'
import { get, set } from '@/services/storage'
import { syncClock, useSecondTick } from './clock'

/* ── runtime ─────────────────────────────────────────────── */

export function FocusRuntime() {
  const s = useFocus()
  const running = s.phase === 'running'
  useSecondTick(running)

  // Browsers throttle timers in background tabs: check the moment the learner comes back.
  useEffect(() => {
    const onVisible = () => { if (document.visibilityState === 'visible') { syncClock(); tick() } }
    document.addEventListener('visibilitychange', onVisible)
    window.addEventListener('focus', onVisible)
    tick()
    return () => {
      document.removeEventListener('visibilitychange', onVisible)
      window.removeEventListener('focus', onVisible)
    }
  }, [])

  // A reload loses the queued chime (audio needs a user gesture): queue it again on the first interaction.
  useEffect(() => {
    if (!running) return
    const arm = () => rearmChime()
    window.addEventListener('pointerdown', arm, { once: true })
    window.addEventListener('keydown', arm, { once: true })
    return () => { window.removeEventListener('pointerdown', arm); window.removeEventListener('keydown', arm) }
  }, [running])

  return createPortal(
    <>
      {(s.phase === 'running' || s.phase === 'paused') && <FocusDock />}
      {s.phase === 'done' && <FocusComplete />}
    </>,
    document.body,
  )
}

/* ── floating timer ──────────────────────────────────────── */

const COLLAPSED_KEY = 'focus:dock-collapsed'

function FocusDock() {
  const s = useFocus()
  const [collapsed, setCollapsed] = useState(() => get<boolean>(COLLAPSED_KEY) ?? false)
  const left = secondsLeft(s)
  const ratio = s.duration ? 1 - left / s.duration : 0
  const paused = s.phase === 'paused'
  const toggleCollapsed = () => setCollapsed((c) => { set(COLLAPSED_KEY, !c); return !c })
  const label = s.kind === 'focus' ? 'Focus' : 'Break'

  return (
    <div
      className={`focus-dock ${collapsed ? 'is-collapsed' : ''} ${s.kind === 'break' ? 'is-break' : ''} ${paused ? 'is-paused' : ''}`}
      role="timer"
      aria-label={`${label} timer, ${formatClock(left)} left${paused ? ', paused' : ''}`}
    >
      <Ring ratio={ratio} size={collapsed ? 26 : 40} />
      <div className="focus-dock-text">
        <span className="focus-dock-clock">{formatClock(left)}</span>
        {!collapsed && <span className="focus-dock-label">{label}{paused ? ' · paused' : ''}</span>}
      </div>
      {!collapsed && (
        <div className="focus-dock-actions">
          {paused ? (
            <button className="icon-btn sm" onClick={resumeFocus} aria-label="Resume"><Play size={15} /></button>
          ) : (
            <button className="icon-btn sm" onClick={pauseFocus} aria-label="Pause"><Pause size={15} /></button>
          )}
          <button className="icon-btn sm" onClick={resetFocus} aria-label="Stop the session"><Square size={13} /></button>
        </div>
      )}
      <button className="icon-btn sm focus-dock-toggle" onClick={toggleCollapsed} aria-label={collapsed ? 'Expand timer' : 'Minimise timer'}>
        {collapsed ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
      </button>
    </div>
  )
}

function Ring({ ratio, size }: { ratio: number; size: number }) {
  const r = 16
  const c = 2 * Math.PI * r
  return (
    <svg className="focus-dock-ring" width={size} height={size} viewBox="0 0 40 40" aria-hidden>
      <circle cx="20" cy="20" r={r} />
      <circle cx="20" cy="20" r={r} style={{ strokeDasharray: c, strokeDashoffset: c * (1 - ratio) }} />
    </svg>
  )
}

/* ── end of session ──────────────────────────────────────── */

function FocusComplete() {
  const s = useFocus()
  const primary = useRef<HTMLButtonElement>(null)
  const focus = s.kind === 'focus'

  useEffect(() => {
    primary.current?.focus()
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') resetFocus() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <div className="focus-complete" role="alertdialog" aria-modal="true" aria-labelledby="focus-complete-title" onClick={(e) => { if (e.target === e.currentTarget) resetFocus() }}>
      <div className="focus-complete-card">
        <div className={`focus-complete-badge ${focus ? '' : 'is-break'}`} aria-hidden>
          {focus ? <Check size={30} strokeWidth={3} /> : <Coffee size={28} />}
        </div>
        <h2 id="focus-complete-title">{focus ? 'Session complete!' : 'Break’s over'}</h2>
        <p className="muted">
          {focus
            ? `${formatDuration(s.duration)} of focus added to today’s streak. Take a short break before the next one.`
            : 'Refreshed? Start another focus session.'}
        </p>
        <div className="focus-complete-actions">
          {focus ? (
            <>
              <button ref={primary} className="btn btn-primary" onClick={() => start(5, 'break')}><Coffee size={15} aria-hidden /> 5 min break</button>
              <button className="btn" onClick={() => startSeconds(s.duration)}><RotateCcw size={15} aria-hidden /> Again ({formatClock(s.duration)})</button>
            </>
          ) : (
            <button ref={primary} className="btn btn-primary" onClick={() => start(25)}><Play size={15} aria-hidden /> Focus 25 min</button>
          )}
          <button className="btn" onClick={resetFocus}>Done</button>
        </div>
      </div>
    </div>
  )
}
