/* ============================================================
   C-NOTE THEME TYPES
   ============================================================ */

/** The two supported themes */
export type Theme = 'dark' | 'light'

/** Theme context shape */
export interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
  setTheme: (theme: Theme) => void
}
