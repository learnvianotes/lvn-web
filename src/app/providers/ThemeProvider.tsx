/* ============================================================
   C-NOTE THEME PROVIDER
   Manages theme state, persistence, and data-theme attribute.
   ============================================================ */

import { useState, useCallback, useEffect, type ReactNode } from 'react'
import { ThemeContext } from '@/contexts/ThemeContext'
import { get, set, STORAGE_KEYS } from '@/lib/storage'
import type { Theme } from '@/types'

/** Read initial theme — system preference if no stored value */
function getInitialTheme(): Theme {
  const stored = get<Theme>(STORAGE_KEYS.THEME)
  if (stored === 'dark' || stored === 'light') return stored
  return window.matchMedia('(prefers-color-scheme: light)').matches
    ? 'light'
    : 'dark'
}

interface ThemeProviderProps {
  children: ReactNode
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme)

  /* Apply data-theme attribute whenever theme changes */
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    set(STORAGE_KEYS.THEME, theme)
  }, [theme])

  const setTheme = useCallback((next: Theme) => {
    setThemeState(next)
  }, [])

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'))
  }, [])

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}
