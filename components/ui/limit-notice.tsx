import type { ReactNode } from 'react'

/** A plan limit or a similar refusal, in the API's words, set apart from a generic failure. */
export function LimitNotice({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="rounded-xl border border-amber-600/40 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:border-amber-500/40 dark:bg-amber-950/40 dark:text-amber-100">
      {children}
    </p>
  )
}
