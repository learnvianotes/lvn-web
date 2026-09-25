import { useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { GlobalHeader } from './GlobalHeader'
import { MobileNavigation } from '@/components/navigation/MobileNavigation'

interface AppShellProps {
  children: ReactNode
}

export function AppShell({ children }: AppShellProps) {
  const [mobileNavOpen, setMobileNavOpen] = useState(false)
  const location = useLocation()

  // In learning workspace (/subjects/:id or /subjects/:id/topics/:topicId),
  // hide the dashboard header so the workspace has a single unified toolbar.
  const isLearningWorkspace =
    location.pathname.startsWith('/subjects/') && location.pathname !== '/subjects'

  return (
    <div className={`app-shell ${isLearningWorkspace ? 'app-shell--workspace' : ''}`}>
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

      {!isLearningWorkspace && (
        <GlobalHeader onMenuOpen={() => setMobileNavOpen(true)} />
      )}

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
