import logo from '@/branding/logo-paths.json'

/**
 * The LearnViaNotes mark: LVN in paper on a flat ink tile, underlined by one highlighter stroke. Drawn inline from
 * branding/logo-paths.json (the same shapes as the favicons and the mobile app). Decorative: the visible name next to
 * it carries the meaning. `idPrefix` is kept for callers; the mark has no gradients, so no ids are needed.
 */
export function Logo({ size = 32, className }: { size?: number; idPrefix?: string; className?: string }) {
  const c = logo.colors
  return (
    <svg width={size} height={size} viewBox="0 0 1024 1024" aria-hidden="true" focusable="false" className={className}>
      <rect width="1024" height="1024" rx={logo.tileRadius} fill={c.tile} />
      {logo.letters.map((d) => (
        <path key={d} d={d} fill={c.letter} />
      ))}
      <path d={logo.marker} fill={c.marker} />
    </svg>
  )
}
