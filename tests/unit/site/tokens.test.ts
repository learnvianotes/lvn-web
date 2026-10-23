import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { ACCENT_SWATCH, ACCENTS, PAPER } from '@/lib/theme'

interface AccentColors {
  brand: string
  brandHover: string
  brandForeground: string
  brandSoft: string
  codeTitle: string
}

interface Tokens {
  appearance: { defaultMode: string; defaultAccent: string; accents: string[]; storage: { mode: string; accent: string } }
  color: {
    base: { light: Record<string, string>; dark: Record<string, string> }
    themes: Record<string, { name: string; light: AccentColors; dark: AccentColors }>
  }
  category: { light: Record<string, string>; dark: Record<string, string> }
}

const raw = readFileSync(new URL('../../../docs/ui-revamp/tokens.json', import.meta.url), 'utf8')
const tokens = JSON.parse(raw) as Tokens
const productCss = readFileSync(new URL('../../../app/globals.css', import.meta.url), 'utf8')
const coreCss = readFileSync(new URL('../../../core-app/src/shared/styles/base.css', import.meta.url), 'utf8')

function channel(value: number) {
  const s = value / 255
  return s <= 0.04045 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4
}

function lum(hex: string) {
  const n = Number.parseInt(hex.slice(1), 16)
  const r = channel((n >> 16) & 255)
  const g = channel((n >> 8) & 255)
  const bl = channel(n & 255)
  return 0.2126 * r + 0.7152 * g + 0.0722 * bl
}

function contrast(a: string, b: string) {
  const hi = Math.max(lum(a), lum(b))
  const lo = Math.min(lum(a), lum(b))
  return (hi + 0.05) / (lo + 0.05)
}

function tone(map: Record<string, string>, key: string) {
  const value = map[key]
  if (!value) throw new Error(`missing ${key}`)
  return value
}

/** The palette mobile will copy. Purple, violet, indigo, lavender, and pink are out (ADR-0094). */
describe('design tokens', () => {
  it('shares one base and overrides only the brand per accent', () => {
    expect(Object.keys(tokens.color.base.light).sort()).toEqual(Object.keys(tokens.color.base.dark).sort())
    expect(tokens.color.base.light).not.toHaveProperty('brand')
    expect(tokens.appearance.defaultMode).toBe('system')
    expect(tokens.appearance.defaultAccent).toBe('navy')
    expect(tokens.appearance.accents).toEqual([...ACCENTS])
    expect(tokens.appearance.storage).toEqual({ mode: 'cnote:theme', accent: 'cnote:accent' })
    for (const id of ACCENTS) {
      const theme = tokens.color.themes[id]
      if (!theme) throw new Error(id)
      expect(theme.light.brand).toBe(ACCENT_SWATCH[id])
      expect(Object.keys(theme.light).sort()).toEqual(Object.keys(theme.dark).sort())
      expect(theme.light.codeTitle).toBe(theme.light.brand)
      expect(theme.dark.codeTitle).toBe(theme.dark.brand)
    }
    expect(tokens.color.base.light.paper).toBe(PAPER.light)
    expect(tokens.color.base.dark.paper).toBe(PAPER.dark)
  })

  it('keeps AA contrast for every accent in light and dark', () => {
    for (const scheme of ['light', 'dark'] as const) {
      const base = tokens.color.base[scheme]
      const paper = tone(base, 'paper')
      expect(contrast(tone(base, 'ink'), paper)).toBeGreaterThanOrEqual(4.5)
      expect(contrast(tone(base, 'inkMuted'), paper)).toBeGreaterThanOrEqual(4.5)
      for (const id of ACCENTS) {
        const theme = tokens.color.themes[id]?.[scheme]
        if (!theme) throw new Error(`${id} ${scheme}`)
        expect(contrast(theme.brand, paper), `${id} ${scheme} brand/paper`).toBeGreaterThanOrEqual(4.5)
        expect(contrast(theme.brand, theme.brandSoft), `${id} ${scheme} brand/soft`).toBeGreaterThanOrEqual(4.5)
        expect(contrast(theme.brandForeground, theme.brand), `${id} ${scheme} label/brand`).toBeGreaterThanOrEqual(4.5)
        expect(contrast(theme.brandForeground, theme.brandHover), `${id} ${scheme} label/hover`).toBeGreaterThanOrEqual(4.5)
      }
    }
  })

  it('uses no purple, violet, indigo, lavender, or pink hex', () => {
    const colors = JSON.stringify({ color: tokens.color, category: tokens.category }).toLowerCase()
    expect(colors).not.toMatch(/purple|violet|indigo|lavender|pink/)
    const banned = ['#8250df', '#d2a8ff', '#a855f7', '#7c3aed', '#c4b5fd', '#db2777', '#f472b6', '#f9a8d4', '#fbcfe8']
    for (const hex of banned) expect(colors).not.toContain(hex)
  })

  it('paints each accent from attribute selectors in both stylesheets', () => {
    for (const id of ACCENTS) {
      expect(productCss).toContain(`[data-accent='${id}']`)
      expect(productCss).toContain(`[data-theme='dark'][data-accent='${id}']`)
      expect(coreCss).toContain(`[data-accent='${id}']`)
      expect(coreCss).toContain(`[data-theme='dark'][data-accent='${id}']`)
      for (const scheme of ['light', 'dark'] as const) {
        const theme = tokens.color.themes[id]?.[scheme]
        if (!theme) throw new Error(`${id} ${scheme}`)
        expect(productCss).toContain(`--accent: ${theme.brand}`)
        expect(productCss).toContain(`--accent-hover: ${theme.brandHover}`)
        expect(productCss).toContain(`--accent-fg: ${theme.brandForeground}`)
        expect(productCss).toContain(`--accent-soft: ${theme.brandSoft}`)
        expect(coreCss).toContain(`--accent: ${theme.brand}`)
        expect(coreCss).toContain(`--accent-hover: ${theme.brandHover}`)
        expect(coreCss).toContain(`--accent-text: ${theme.brandForeground}`)
        expect(coreCss).toContain(`--accent-soft: ${theme.brandSoft}`)
        expect(coreCss).toContain(`--code-title: ${theme.codeTitle}`)
      }
    }
  })
})
