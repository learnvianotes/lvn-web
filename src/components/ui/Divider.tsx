/* ============================================================
   Divider — C-NOTE UI Primitive
   Horizontal or vertical visual separator.
   ============================================================ */

interface DividerProps {
  orientation?: 'horizontal' | 'vertical'
  subtle?: boolean
  className?: string
  label?: string
}

export function Divider({
  orientation = 'horizontal',
  subtle = false,
  label,
  className = '',
}: DividerProps) {
  if (orientation === 'vertical') {
    return (
      <div
        role="separator"
        aria-orientation="vertical"
        className={`divider divider--vertical ${subtle ? 'divider--subtle' : ''} ${className}`}
      />
    )
  }

  if (label) {
    return (
      <div className={`divider divider--labeled ${className}`} role="separator">
        <span className="divider__line" />
        <span className="divider__label">{label}</span>
        <span className="divider__line" />
      </div>
    )
  }

  return (
    <hr
      className={`divider ${subtle ? 'divider--subtle' : ''} ${className}`}
    />
  )
}
