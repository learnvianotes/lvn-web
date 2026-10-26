import { cloneElement, isValidElement, useId, type ReactElement, type ReactNode } from 'react'

/**
 * A labelled form control with its hint and error, wired for screen readers: the error is announced and linked with
 * aria-describedby, and the control gets aria-invalid.
 */
export function Field({ label, hint, error, children }: { label: string; hint?: ReactNode; error?: string; children: ReactElement<Record<string, unknown>> }) {
  const id = useId()
  const hintId = `${id}-hint`
  const errorId = `${id}-error`
  const describedBy = [hint ? hintId : null, error ? errorId : null].filter(Boolean).join(' ') || undefined
  const control = isValidElement(children) ? cloneElement(children, { id, 'aria-invalid': error ? true : undefined, 'aria-describedby': describedBy }) : children
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium">{label}</label>
      {control}
      {hint ? <p id={hintId} className="text-xs text-muted">{hint}</p> : null}
      {error ? <p id={errorId} role="alert" className="text-xs font-medium text-bad">{error}</p> : null}
    </div>
  )
}
