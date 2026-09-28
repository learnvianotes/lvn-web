/* ============================================================
   FocusTimer — header control. Idle: a timer icon. Running: a
   countdown pill with a progress ring. Click for presets,
   custom length, pause / reset and the end-of-session sound.
   ============================================================ */

import './focus.css'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Bell, BellOff, Coffee, Pause, Play, RotateCcw, Target, Timer } from 'lucide-react'
import { APP_NAME } from '@/config'
import {
  formatClock, pauseFocus, resetFocus, resumeFocus, secondsLeft, start, tick, toggleSound, useFocus,
} from '@/features/focus/focus'

const PRESETS = [15, 25, 45, 60]

export function FocusTimer() {
  const s = useFocus()
  const [open, setOpen] = useState(false)
  const [, force] = useState(0)
  const root = useRef<HTMLDivElement>(null)

  // Re-render every second while running (and let the store notice the end).
  useEffect(() => {
    if (s.phase !== 'running') return
    tick()
    const id = window.setInterval(() => { tick(); force((n) => n + 1) }, 1000)
    return () => window.clearInterval(id)
  }, [s.phase])

  // Show the countdown in the tab title while running; announce the end.
  const left = secondsLeft(s)
  useEffect(() => {
    if (s.phase === 'idle') return
    const base = document.title.replace(/^(\d\d:\d\d [·•] |✓ .*? · )/, '')
    document.title = s.phase === 'done'
      ? `✓ ${s.kind === 'focus' ? 'Focus done' : 'Break over'} · ${base}`
      : `${formatClock(left)} · ${base}`
    return () => { document.title = document.title.replace(/^(\d\d:\d\d · |✓ .*? · )/, '') || APP_NAME }
  }, [left, s.phase, s.kind])

  useEffect(() => { if (s.phase === 'done') setOpen(true) }, [s.phase])

  useEffect(() => {
    if (!open) return
    const onDown = (e: MouseEvent) => { if (!root.current?.contains(e.target as Node)) setOpen(false) }
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onDown)
    window.addEventListener('keydown', onKey)
    return () => { document.removeEventListener('mousedown', onDown); window.removeEventListener('keydown', onKey) }
  }, [open])

  const active = s.phase === 'running' || s.phase === 'paused'
  const ratio = s.duration ? 1 - left / s.duration : 0

  return (
    <div className="focus" ref={root}>
      <button
        className={`focus-btn ${active ? 'is-active' : ''} ${s.phase === 'paused' ? 'is-paused' : ''} ${s.kind === 'break' ? 'is-break' : ''} ${s.phase === 'done' ? 'is-done' : ''}`}
        onClick={() => setOpen((o) => !o)}
        aria-label={active ? `Focus timer, ${formatClock(left)} left` : 'Focus timer'}
        aria-expanded={open}
        title="Focus timer"
      >
        {active ? (
          <>
            <svg className="focus-ring" viewBox="0 0 20 20" aria-hidden>
              <circle cx="10" cy="10" r="8" />
              <circle cx="10" cy="10" r="8" style={{ strokeDashoffset: `${50.27 * (1 - ratio)}` }} />
            </svg>
            <span className="focus-clock">{formatClock(left)}</span>
          </>
        ) : (
          <Timer size={18} />
        )}
      </button>
      {open && <FocusPopover close={() => setOpen(false)} />}
    </div>
  )
}

function FocusPopover({ close }: { close: () => void }) {
  const s = useFocus()
  const [custom, setCustom] = useState('')
  const left = secondsLeft(s)

  const startCustom = (e: FormEvent) => {
    e.preventDefault()
    const m = Number(custom)
    if (m >= 1 && m <= 180) { start(m); setCustom('') }
  }

  return (
    <div className="focus-menu" role="dialog" aria-label="Focus timer">
      <div className="focus-menu-head">
        <strong><Target size={15} aria-hidden /> Focus time</strong>
        <button className="icon-btn sm" onClick={toggleSound} aria-label={s.sound ? 'Mute end sound' : 'Play a sound at the end'} title={s.sound ? 'Sound on' : 'Sound off'}>
          {s.sound ? <Bell size={15} /> : <BellOff size={15} />}
        </button>
      </div>

      {s.phase === 'done' ? (
        <div className="focus-done">
          <p className="focus-done-title">{s.kind === 'focus' ? '🎉 Session complete!' : 'Break’s over'}</p>
          <p className="muted small">
            {s.kind === 'focus' ? `${Math.round(s.duration / 60)} focused minutes added to today’s streak.` : 'Ready for another round?'}
          </p>
          <div className="focus-actions">
            {s.kind === 'focus' ? (
              <button className="btn btn-sm" onClick={() => start(5, 'break')}><Coffee size={14} aria-hidden /> 5 min break</button>
            ) : (
              <button className="btn btn-sm btn-primary" onClick={() => start(25)}><Play size={14} aria-hidden /> Focus 25 min</button>
            )}
            <button className="btn btn-sm" onClick={() => { resetFocus(); close() }}>Done</button>
          </div>
        </div>
      ) : s.phase === 'idle' ? (
        <>
          <p className="muted small">Pick a session length. Stay on the page — your focus minutes count toward your streak.</p>
          <div className="focus-presets">
            {PRESETS.map((m) => (
              <button key={m} className="focus-preset" onClick={() => start(m)}>
                <strong>{m}</strong><span>min</span>
              </button>
            ))}
          </div>
          <form className="focus-custom" onSubmit={startCustom}>
            <input
              type="number"
              min={1}
              max={180}
              inputMode="numeric"
              placeholder="Custom minutes"
              value={custom}
              onChange={(e) => setCustom(e.target.value)}
              aria-label="Custom minutes"
            />
            <button className="btn btn-sm btn-primary" type="submit" disabled={!custom}>Start</button>
          </form>
        </>
      ) : (
        <>
          <div className="focus-big">
            <span className="focus-big-clock">{formatClock(left)}</span>
            <span className="muted small">{s.kind === 'focus' ? 'Focusing' : 'On a break'}{s.phase === 'paused' ? ' · paused' : ''}</span>
          </div>
          <div className="focus-actions">
            {s.phase === 'running' ? (
              <button className="btn btn-sm" onClick={pauseFocus}><Pause size={14} aria-hidden /> Pause</button>
            ) : (
              <button className="btn btn-sm btn-primary" onClick={resumeFocus}><Play size={14} aria-hidden /> Resume</button>
            )}
            <button className="btn btn-sm" onClick={resetFocus}><RotateCcw size={14} aria-hidden /> Reset</button>
          </div>
        </>
      )}
    </div>
  )
}
