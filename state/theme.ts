'use client'

import { create } from 'zustand'
import { THEME_KEY } from '@/lib/theme'

export type Theme = 'light' | 'dark'

interface ThemeState {
  theme: Theme
  setTheme: (theme: Theme) => void
}

function current(): Theme {
  if (typeof document === 'undefined') return 'light'
  return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light'
}

export const useTheme = create<ThemeState>((set) => ({
  theme: current(),
  setTheme: (theme) => {
    document.documentElement.dataset.theme = theme
    try { localStorage.setItem(THEME_KEY, JSON.stringify(theme)) } catch { /* private mode: theme lasts for this tab */ }
    set({ theme })
  },
}))
