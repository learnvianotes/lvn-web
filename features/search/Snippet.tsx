import { Fragment } from 'react'

/** The API's snippet with its matches (wrapped in U+E000 … U+E001) shown as marks. */
export function Snippet({ text, className }: { text: string; className?: string }) {
  const parts = text.split(/([^]*)/)
  return (
    <span className={className}>
      {parts.map((p, i) =>
        p.startsWith('') ? (
          <mark key={i} className="rounded-sm bg-accent-soft font-semibold text-fg">
            {p.slice(1, -1)}
          </mark>
        ) : (
          <Fragment key={i}>{p}</Fragment>
        ),
      )}
    </span>
  )
}
