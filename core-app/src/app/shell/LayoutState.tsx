/* ============================================================
   LayoutState — shared UI state of the app shell:
     • left sidebar (only on study pages; content is portaled in)
     • right progress panel (every page)
     • subject highlighted from the progress wheel (home page)
   Desktop: panels sit beside the content and push it.
   Mobile:  panels slide in as drawers over a dimmed backdrop.
   ============================================================ */

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { get, set } from '@core/services/storage'

/** Below this width panels are drawers (see layout.css). */
export const DRAWER_QUERY = '(max-width: 1023px)'
const isDrawerMode = () => window.matchMedia(DRAWER_QUERY).matches

interface LayoutState {
  /** a study page has provided sidebar content */
  hasSidebar: boolean
  setHasSidebar: (on: boolean) => void
  /** DOM node study pages portal their sidebar into */
  sidebarNode: HTMLElement | null
  setSidebarNode: (el: HTMLElement | null) => void
  sidebarOpen: boolean
  insightsOpen: boolean
  toggleSidebar: () => void
  toggleInsights: () => void
  closeDrawers: () => void
  highlighted: string | undefined
  setHighlighted: (subjectId: string | undefined) => void
}

const Ctx = createContext<LayoutState | null>(null)

export function LayoutProvider({ children }: { children: ReactNode }) {
  const location = useLocation()
  const [hasSidebar, setHasSidebar] = useState(false)
  const [sidebarNode, setSidebarNode] = useState<HTMLElement | null>(null)
  const [highlighted, setHighlighted] = useState<string>()
  const [sidebarOpen, setSidebarOpen] = useState(() => !isDrawerMode() && get<boolean>('sidebar-open') !== false)
  // The progress panel was for signed-in learners; it stays closed on the guest-only /core pages.
  const [insightsOpen, setInsightsOpen] = useState(false)

  const toggleSidebar = useCallback(() => {
    setSidebarOpen((open) => {
      if (!isDrawerMode()) set('sidebar-open', !open)
      else if (!open) setInsightsOpen(false) // one drawer at a time on mobile
      return !open
    })
  }, [])

  const toggleInsights = useCallback(() => {
    setInsightsOpen((open) => {
      if (!isDrawerMode()) set('insights-open', !open)
      else if (!open) setSidebarOpen(false)
      return !open
    })
  }, [])

  const closeDrawers = useCallback(() => {
    if (!isDrawerMode()) return
    setSidebarOpen(false)
    setInsightsOpen(false)
  }, [])

  // Drawers close after navigating on mobile.
  useEffect(() => { closeDrawers() }, [location.pathname, location.hash, closeDrawers])

  // Switching between desktop and mobile widths: restore sensible defaults.
  useEffect(() => {
    const mq = window.matchMedia(DRAWER_QUERY)
    const onChange = () => {
      setSidebarOpen(!mq.matches && get<boolean>('sidebar-open') !== false)
      setInsightsOpen(false)
    }
    mq.addEventListener('change', onChange)
    return () => mq.removeEventListener('change', onChange)
  }, [])

  // Mobile: lock page scroll behind an open drawer; Escape closes it.
  const drawerOpen = ((hasSidebar && sidebarOpen) || insightsOpen) && isDrawerMode()
  useEffect(() => {
    if (!drawerOpen) return
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && closeDrawers()
    document.body.classList.add('scroll-locked')
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.classList.remove('scroll-locked')
      window.removeEventListener('keydown', onKey)
    }
  }, [drawerOpen, closeDrawers])

  const value = useMemo(
    () => ({
      hasSidebar, setHasSidebar, sidebarNode, setSidebarNode, sidebarOpen, insightsOpen,
      toggleSidebar, toggleInsights, closeDrawers, highlighted, setHighlighted,
    }),
    [hasSidebar, sidebarNode, sidebarOpen, insightsOpen, toggleSidebar, toggleInsights, closeDrawers, highlighted],
  )
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useLayout() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useLayout must be used inside <LayoutProvider>')
  return ctx
}
