/* SiteFooter — landing page only: About and (when offered) Install app. */

import { Link } from 'react-router-dom'
import { Download } from 'lucide-react'
import { APP_NAME } from '@/config'
import { promptInstall, useCanInstall } from '@/lib/install'

export function SiteFooter() {
  const canInstall = useCanInstall()
  return (
    <footer className="site-footer">
      <span>© {new Date().getFullYear()} {APP_NAME}</span>
      <Link to="/about">About</Link>
      {canInstall && (
        <button className="footer-install" onClick={() => void promptInstall()}>
          <Download size={14} aria-hidden /> Install app
        </button>
      )}
    </footer>
  )
}
