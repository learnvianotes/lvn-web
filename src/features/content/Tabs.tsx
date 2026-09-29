/* Tab widget: a tab bar (UI only → data-ui) over the content's tab panels. */

import { useState, type CSSProperties, type ReactNode } from 'react'

interface Panel {
  label: string
  id?: string
  style?: CSSProperties
  content: ReactNode
}

export function Tabs({ panels }: { panels: Panel[] }) {
  const [active, setActive] = useState(0)
  return (
    <div className="tabs">
      <div className="tab-bar" role="tablist" data-ui>
        {panels.map((p, i) => (
          <button key={i} type="button" role="tab" aria-selected={i === active} onClick={() => setActive(i)}>
            {p.label || `Tab ${i + 1}`}
          </button>
        ))}
      </div>
      {panels.map((p, i) => (
        <div key={i} id={p.id} className="tab-panel" data-label={p.label} style={p.style} hidden={i !== active}>
          {p.content}
        </div>
      ))}
    </div>
  )
}
