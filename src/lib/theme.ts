/* ============================================================
   THEME — light / dark, stored locally.
   index.html applies the stored theme before first paint.
   ============================================================ */

import { useCallback, useSyncExternalStore } from 'react'
import { get, set } from './storage'

export type Theme = 'light' | 'dark'

const listeners = new Set<() => void>()

function current(): Theme {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
}

function apply(theme: Theme) {
  document.documentElement.setAttribute('data-theme', theme)
  // Browser / installed-app title bar follows the chosen theme.
  document.querySelectorAll('meta[name="theme-color"]').forEach((m) => m.remove())
  const meta = document.createElement('meta')
  meta.name = 'theme-color'
  meta.content = theme === 'dark' ? '#17171a' : '#ffffff'
  document.head.appendChild(meta)
}

export function initTheme() {
  const stored = get<Theme>('theme')
  apply(stored ?? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
}

export function useTheme() {
  const theme = useSyncExternalStore(
    (l) => { listeners.add(l); return () => listeners.delete(l) },
    current,
  )
  const toggle = useCallback(() => {
    const next: Theme = current() === 'dark' ? 'light' : 'dark'
    apply(next)
    set('theme', next)
    listeners.forEach((l) => l())
  }, [])
  return { theme, toggle }
}
