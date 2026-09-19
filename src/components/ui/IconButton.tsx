/* ============================================================
   IconButton — C-NOTE UI Primitive
   A square button containing only an icon.
   ============================================================ */

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'

export type IconButtonSize = 'sm' | 'md' | 'lg'
export type IconButtonVariant = 'ghost' | 'secondary'

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  /** Required for accessibility */
  'aria-label': string
  size?: IconButtonSize
  variant?: IconButtonVariant
  children: ReactNode
}

const sizeStyles: Record<IconButtonSize, string> = {
  sm: 'icon-btn--sm',
  md: 'icon-btn--md',
  lg: 'icon-btn--lg',
}

const variantStyles: Record<IconButtonVariant, string> = {
  ghost:     'icon-btn--ghost',
  secondary: 'icon-btn--secondary',
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      size = 'md',
      variant = 'ghost',
      className = '',
      children,
      ...props
    },
    ref,
  ) => {
    const classes = [
      'icon-btn',
      sizeStyles[size],
      variantStyles[variant],
      className,
    ]
      .filter(Boolean)
      .join(' ')

    return (
      <button ref={ref} className={classes} {...props}>
        {children}
      </button>
    )
  },
)

IconButton.displayName = 'IconButton'
