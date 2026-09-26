/* ============================================================
   StudyLayout — used by study pages: puts their contents list in
   the shell's left sidebar and renders the page body.
   ============================================================ */

import { useEffect, useRef, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { X } from 'lucide-react'
import { useLayout } from './layout/LayoutState'

interface Props {
  sidebarTitle: ReactNode
  sidebar: ReactNode
  children: ReactNode
}

export function StudyLayout({ sidebarTitle, sidebar, children }: Props) {
  const { setHasSidebar, sidebarNode, toggleSidebar } = useLayout()
  const body = useRef<HTMLElement>(null)

  useEffect(() => {
    setHasSidebar(true)
    return () => setHasSidebar(false)
  }, [setHasSidebar])

  // Keep the current item visible in the sidebar.
  useEffect(() => {
    body.current?.querySelector('.nav-item.active')?.scrollIntoView({ block: 'nearest' })
  })

  return (
    <>
      {sidebarNode && createPortal(
        <>
          <div className="ws-sidebar-head">
            <div className="ws-sidebar-title">{sidebarTitle}</div>
            <button className="icon-btn sm" onClick={toggleSidebar} aria-label="Close contents"><X size={16} /></button>
          </div>
          <nav className="ws-sidebar-body" ref={body}>{sidebar}</nav>
        </>,
        sidebarNode,
      )}
      <div className="ws-content">{children}</div>
    </>
  )
}
