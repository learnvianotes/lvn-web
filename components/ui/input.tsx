import { forwardRef, type InputHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(function Input({ className, ...props }, ref) {
  return (
    <input
      ref={ref}
      className={cn(
        'h-11 w-full min-w-0 max-w-full rounded-xl border border-border bg-surface px-3 text-[15px] text-fg placeholder:text-muted',
        'focus-visible:border-accent focus-visible:outline-none',
        'aria-[invalid=true]:border-bad disabled:opacity-60',
        className,
      )}
      {...props}
    />
  )
})
