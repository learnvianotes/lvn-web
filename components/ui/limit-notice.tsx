import type { ReactNode } from 'react'

/** A plan limit or a similar refusal, in the API's words, set apart from a generic failure. */
export function LimitNotice({ children }: { children: ReactNode }) {
  return (
    <p role="alert" className="rounded-xl border border-warn/40 bg-warn/10 px-4 py-3 text-sm text-warn">
      {children}
    </p>
  )
}
