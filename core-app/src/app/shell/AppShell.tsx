/* ============================================================
   AppShell — header + the page, with the contents sidebar on
   study pages (they portal into it, see StudyLayout). The
   signed-in progress panel of the old site is not part of the
   guest-only /core pages.
   ============================================================ */

import { Outlet } from 'react-router-dom'
import { Header } from '@core/app/shell/Header'
import { HelpCenter } from '@core/features/help/HelpCenter'
import { useLayout } from '@core/app/shell/LayoutState'

export function AppShell() {
  const { hasSidebar, sidebarOpen, closeDrawers, setSidebarNode } = useLayout()
  const classes = ['shell', hasSidebar && sidebarOpen && 'sidebar-open'].filter(Boolean).join(' ')

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

        <div className="ws-scrim" onClick={closeDrawers} aria-hidden />
      </div>
      <HelpCenter />
    </>
  )
}
