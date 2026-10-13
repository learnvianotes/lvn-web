/**
 * The landing hero's picture (board A): a note being written, a stack of flashcards, a question answered and a
 * graduation cap, drawn in the brand's colours so it sits on the light lavender hero and on the night sky alike.
 */
export function HeroArt({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 480 400" role="img" aria-label="A note, flashcards and a question answered" className={className}>
      <defs>
        <linearGradient id="hero-card" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#FFFFFF" />
          <stop offset="1" stopColor="#EEF2FF" />
        </linearGradient>
        <linearGradient id="hero-accent" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#6366F1" />
          <stop offset="1" stopColor="#8B5CF6" />
        </linearGradient>
        <filter id="hero-shadow" x="-20%" y="-20%" width="140%" height="140%">
          <feDropShadow dx="0" dy="12" stdDeviation="14" floodColor="#312E81" floodOpacity="0.18" />
        </filter>
      </defs>
      <circle cx="380" cy="80" r="64" fill="#A5B4FC" opacity="0.35" />
      <circle cx="70" cy="320" r="48" fill="#F9A8D4" opacity="0.35" />
      {/* Flashcards, fanned behind the note */}
      <g filter="url(#hero-shadow)">
        <rect x="270" y="150" width="170" height="110" rx="18" fill="#FDE68A" transform="rotate(12 355 205)" />
        <rect x="262" y="160" width="170" height="110" rx="18" fill="#FBCFE8" transform="rotate(4 347 215)" />
        <rect x="255" y="172" width="170" height="110" rx="18" fill="url(#hero-card)" />
        <text x="358" y="216" textAnchor="middle" fontFamily="Inter, sans-serif" fontSize="15" fontWeight="700" fill="#312E81">
          What is a BST?
        </text>
        <rect x="306" y="232" width="104" height="9" rx="4.5" fill="#C7D2FE" />
        <rect x="320" y="250" width="76" height="9" rx="4.5" fill="#E0E7FF" />
      </g>
      {/* The note */}
      <g filter="url(#hero-shadow)">
        <rect x="40" y="70" width="240" height="260" rx="24" fill="url(#hero-card)" />
        <rect x="64" y="96" width="120" height="14" rx="7" fill="url(#hero-accent)" />
        <rect x="64" y="128" width="190" height="9" rx="4.5" fill="#C7D2FE" />
        <rect x="64" y="148" width="170" height="9" rx="4.5" fill="#E0E7FF" />
        <rect x="64" y="168" width="182" height="9" rx="4.5" fill="#E0E7FF" />
        {/* A small tree, as in the board's note */}
        <g stroke="#A5B4FC" strokeWidth="3">
          <line x1="160" y1="212" x2="122" y2="246" />
          <line x1="160" y1="212" x2="198" y2="246" />
          <line x1="122" y1="246" x2="102" y2="280" />
          <line x1="122" y1="246" x2="142" y2="280" />
        </g>
        <circle cx="160" cy="212" r="14" fill="#FDE68A" />
        <circle cx="122" cy="246" r="12" fill="#A7F3D0" />
        <circle cx="198" cy="246" r="12" fill="#BFDBFE" />
        <circle cx="102" cy="280" r="10" fill="#FBCFE8" />
        <circle cx="142" cy="280" r="10" fill="#DDD6FE" />
        {/* Learned */}
        <circle cx="252" cy="96" r="18" fill="#22C55E" />
        <path d="M243 96 l6 6 l12 -13" stroke="#FFFFFF" strokeWidth="4" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </g>
      {/* A question, answered */}
      <g filter="url(#hero-shadow)">
        <rect x="292" y="300" width="160" height="56" rx="18" fill="url(#hero-accent)" />
        <path d="M312 356 l-10 18 l26 -18 z" fill="#7C3AED" />
        <text x="372" y="334" textAnchor="middle" fontFamily="Inter, sans-serif" fontSize="14" fontWeight="600" fill="#FFFFFF">
          Explain simply ✨
        </text>
      </g>
      {/* Graduation cap */}
      <g transform="translate(320 36)">
        <path d="M0 26 L52 6 L104 26 L52 46 Z" fill="#312E81" />
        <path d="M24 36 v18 c0 8 56 8 56 0 v-18 l-28 10 z" fill="#4F46E5" />
        <line x1="100" y1="27" x2="100" y2="56" stroke="#F59E0B" strokeWidth="3" />
        <circle cx="100" cy="58" r="4" fill="#F59E0B" />
      </g>
      {/* Sparkles */}
      <path d="M440 220 l4 10 l10 4 l-10 4 l-4 10 l-4 -10 l-10 -4 l10 -4 z" fill="#FBBF24" />
      <path d="M30 120 l3 7 l7 3 l-7 3 l-3 7 l-3 -7 l-7 -3 l7 -3 z" fill="#818CF8" />
    </svg>
  )
}
