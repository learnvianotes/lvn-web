/* ============================================================
   AppShell — root layout wrapper
   Composes GlobalHeader + MobileNavigation + main content.
   ============================================================ */

import { useState, type ReactNode } from 'react'
import { GlobalHeader } from './GlobalHeader'
import { MobileNavigation } from '@/components/navigation/MobileNavigation'

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)

  return (
    <div className="app-shell">
      {/* Skip to content link for keyboard/screen reader users */}
      <a
        href="#main-content"
        className="sr-only"
        style={{ position: 'absolute' }}
        onFocus={(e) => e.currentTarget.classList.remove('sr-only')}
        onBlur={(e) => e.currentTarget.classList.add('sr-only')}
      >
        Skip to main content
      </a>

      <GlobalHeader onMenuOpen={() => setMobileNavOpen(true)} />

      <MobileNavigation
        isOpen={mobileNavOpen}
        onClose={() => setMobileNavOpen(false)}
      />

      <div className="app-main">
        {children}
      </div>
    </div>
  )
}
