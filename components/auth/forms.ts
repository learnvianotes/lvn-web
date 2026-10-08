import type { FieldValues, Path, UseFormSetError } from 'react-hook-form'

export interface ProblemLike {
  field: string[] | null
  message: string
  code: string
}

/**
 * Puts the API's userErrors on their form fields (`["input", "email"]` → `email`); anything without a field is
 * returned for an alert above the form.
 */
export function applyProblems<T extends FieldValues>(problems: ProblemLike[], setError: UseFormSetError<T>, fields: readonly Path<T>[]): string | null {
  let general: string | null = null
  for (const p of problems) {
    const name = p.field?.at(-1) as Path<T> | undefined
    if (name && fields.includes(name)) setError(name, { type: 'server', message: p.message })
    else general ??= p.message
  }
  return general
}
