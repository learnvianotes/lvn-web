import { describe, expect, it } from 'vitest'
import { catalog as catalogSchema } from '@/features/core-content/schema'
import { getCatalog } from '@/features/core-content/source'

/** The landing page and sitemap.xml read content-build/catalog.json through this module. */
describe('getCatalog', () => {
  const catalog = getCatalog()

  it('parses the catalog with every subject and its topics', () => {
    expect(catalog.subjects.length).toBeGreaterThan(0)
    for (const s of catalog.subjects) {
      expect(s.topics.length, s.id).toBeGreaterThan(0)
      expect(s.itemCount, s.id).toBe(s.kind === 'notes' ? s.topics.length : s.topics.reduce((n, t) => n + (t.problems?.length ?? 0), 0))
    }
  })

  it('orders subjects for the landing page', () => {
    const orders = catalog.subjects.map((s) => s.order)
    expect(orders).toEqual([...orders].sort((a, b) => a - b))
  })

  it('puts every subject in a known category', () => {
    const categories = new Set(catalog.categories.map((c) => c.id))
    for (const s of catalog.subjects) expect(categories, s.id).toContain(s.category)
  })

  it('rejects a malformed export instead of rendering it', () => {
    expect(catalogSchema.safeParse({ ...catalog, subjects: [{ id: 'x' }] }).success).toBe(false)
  })
})
