/* ============================================================
   Button — C-NOTE UI Primitive
   ============================================================ */

import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'

export type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
export type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  children: ReactNode
  /** Show a loading state — disables interaction */
  isLoading?: boolean
  /** Stretch to fill container width */
  fullWidth?: boolean
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:   'btn--primary',
  secondary: 'btn--secondary',
  ghost:     'btn--ghost',
  danger:    'btn--danger',
}

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'btn--sm',
  md: 'btn--md',
  lg: 'btn--lg',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'secondary',
      size = 'md',
      isLoading = false,
      fullWidth = false,
      disabled,
      className = '',
      children,
      ...props
    },
    ref,
  ) => {
    const classes = [
      'btn',
      variantStyles[variant],
      sizeStyles[size],
      fullWidth ? 'btn--full' : '',
      className,
    ]
      .filter(Boolean)
      .join(' ')

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || isLoading}
        aria-busy={isLoading}
        {...props}
      >
        {isLoading ? (
          <span className="btn__spinner" aria-hidden="true" />
        ) : null}
        <span className={isLoading ? 'btn__label--loading' : ''}>{children}</span>
      </button>
    )
  },
)

Button.displayName = 'Button'
