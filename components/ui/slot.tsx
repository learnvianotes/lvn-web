import { cloneElement, isValidElement, type HTMLAttributes, type ReactElement, type ReactNode } from 'react'
import { cn } from '@/lib/cn'

/** Minimal Radix-style Slot: merges its props and className into its only child. */
export function Slot({ children, className, ...props }: HTMLAttributes<HTMLElement> & { children?: ReactNode }) {
  if (!isValidElement(children)) return null
  const child = children as ReactElement<HTMLAttributes<HTMLElement>>
  return cloneElement(child, { ...props, ...child.props, className: cn(className, child.props.className) })
}
