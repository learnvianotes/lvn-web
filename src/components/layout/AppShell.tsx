/* ============================================================
   AppShell — header + three columns that scroll independently:
     [ contents sidebar | page | progress panel ]
   The sidebar only exists on study pages (they portal into it,
   see StudyLayout). The progress panel is available everywhere.
   ============================================================ */

import { Outlet, useLocation, useMatch, useNavigate } from 'react-router-dom'
import { X } from 'lucide-react'
import { useSubject } from '@/content/hooks'
import { Header } from '../Header'
import { InsightsPanel } from '../insights/InsightsPanel'
import { HelpCenter } from '../help/HelpCenter'
import { useLayout } from './LayoutState'

export function AppShell() {
  const { hasSidebar, sidebarOpen, insightsOpen, toggleInsights, closeDrawers, setSidebarNode, highlighted, setHighlighted } = useLayout()
  const navigate = useNavigate()
  const location = useLocation()
  const match = useMatch('/:subjectId/*')
  const currentSubject = useSubject(match?.params.subjectId)
  const onHome = location.pathname === '/'

  const selectSubject = (id: string) => {
    if (onHome) setHighlighted(id)
    else navigate(`/${id}`)
  }

  const classes = ['shell', hasSidebar && sidebarOpen && 'sidebar-open', insightsOpen && 'insights-open'].filter(Boolean).join(' ')

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
    </>
  )
}
