import logo from '@/branding/logo-paths.json'

/**
 * The LearnViaNotes mark on its indigo tile, drawn inline from branding/logo-paths.json (the same shapes as the
 * favicons and the mobile app). Decorative: the visible name next to it carries the meaning.
 * `idPrefix` keeps gradient ids unique if the logo appears more than once on a page.
 */
export function Logo({ size = 32, idPrefix = 'lvn-logo', className }: { size?: number; idPrefix?: string; className?: string }) {
  const c = logo.colors
  return (
    <svg width={size} height={size} viewBox="0 0 1024 1024" aria-hidden="true" focusable="false" className={className}>
      <defs>
        <linearGradient id={`${idPrefix}-bg`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={c.gradient[0]} />
          <stop offset="0.55" stopColor={c.gradient[1]} />
          <stop offset="1" stopColor={c.gradient[2]} />
        </linearGradient>
        <radialGradient id={`${idPrefix}-glow`} cx="0.22" cy="0.18" r="0.75">
          <stop offset="0" stopColor="#FFFFFF" stopOpacity={0.22} />
          <stop offset="1" stopColor="#FFFFFF" stopOpacity={0} />
        </radialGradient>
      </defs>
      <rect width="1024" height="1024" rx={logo.tileRadius} fill={`url(#${idPrefix}-bg)`} />
      <rect width="1024" height="1024" rx={logo.tileRadius} fill={`url(#${idPrefix}-glow)`} />
      <path d={logo.leftPage} fill={c.page} />
      <path d={logo.rightPage} fill={c.pageShade} />
      {logo.lines.map((d) => (
        <path key={d} d={d} fill="none" stroke={c.line} strokeWidth={18} strokeLinecap="round" />
      ))}
      <path d={logo.check} fill="none" stroke={c.check} strokeWidth={28} strokeLinecap="round" strokeLinejoin="round" />
      <path d={logo.spark} fill={c.spark} />
    </svg>
  )
}
