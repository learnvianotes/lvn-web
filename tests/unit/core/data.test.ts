import { describe, expect, it } from 'vitest'
import { legacyCatalog, legacyDataPaths, legacyDocument, legacyMeta } from '@core-server/content'
import type { Problem, TopicDoc } from '@core/features/catalog/types'

const catalog = legacyCatalog()
const notes = catalog.subjects.find((s) => s.kind === 'notes')!
const sheet = catalog.subjects.find((s) => s.kind === 'problems')!

describe('/core data paths', () => {
  it('lists meta, the catalog and one document per topic or problem category', () => {
    const paths = legacyDataPaths()
    const items = catalog.subjects.reduce((n, s) => n + s.topics.length, 0)
    expect(paths.slice(0, 2)).toEqual(['meta.json', 'catalog.json'])
    expect(paths).toHaveLength(items + 2)
    expect(new Set(paths).size).toBe(paths.length)
    expect(paths).toContain(`topics/${notes.id}/${notes.topics[0]!.id}.json`)
    expect(paths).toContain(`problems/${sheet.id}/${sheet.topics[0]!.id}.json`)
  })

  it('resolves every listed path to a document', () => {
    for (const p of legacyDataPaths()) expect(legacyDocument(p), p).toBeDefined()
  })
})

describe('/core documents', () => {
  it('serves a topic as structured content, like the old Firestore document', () => {
    const t = notes.topics[0]!
    const doc = legacyDocument(`topics/${notes.id}/${t.id}.json`) as TopicDoc
    expect(doc).toMatchObject({ subjectId: notes.id, id: t.id, title: t.title })
    expect(Array.isArray(doc.content)).toBe(true)
    expect(doc.content.length).toBeGreaterThan(0)
  })

  it('serves a problem category in sheet order with rich fields converted', () => {
    const category = sheet.topics[0]!
    const problems = legacyDocument(`problems/${sheet.id}/${category.id}.json`) as Problem[]
    expect(problems.map((p) => p.id)).toEqual(category.problems!.map((p) => p.id))
    const orders = problems.map((p) => p.order)
    expect(orders).toEqual([...orders].sort((a, b) => a - b))
    for (const p of problems) {
      expect(Array.isArray(p.statement)).toBe(true)
      expect(p).not.toHaveProperty('naive.html')
      if (p.optimal) expect(Array.isArray(p.optimal.content)).toBe(true)
    }
  })

  it.each([
    'nope.json',
    'topics/nope/x.json',
    `topics/${notes.id}/nope.json`,
    `topics/${notes.id}/../catalog.json`,
    `topics/${sheet.id}/${sheet.topics[0]!.id}.json`,
    `problems/${notes.id}/${notes.topics[0]!.id}.json`,
    `problems/${sheet.id}/nope.json`,
  ])('has no document at %s', (p) => {
    expect(legacyDocument(p)).toBeUndefined()
  })
})

describe('/core content version', () => {
  it('counts what is served and is stable', () => {
    const meta = legacyMeta()
    expect(meta.version).toMatch(/^[0-9a-f]{16}$/)
    expect(meta.subjects).toBe(catalog.subjects.length)
    expect(meta.topics).toBe(catalog.subjects.filter((s) => s.kind === 'notes').reduce((n, s) => n + s.topics.length, 0))
    expect(meta.problems).toBe(sheet.topics.reduce((n, t) => n + (t.problems?.length ?? 0), 0))
    expect(legacyMeta()).toBe(meta)
  })
})
