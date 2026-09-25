/* ============================================================
   GlobalHeader — App-style header
   Left:  app icon + "C-NOTE" + subtitle
   Right: subjects count + theme toggle
   No sticky nav bar. Minimal. Matches the reference design.
   ============================================================ */

import { Menu } from 'lucide-react'
import { Link } from 'react-router-dom'
import { useTheme } from '@/hooks/useTheme'
import { ThemeToggle } from '@/features/theme/ThemeToggle'
import { SUBJECTS } from '@/data/subjects'

interface GlobalHeaderProps {
  onMenuOpen?: () => void
}

export function GlobalHeader({ onMenuOpen }: GlobalHeaderProps) {
  const { theme } = useTheme()

  return (
    <header className="app-header" data-theme-active={theme}>
      <div className="app-header__inner">
        {/* Identity */}
        <Link to="/" className="app-header__identity" aria-label="C-NOTE home">
          <img
            src="/app-icon.png"
            alt=""
            aria-hidden="true"
            className="app-header__icon"
          />
          <div className="app-header__text">
            <span className="app-header__name">C-NOTE</span>
            <span className="app-header__subtitle">Personal Technical Knowledge Base</span>
          </div>
        </Link>

        {/* Actions */}
        <div className="app-header__actions">
          <span className="app-header__count" aria-label={`${SUBJECTS.length} subjects`}>
            <span className="pulse-dot" aria-hidden="true" />
            {SUBJECTS.length} Subjects
          </span>
          <ThemeToggle />
          {onMenuOpen && (
            <button
              className="icon-btn icon-btn--ghost icon-btn--sm header-mobile-menu-btn"
              aria-label="Open navigation menu"
              onClick={onMenuOpen}
            >
              <Menu size={16} />
            </button>
          )}
        </div>
      </div>
    </header>
  )
}
