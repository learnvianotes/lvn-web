/* ============================================================
   ProgressWheel — one equal slice per subject; the filled part
   of each slice grows outward with that subject's completion.
   Click a slice (or a breakdown row) to select the subject.
   ============================================================ */

import { useState } from 'react'
import type { SubjectProgress } from '@/features/progress/stats'

const SIZE = 196
const C = SIZE / 2
const R_IN = 40
const R_OUT = 94
const GAP = 0.025 // radians between slices

function sector(a0: number, a1: number, r0: number, r1: number) {
  const p = (r: number, a: number) => `${(C + r * Math.sin(a)).toFixed(2)} ${(C - r * Math.cos(a)).toFixed(2)}`
  const large = a1 - a0 > Math.PI ? 1 : 0
  return `M ${p(r1, a0)} A ${r1} ${r1} 0 ${large} 1 ${p(r1, a1)} L ${p(r0, a1)} A ${r0} ${r0} 0 ${large} 0 ${p(r0, a0)} Z`
}

interface Props {
  items: SubjectProgress[]
  selectedId?: string
  onSelect: (subjectId: string) => void
}

export function ProgressWheel({ items, selectedId, onSelect }: Props) {
  const [hover, setHover] = useState<number | null>(null)
  const done = items.reduce((n, i) => n + i.done, 0)
  const total = items.reduce((n, i) => n + i.total, 0)
  const pct = total ? Math.round((done / total) * 100) : 0
  const step = (2 * Math.PI) / items.length
  const hovered = hover !== null ? items[hover] : null

  return (
    <div className="wheel">
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} role="group" aria-label={`Overall progress ${pct}%`}>
        {items.map((it, i) => {
          const a0 = i * step + GAP / 2
          const a1 = (i + 1) * step - GAP / 2
          const fillR = R_IN + (R_OUT - R_IN) * it.ratio
          const selected = it.subject.id === selectedId
          return (
            <g
              key={it.subject.id}
              className={`wheel-slice ${selected ? 'is-selected' : ''} ${hover === i ? 'is-hover' : ''}`}
              onMouseEnter={() => setHover(i)}
              onMouseLeave={() => setHover(null)}
              onClick={() => onSelect(it.subject.id)}
              role="button"
              tabIndex={0}
              aria-label={`${it.subject.title}: ${it.done} of ${it.total} done`}
              onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && (e.preventDefault(), onSelect(it.subject.id))}
              onFocus={() => setHover(i)}
              onBlur={() => setHover(null)}
            >
              <path className="wheel-track" d={sector(a0, a1, R_IN, R_OUT)} />
              {it.ratio > 0 && <path className="wheel-fill" d={sector(a0, a1, R_IN, Math.max(fillR, R_IN + 3))} />}
            </g>
          )
        })}
      </svg>
      <div className="wheel-center" aria-hidden>
        {hovered ? (
          <>
            <strong>{Math.round(hovered.ratio * 100)}%</strong>
            <span>{hovered.subject.title}</span>
            <span className="muted">{hovered.done}/{hovered.total}</span>
          </>
        ) : (
          <>
            <strong>{pct}%</strong>
            <span>overall</span>
            <span className="muted">{done}/{total}</span>
          </>
        )}
      </div>
    </div>
  )
}

/** Tabular view of the same data (also the accessible alternative). */
export function ProgressBreakdown({ items, selectedId, onSelect }: Props) {
  return (
    <ul className="breakdown">
      {items.map((it) => (
        <li key={it.subject.id}>
          <button
            className={`breakdown-row ${it.subject.id === selectedId ? 'is-selected' : ''}`}
            onClick={() => onSelect(it.subject.id)}
          >
            <span className="breakdown-name">{it.subject.title}</span>
            <span className="breakdown-bar" aria-hidden><span style={{ width: `${it.ratio * 100}%` }} /></span>
            <span className="breakdown-count">{it.done}/{it.total}</span>
          </button>
        </li>
      ))}
    </ul>
  )
}
