import { Link } from 'react-router-dom'
import { ChartPie, MessageCircleQuestion, Moon, PanelLeft, Sun } from 'lucide-react'
import { useTheme } from '@/shared/lib/theme'
import { APP_NAME } from '@/config'
import { useLayout } from '@/app/shell/LayoutState'
import { toggleHelp, useHelpOpen } from '@/features/help/HelpCenter'
import { Search } from '@/features/search/Search'
import { FocusTimer } from '@/features/focus/FocusTimer'
import { AccountMenu } from '@/features/auth/AccountMenu'
import { useUser } from '@/features/auth/auth'

export function Header() {
  const { theme, toggle } = useTheme()
  const { hasSidebar, sidebarOpen, insightsOpen, toggleSidebar, toggleInsights } = useLayout()
  const helpOpen = useHelpOpen()
  const user = useUser()

  return (
    <header className={`header ${hasSidebar ? 'has-sidebar' : ''}`}>
      <div className="header-start">
        {hasSidebar && (
          <button
            className={`icon-btn ${sidebarOpen ? 'is-on' : ''}`}
            onClick={toggleSidebar}
            aria-label={sidebarOpen ? 'Hide contents' : 'Show contents'}
            aria-expanded={sidebarOpen}
            title="Contents"
          >
            <PanelLeft size={18} />
          </button>
        )}
        <Link to="/" className="brand" aria-label={`${APP_NAME} home`}>
          <img src="/icons/icon-48.png" alt="" width={28} height={28} />
          <span>{APP_NAME}</span>
        </Link>
      </div>
      <div className="header-actions">
        <Search />
        {user && <FocusTimer />}
        <button
          className={`icon-btn ${insightsOpen ? 'is-on' : ''}`}
          onClick={toggleInsights}
          aria-label={insightsOpen ? 'Hide progress' : 'Show progress and streak'}
          aria-expanded={insightsOpen}
          title="Progress & streak"
        >
          <ChartPie size={18} />
        </button>
        <button
          className={`icon-btn ${helpOpen ? 'is-on' : ''}`}
          onClick={toggleHelp}
          aria-label={helpOpen ? 'Close help center' : 'Help center'}
          aria-expanded={helpOpen}
          title="Help center"
        >
          <MessageCircleQuestion size={18} />
        </button>
        <button
          className="icon-btn"
          onClick={toggle}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
        <AccountMenu />
      </div>
    </header>
  )
}
