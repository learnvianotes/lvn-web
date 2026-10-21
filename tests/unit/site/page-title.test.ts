import { describe, expect, it } from 'vitest'
import { templated } from '@/lib/page-title'

/** How Next fills the title template (next/dist/lib/metadata/resolvers/resolve-title.js). */
const fill = (template: string, title: string) => template.replace(/%s/g, title)

describe('templated', () => {
  it('a "$" in a title stays a "$" in the filled template', () => {
    const tricky = "Costs $& $' $` $1 $$ </script>"
    expect(fill('%s · LearnViaNotes', templated(tricky))).toBe(`${tricky} · LearnViaNotes`)
    // Without it the template garbles the title.
    expect(fill('%s · LearnViaNotes', tricky)).not.toBe(`${tricky} · LearnViaNotes`)
  })

  it('leaves titles without a "$" alone', () => {
    expect(templated("Dijkstra's algorithm")).toBe("Dijkstra's algorithm")
  })
})
