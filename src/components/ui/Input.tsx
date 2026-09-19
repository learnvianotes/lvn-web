/* ============================================================
   Input — C-NOTE UI Primitive
   ============================================================ */

import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  hint?: string
  error?: string
  /** Icon to render on the left side */
  leadingIcon?: ReactNode
  /** Icon or element to render on the right side */
  trailingIcon?: ReactNode
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      label,
      hint,
      error,
      leadingIcon,
      trailingIcon,
      id,
      className = '',
      ...props
    },
    ref,
  ) => {
    const inputId = id ?? (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined)
    const hintId = hint ? `${inputId}-hint` : undefined
    const errorId = error ? `${inputId}-error` : undefined
    const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined

    return (
      <div className="input-wrapper">
        {label ? (
          <label htmlFor={inputId} className="input-label">
            {label}
          </label>
        ) : null}

        <div className={`input-field-wrap ${leadingIcon ? 'input-field-wrap--leading' : ''} ${trailingIcon ? 'input-field-wrap--trailing' : ''}`}>
          {leadingIcon ? (
            <span className="input-icon input-icon--leading" aria-hidden="true">
              {leadingIcon}
            </span>
          ) : null}

          <input
            ref={ref}
            id={inputId}
            className={`input-field ${error ? 'input-field--error' : ''} ${className}`}
            aria-invalid={!!error}
            aria-describedby={describedBy}
            {...props}
          />

          {trailingIcon ? (
            <span className="input-icon input-icon--trailing" aria-hidden="true">
              {trailingIcon}
            </span>
          ) : null}
        </div>

        {hint && !error ? (
          <span id={hintId} className="input-hint">
            {hint}
          </span>
        ) : null}

        {error ? (
          <span id={errorId} className="input-error" role="alert">
            {error}
          </span>
        ) : null}
      </div>
    )
  },
)

Input.displayName = 'Input'
