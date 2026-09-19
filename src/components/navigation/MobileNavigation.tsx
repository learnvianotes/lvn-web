/* ============================================================
   MobileNavigation — drawer-based navigation for mobile
   ============================================================ */

import { useEffect, useCallback } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import { X, BookOpen, FlaskConical } from 'lucide-react'
import { IconButton } from '@/components/ui/IconButton'

interface MobileNavigationProps {
  isOpen: boolean
  onClose: () => void
}

const NAV_ITEMS = [
  { to: '/',        label: 'Home',        icon: BookOpen },
  { to: '/subjects', label: 'All Subjects', icon: BookOpen },
] as const

export function MobileNavigation({ isOpen, onClose }: MobileNavigationProps) {
  const location = useLocation()

  /* Close on route change */
  useEffect(() => {
    onClose()
  }, [location.pathname, onClose])

  /* Close on Escape key */
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    },
    [onClose],
  )

  useEffect(() => {
    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown)
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.body.style.overflow = ''
    }
  }, [isOpen, handleKeyDown])

  if (!isOpen) return null

  return (
    <>
      {/* Overlay */}
      <div
        className="mobile-nav-overlay"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Drawer */}
      <nav
        className="mobile-nav-drawer"
        aria-label="Mobile navigation"
        role="dialog"
        aria-modal="true"
      >
        <div className="mobile-nav-header">
          <span className="header-logo__text">C-NOTE</span>
          <IconButton aria-label="Close navigation" onClick={onClose} size="md" variant="ghost">
            <X size={18} />
          </IconButton>
        </div>

        <div className="mobile-nav-content">
          <p className="mobile-nav-section-label">Navigation</p>

          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `mobile-nav-item ${isActive ? 'mobile-nav-item--active' : ''}`
              }
            >
              <Icon size={16} aria-hidden="true" />
              {label}
            </NavLink>
          ))}

          {/* Dev-only design system link */}
          <div style={{ marginTop: 'var(--space-6)' }}>
            <p className="mobile-nav-section-label">Developer</p>
            <NavLink
              to="/design-system"
              className={({ isActive }) =>
                `mobile-nav-item ${isActive ? 'mobile-nav-item--active' : ''}`
              }
            >
              <FlaskConical size={16} aria-hidden="true" />
              Design Lab
            </NavLink>
          </div>
        </div>
      </nav>
    </>
  )
}
