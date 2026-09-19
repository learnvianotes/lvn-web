/* ============================================================
   ThemeToggle — switches between dark and light theme
   ============================================================ */

import { Moon, Sun } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'
import { IconButton } from '@/components/ui/IconButton'
import { Tooltip } from '@/components/ui/Tooltip'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <Tooltip content={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}>
      <IconButton
        aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
        onClick={toggleTheme}
        size="md"
        variant="ghost"
      >
        {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
      </IconButton>
    </Tooltip>
  )
}
