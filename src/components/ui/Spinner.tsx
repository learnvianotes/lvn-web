/* ============================================================
   Spinner — C-NOTE UI Primitive
   Accessible loading spinner.
   ============================================================ */

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  label?: string
  className?: string
}

export function Spinner({ size = 'md', label = 'Loading…', className = '' }: SpinnerProps) {
  return (
    <span
      className={`spinner spinner--${size} ${className}`}
      role="status"
      aria-label={label}
    >
      <span className="sr-only">{label}</span>
    </span>
  )
}
