/* ============================================================
   C-NOTE THEME CONTEXT
   Single source of truth for theme state.
   Components never read localStorage directly for theme.
   ============================================================ */

import { createContext } from 'react'
import type { ThemeContextValue } from '@/types'

export const ThemeContext = createContext<ThemeContextValue | null>(null)
