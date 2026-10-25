import { Link } from 'react-router-dom'
import { MessageCircleQuestionMark, Moon, PanelLeft, Sun } from 'lucide-react'
import { useTheme } from '@core/shared/lib/theme'
import { APP_NAME } from '@core/config'
import { useLayout } from '@core/app/shell/LayoutState'
import { toggleHelp, useHelpOpen } from '@core/features/help/HelpCenter'
import { Search } from '@core/features/search/Search'

export function Header() {
  const { theme, toggle } = useTheme()
  const { hasSidebar, sidebarOpen, toggleSidebar } = useLayout()
  const helpOpen = useHelpOpen()

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
        <button
          className={`icon-btn ${helpOpen ? 'is-on' : ''}`}
          onClick={toggleHelp}
          aria-label={helpOpen ? 'Close help center' : 'Help center'}
          aria-expanded={helpOpen}
          title="Help center"
        >
          <MessageCircleQuestionMark size={18} />
        </button>
        <button
          className="icon-btn"
          onClick={toggle}
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          title={theme === 'dark' ? 'Light mode' : 'Dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  )
}
