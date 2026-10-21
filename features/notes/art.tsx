/** Small inline illustrations in the brand's gradient (ui-reference: warm illustrations). Decorative only. */

export function NotebookArt({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 200 150" className={className} aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="nb-page" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#EFF6FF" />
          <stop offset="1" stopColor="#DBEAFE" />
        </linearGradient>
        <linearGradient id="nb-cover" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#3B82F6" />
          <stop offset="1" stopColor="#06B6D4" />
        </linearGradient>
      </defs>
      <ellipse cx="100" cy="136" rx="70" ry="8" fill="#3B82F6" opacity="0.12" />
      <path d="M30 40 Q65 28 100 40 L100 128 Q65 116 30 128 Z" fill="url(#nb-cover)" />
      <path d="M36 42 Q66 32 100 44 L100 124 Q66 112 36 122 Z" fill="url(#nb-page)" />
      <path d="M170 40 Q135 28 100 40 L100 128 Q135 116 170 128 Z" fill="url(#nb-cover)" />
      <path d="M164 42 Q134 32 100 44 L100 124 Q134 112 164 122 Z" fill="#FFFFFF" />
      {[58, 72, 86, 100].map((y) => (
        <path key={y} d={`M46 ${y} Q68 ${y - 6} 92 ${y + 2}`} stroke="#93C5FD" strokeWidth="3" strokeLinecap="round" fill="none" />
      ))}
      <path d="M114 78 l10 10 l22 -24" stroke="#10B981" strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" fill="none" />
      <path d="M150 22 l3 8 l8 3 l-8 3 l-3 8 l-3 -8 l-8 -3 l8 -3 Z" fill="#F59E0B" />
      <path d="M40 18 l2 5 l5 2 l-5 2 l-2 5 l-2 -5 l-5 -2 l5 -2 Z" fill="#93C5FD" />
    </svg>
  )
}
