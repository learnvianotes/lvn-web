/* ============================================================
   GlobalHeader — top navigation bar
   ============================================================ */

import { Link } from 'react-router-dom'
import { Search, Menu } from 'lucide-react'
import { ThemeToggle } from '@/features/theme/ThemeToggle'
import { IconButton } from '@/components/ui/IconButton'

interface GlobalHeaderProps {
  onMenuOpen?: () => void
}

export function GlobalHeader({ onMenuOpen }: GlobalHeaderProps) {
  return (
    <header className="global-header" role="banner">
      <div className="global-header__inner">
        {/* Identity */}
        <Link to="/" className="header-logo" aria-label="C-NOTE home">
          <span className="header-logo__mark" aria-hidden="true">C</span>
          <span className="header-logo__text">C-NOTE</span>
        </Link>

        <div className="header-spacer" />

        {/* Search trigger — visual placeholder for Phase 1 */}
        <button
          className="header-search-trigger"
          aria-label="Search (coming soon)"
          disabled
          title="Search will be available in a future phase"
        >
          <Search size={13} aria-hidden="true" />
          <span>Search…</span>
          <kbd className="header-search-trigger__kbd" aria-label="keyboard shortcut">⌘K</kbd>
        </button>

        {/* Right actions */}
        <div className="header-actions">
          <ThemeToggle />

          {/* Mobile menu trigger */}
          <IconButton
            aria-label="Open navigation menu"
            className="header-mobile-menu-btn"
            onClick={onMenuOpen}
            size="md"
            variant="ghost"
          >
            <Menu size={18} />
          </IconButton>
        </div>
      </div>
    </header>
  )
}
