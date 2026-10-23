import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'

/** The palette mobile will copy. Purple, violet, indigo and lavender are out (ADR-0094). */
describe('design tokens', () => {
  const raw = readFileSync(new URL('../../../docs/ui-revamp/tokens.json', import.meta.url), 'utf8')
  const tokens = JSON.parse(raw) as { color: { light: Record<string, string>; dark: Record<string, string> } }

  it('names the same roles in light and dark', () => {
    expect(Object.keys(tokens.color.light).sort()).toEqual(Object.keys(tokens.color.dark).sort())
  })

  it('uses no purple, violet, indigo or lavender hex', () => {
    const colors = JSON.stringify({ color: tokens.color, category: (JSON.parse(raw) as { category: unknown }).category }).toLowerCase()
    expect(colors).not.toMatch(/purple|violet|indigo|lavender/)
    const banned = ['#8250df', '#d2a8ff', '#a855f7', '#7c3aed', '#c4b5fd', '#db2777', '#f472b6', '#f9a8d4', '#fbcfe8']
    for (const hex of banned) expect(colors).not.toContain(hex)
  })
})
