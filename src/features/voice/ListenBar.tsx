/* ============================================================
   ListenBar — floating player while read-aloud is active:
   previous / play-pause / next, speed, voice and stop.
   Mounted once in the app shell.
   ============================================================ */

import './voice.css'
import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { AudioLines, Pause, Play, SkipBack, SkipForward, X } from 'lucide-react'
import { RATES, next, pause, previous, resume, setRate, setVoice, stop, useSpeech, useVoices } from '@/features/voice/speech'

export function ListenBar() {
  const s = useSpeech()
  const voices = useVoices()
  const location = useLocation()

  // Segments point at the page's elements — stop when the page changes.
  useEffect(() => stop, [location.pathname])

  useEffect(() => {
    if (s.status === 'idle') return
    const onKey = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLElement && e.target.closest('input, textarea, select, [contenteditable]')) return
      if (e.key === 'Escape') stop()
      else if (e.key === 'k' && !e.metaKey && !e.ctrlKey) {
        e.preventDefault()
        if (s.status === 'playing') pause()
        else resume()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [s.status])

  if (s.status === 'idle') return null
  const pct = s.total ? ((s.index + 1) / s.total) * 100 : 0

  return (
    <div className="listen-bar" role="region" aria-label="Read aloud">
      <span className="listen-progress" style={{ width: `${pct}%` }} aria-hidden />
      <span className={`listen-wave ${s.status === 'playing' ? 'is-on' : ''}`} aria-hidden><AudioLines size={18} /></span>
      <span className="listen-title">
        <strong>{s.title}</strong>
        <span className="muted small">{s.index + 1} / {s.total}</span>
      </span>
      <div className="listen-controls">
        <button className="icon-btn sm" onClick={previous} aria-label="Previous paragraph"><SkipBack size={16} /></button>
        <button className="icon-btn listen-play" onClick={s.status === 'playing' ? pause : resume} aria-label={s.status === 'playing' ? 'Pause' : 'Resume'}>
          {s.status === 'playing' ? <Pause size={18} /> : <Play size={18} />}
        </button>
        <button className="icon-btn sm" onClick={next} aria-label="Next paragraph"><SkipForward size={16} /></button>
      </div>
      <select className="listen-select" value={s.rate} onChange={(e) => setRate(Number(e.target.value))} aria-label="Speed">
        {RATES.map((r) => <option key={r} value={r}>{r}×</option>)}
      </select>
      {voices.length > 1 && (
        <select className="listen-select listen-voice" value={s.voiceURI} onChange={(e) => setVoice(e.target.value)} aria-label="Voice">
          <option value="">Auto voice</option>
          {voices.map((v) => <option key={v.voiceURI} value={v.voiceURI}>{v.name.replace(/^(Microsoft|Google)\s/, '')}</option>)}
        </select>
      )}
      <button className="icon-btn sm" onClick={stop} aria-label="Stop reading"><X size={16} /></button>
    </div>
  )
}
