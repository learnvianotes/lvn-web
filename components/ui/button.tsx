import { Slot } from './slot'
import { cn } from '@/lib/cn'
import type { ButtonHTMLAttributes } from 'react'

const variants = {
  primary: 'bg-accent text-accent-fg hover:opacity-90',
  secondary: 'border border-border bg-surface text-fg hover:bg-surface-2',
  ghost: 'text-muted hover:bg-surface-2 hover:text-fg',
}

const sizes = { md: 'h-11 px-5 text-sm', sm: 'h-9 px-3 text-sm', icon: 'size-9' }

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: keyof typeof variants
  size?: keyof typeof sizes
  /** Render the single child (e.g. a Link) with button styles instead of a <button>. */
  asChild?: boolean
}

export function Button({ variant = 'primary', size = 'md', asChild, className, ...props }: ButtonProps) {
  const Comp = asChild ? Slot : 'button'
  return (
    <Comp
      className={cn(
        'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-xl font-medium transition-colors disabled:pointer-events-none disabled:opacity-50',
        variants[variant],
        sizes[size],
        className,
      )}
      {...props}
    />
  )
}
