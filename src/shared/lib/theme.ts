/* ============================================================
   THEME — light / dark / system, stored on this device.
   index.html applies the stored theme before first paint.
   ============================================================ */

import { useCallback, useSyncExternalStore } from 'react'
import { get, remove, set } from '@/services/storage'

export type Theme = 'light' | 'dark'
export type ThemeMode = Theme | 'system'

const listeners = new Set<() => void>()
const notify = () => listeners.forEach((l) => l())
const subscribe = (l: () => void) => { listeners.add(l); return () => { listeners.delete(l) } }
const darkQuery = () => window.matchMedia('(prefers-color-scheme: dark)')

function current(): Theme {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
}

function storedMode(): ThemeMode {
  const t = get<Theme>('theme')
  return t === 'light' || t === 'dark' ? t : 'system'
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

const resolve = (mode: ThemeMode): Theme => (mode === 'system' ? (darkQuery().matches ? 'dark' : 'light') : mode)

export function initTheme() {
  apply(resolve(storedMode()))
  // "System": follow the OS switching between light and dark.
  darkQuery().addEventListener('change', () => {
    if (storedMode() === 'system') { apply(resolve('system')); notify() }
  })
}

export function setThemeMode(mode: ThemeMode) {
  if (mode === 'system') remove('theme')
  else set('theme', mode)
  apply(resolve(mode))
  notify()
}

export function useThemeMode(): ThemeMode {
  return useSyncExternalStore(subscribe, storedMode)
}

export function useTheme() {
  const theme = useSyncExternalStore(subscribe, current)
  const toggle = useCallback(() => setThemeMode(current() === 'dark' ? 'light' : 'dark'), [])
  return { theme, toggle }
}
