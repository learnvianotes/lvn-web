import { describe, expect, it } from 'vitest'
import { pageInfo, SITE_DESCRIPTION } from '@core/app/title'
import type { Catalog } from '@core/features/catalog/types'

const catalog: Catalog = {
  version: 1,
  generatedAt: '2026-10-01T00:00:00Z',
  subjects: [
    { id: 'python', title: 'Python', description: 'Python from zero.', icon: 'python', kind: 'notes', order: 1, itemCount: 1,
      topics: [{ id: 'variables', title: 'Variables', group: '', headings: ['Names', 'Types'] }] },
    { id: 'sheet-150', title: 'Sheet 150', description: '150 problems.', icon: 'list', kind: 'problems', order: 2, itemCount: 2,
      topics: [{ id: 'stack', title: 'Stack', group: '', problems: [
        { id: 'a', lc: 20, title: 'Valid Parentheses', difficulty: 'Easy' },
        { id: 'b', lc: 155, title: 'Min Stack', difficulty: 'Medium' },
      ] }] },
  ],
}

describe('pageInfo', () => {
  it('names the home and about pages after the site', () => {
    expect(pageInfo(catalog, [])).toEqual({ title: 'LearnViaNotes', description: SITE_DESCRIPTION })
    expect(pageInfo(catalog, ['about']).title).toBe('About · LearnViaNotes')
  })

  it('uses the subject for a subject page', () => {
    expect(pageInfo(catalog, ['python'])).toEqual({ title: 'Python · LearnViaNotes', description: 'Python from zero.' })
  })

  it('describes a notes topic by its headings', () => {
    const info = pageInfo(catalog, ['python', 'variables'])
    expect(info.title).toBe('Variables · Python · LearnViaNotes')
    expect(info.description).toContain('Covers Names, Types.')
  })

  it('describes a problem category by its problem count', () => {
    expect(pageInfo(catalog, ['sheet-150', 'stack']).description).toMatch(/^Stack: 2 interview problems from Sheet 150/)
  })

  it('falls back to the site title while the catalog loads or for unknown paths', () => {
    expect(pageInfo(undefined, ['python', 'variables']).title).toBe('LearnViaNotes')
    expect(pageInfo(catalog, ['nope']).title).toBe('LearnViaNotes')
    expect(pageInfo(catalog, ['python', 'nope']).title).toBe('Python · LearnViaNotes')
  })
})
