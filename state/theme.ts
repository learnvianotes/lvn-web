'use client'

import { create } from 'zustand'
import {
  ACCENT_KEY,
  THEME_KEY,
  applyAppearance,
  prefersDark,
  readAccent,
  readMode,
  type AccentId,
  type ResolvedTheme,
  type ThemeMode,
} from '@/lib/theme'

interface AppearanceState {
  mode: ThemeMode
  accent: AccentId
  resolved: ResolvedTheme
  setMode: (mode: ThemeMode) => void
  setAccent: (accent: AccentId) => void
  /** Read this device's storage and paint. Used after hydration and when the OS scheme changes. */
  sync: () => void
}

function persist(key: string, value: string) {
  try {
    localStorage.setItem(key, JSON.stringify(value))
  } catch {
    /* private mode: the choice lasts for this tab */
  }
}

export const useAppearance = create<AppearanceState>((set, get) => ({
  // Server and the first client render agree. ThemeSync reads storage after mount.
  mode: 'system',
  accent: 'navy',
  resolved: 'light',
  setMode: (mode) => {
    persist(THEME_KEY, mode)
    const resolved = applyAppearance(mode, get().accent, prefersDark())
    set({ mode, resolved })
  },
  setAccent: (accent) => {
    persist(ACCENT_KEY, accent)
    applyAppearance(get().mode, accent, prefersDark())
    set({ accent })
  },
  sync: () => {
    let mode: ThemeMode = 'system'
    let accent: AccentId = 'navy'
    try {
      mode = readMode(localStorage.getItem(THEME_KEY))
      accent = readAccent(localStorage.getItem(ACCENT_KEY))
    } catch {
      /* storage blocked */
    }
    const resolved = applyAppearance(mode, accent, prefersDark())
    set({ mode, accent, resolved })
  },
}))
