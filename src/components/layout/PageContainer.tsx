/* ============================================================
   PageContainer — consistent content width + padding
   ============================================================ */

import type { ReactNode } from 'react'

interface PageContainerProps {
  children: ReactNode
  narrow?: boolean
  className?: string
}

export function PageContainer({ children, narrow = false, className = '' }: PageContainerProps) {
  return (
    <main
      className={`page-container ${narrow ? 'page-container--narrow' : ''} ${className}`}
      id="main-content"
    >
      {children}
    </main>
  )
}
