/**
 * A small flat illustration for the notes home and its empty state: an open ruled notebook with one line marked by the
 * highlighter (ADR-0114). Theme colours only, so it follows light and dark. Decorative only.
 */
export function NotebookArt({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 200 150" className={className} aria-hidden="true" focusable="false">
      <path d="M24 30 Q62 20 100 30 L100 132 Q62 122 24 132 Z" fill="var(--surface)" stroke="var(--border)" strokeWidth="2" />
      <path d="M176 30 Q138 20 100 30 L100 132 Q138 122 176 132 Z" fill="var(--surface)" stroke="var(--border)" strokeWidth="2" />
      {[52, 68, 84, 100, 116].map((y) => (
        <g key={y}>
          <path d={`M34 ${y} Q62 ${y - 6} 92 ${y}`} stroke="var(--border)" strokeWidth="2" fill="none" />
          <path d={`M108 ${y} Q138 ${y - 6} 166 ${y}`} stroke="var(--border)" strokeWidth="2" fill="none" />
        </g>
      ))}
      <path d="M110 77 Q138 70 160 76 L160 86 Q138 80 110 87 Z" fill="var(--highlight)" />
      <path d="M38 50 Q58 45 78 48" stroke="var(--fg)" strokeWidth="3" strokeLinecap="round" fill="none" />
      <path d="M38 66 Q56 62 86 65" stroke="var(--muted)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
      <path d="M112 80 Q136 74 156 79" stroke="var(--fg)" strokeWidth="2.5" strokeLinecap="round" fill="none" />
    </svg>
  )
}
