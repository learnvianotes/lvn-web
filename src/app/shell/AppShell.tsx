/* ============================================================
   AppShell — header + three columns that scroll independently:
     [ contents sidebar | page | progress panel ]
   The sidebar only exists on study pages (they portal into it,
   see StudyLayout). The progress panel is available everywhere.
   ============================================================ */

import { Outlet, useLocation, useMatch, useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'
import { useSubject } from '@/features/catalog/hooks'
import { Header } from '@/app/shell/Header'
import { InsightsPanel } from '@/features/progress/insights/InsightsPanel'
import { HelpCenter } from '@/features/help/HelpCenter'
import { useLayout } from '@/app/shell/LayoutState'
import { ListenBar } from '@/features/voice/ListenBar'
import { trackPageView } from '@/services/analytics'
import { useEffect, useRef } from 'react'

export function AppShell() {
  const { hasSidebar, sidebarOpen, insightsOpen, toggleInsights, closeDrawers, setSidebarNode, highlighted, setHighlighted } = useLayout()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useMatch('/:subjectId/*')
  const currentSubject = useSubject(match?.params.subjectId)
  const onHome = location.pathname === '/'
  const isAuthPage = ['/login', '/signup', '/forgot-password'].includes(location.pathname)

  // Analytics logs the first page view itself; log client-side navigations after that.
  const firstView = useRef(true)
  useEffect(() => {
    if (firstView.current) { firstView.current = false; return }
    trackPageView(location.pathname)
  }, [location.pathname])

  const selectSubject = (id: string) => {
    if (onHome) setHighlighted(id)
    else navigate(`/${id}`)
  }

  const classes = ['shell', hasSidebar && sidebarOpen && 'sidebar-open', insightsOpen && !isAuthPage && 'insights-open'].filter(Boolean).join(' ')

  return (
    <>
      <Header />
      <div className={classes}>
        <aside className="ws-panel ws-sidebar" aria-label="Contents" inert={!(hasSidebar && sidebarOpen)}>
          <div className="ws-panel-inner" ref={setSidebarNode} />
        </aside>

        <main className="ws-main">
          <Outlet />
        </main>

        <aside className="ws-panel ws-insights" aria-label="Progress and streak" inert={!insightsOpen}>
          <div className="ws-panel-inner">
            <div className="ws-insights-head">
              <span>Your progress</span>
              <button className="icon-btn sm" onClick={toggleInsights} aria-label="Close progress"><X size={16} /></button>
            </div>
            <InsightsPanel selectedId={onHome ? highlighted : currentSubject?.id} onSelectSubject={selectSubject} />
          </div>
        </aside>

        <div className="ws-scrim" onClick={closeDrawers} aria-hidden />
      </div>
      <HelpCenter />
      <ListenBar />
    </>
  )
}
