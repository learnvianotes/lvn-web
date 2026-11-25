/**
 * Appearance shared by the product site and /core.
 *
 * `cnote:theme` is the old site's key (JSON "light", "dark", or "system"). Core treats anything
 * other than light or dark as system, and removes the key for system. A missing key is system.
 * `cnote:accent` is JSON "ink" | "navy" | "teal" | "forest" | "slate" | "amber". A missing key is ink.
 *
 * `data-theme` is the resolved light or dark (what CSS and the core reader assert).
 * `data-accent` selects the brand overrides. `data-mode` is the saved mode, including system.
 * The pre-paint script in each root layout sets all three before first paint.
 */

export const THEME_KEY = 'cnote:theme'
export const ACCENT_KEY = 'cnote:accent'

export const MODES = ['system', 'light', 'dark'] as const
export const ACCENTS = ['ink', 'navy', 'teal', 'forest', 'slate', 'amber'] as const

export type ThemeMode = (typeof MODES)[number]
export type AccentId = (typeof ACCENTS)[number]
export type ResolvedTheme = 'light' | 'dark'

/** Paper, used for the browser theme-color as well as the page. Matches tokens.json color.base. */
export const PAPER: Record<ResolvedTheme, string> = {
  light: '#f8f7f4',
  dark: '#141413',
}

/** Light brand, used only as the picker's swatch. CSS owns the real accent. */
export const ACCENT_SWATCH: Record<AccentId, string> = {
  ink: '#1e40af',
  navy: '#1e4d8c',
  teal: '#0c5c66',
  forest: '#0f6b45',
  slate: '#334155',
  amber: '#8a4b08',
}

export function isThemeMode(value: unknown): value is ThemeMode {
  return value === 'system' || value === 'light' || value === 'dark'
}

export function isAccentId(value: unknown): value is AccentId {
  return value === 'ink' || value === 'navy' || value === 'teal' || value === 'forest' || value === 'slate' || value === 'amber'
}

/** Parse the stored mode. Missing, invalid, or core's removed key all mean system. */
export function readMode(raw: string | null): ThemeMode {
  if (raw == null) return 'system'
  try {
    const value: unknown = JSON.parse(raw)
    if (isThemeMode(value)) return value
  } catch {
    /* not JSON — fall through */
  }
  return isThemeMode(raw) ? raw : 'system'
}

/** Parse the stored accent. Missing or unknown values fall back to ink. */
export function readAccent(raw: string | null): AccentId {
  if (raw == null) return 'ink'
  try {
    const value: unknown = JSON.parse(raw)
    if (isAccentId(value)) return value
  } catch {
    /* not JSON — fall through */
  }
  return isAccentId(raw) ? raw : 'ink'
}

export function resolveAppearance(mode: ThemeMode, prefersDark: boolean): ResolvedTheme {
  if (mode === 'system') return prefersDark ? 'dark' : 'light'
  return mode
}

export function prefersDark(): boolean {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') return false
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

/** Write the resolved theme and the accent onto the document. Safe to call again. */
export function applyAppearance(mode: ThemeMode, accent: AccentId, systemDark: boolean): ResolvedTheme {
  const resolved = resolveAppearance(mode, systemDark)
  if (typeof document === 'undefined') return resolved
  const root = document.documentElement
  root.dataset.theme = resolved
  root.dataset.accent = accent
  root.dataset.mode = mode
  const color = PAPER[resolved]
  document.querySelectorAll('meta[name="theme-color"]').forEach((el) => {
    el.setAttribute('content', color)
  })
  return resolved
}

/**
 * Inline script for <head>. It re-reads storage on every OS scheme change, so a later
 * choice (including one made by the /core toggle) is not overwritten by a stale closure.
 * Accent colors themselves live in CSS attribute selectors, not in this script.
 */
export function themeBootScript(): string {
  const modeKey = JSON.stringify(THEME_KEY)
  const accentKey = JSON.stringify(ACCENT_KEY)
  const light = JSON.stringify(PAPER.light)
  const dark = JSON.stringify(PAPER.dark)
  return `try{var q=matchMedia('(prefers-color-scheme: dark)');var paint=function(){var mode='system';try{mode=JSON.parse(localStorage.getItem(${modeKey}))}catch(e){}if(mode!=='light'&&mode!=='dark'&&mode!=='system')mode='system';var accent='ink';try{accent=JSON.parse(localStorage.getItem(${accentKey}))}catch(e){}if(accent!=='ink'&&accent!=='navy'&&accent!=='teal'&&accent!=='forest'&&accent!=='slate'&&accent!=='amber')accent='ink';var tone=mode==='system'?(q.matches?'dark':'light'):mode;var root=document.documentElement;root.setAttribute('data-theme',tone);root.setAttribute('data-accent',accent);root.setAttribute('data-mode',mode);var color=tone==='dark'?${dark}:${light};document.querySelectorAll('meta[name="theme-color"]').forEach(function(el){el.setAttribute('content',color)})};paint();q.addEventListener('change',paint)}catch(e){}`
}
