import { describe, expect, it } from 'vitest'
import { parsePublicNoteSegment, publicNotePath } from '@/features/public-notes/paths'

const ID = '01920000-0000-7000-8000-00000000d001'

describe('public note addresses', () => {
  it('are /n/<slug>-<id>, with a stand-in slug for untitled notes', () => {
    expect(publicNotePath({ id: ID, slug: 'binary-search' })).toBe(`/n/binary-search-${ID}`)
    expect(publicNotePath({ id: ID, slug: '' })).toBe(`/n/note-${ID}`)
  })

  it('read back the id, whatever the slug holds', () => {
    expect(parsePublicNoteSegment(`binary-search-${ID}`)).toEqual({ id: ID, slug: 'binary-search' })
    expect(parsePublicNoteSegment(ID)).toEqual({ id: ID, slug: '' })
    expect(parsePublicNoteSegment(`a-b-c-${ID.toUpperCase()}`)).toEqual({ id: ID, slug: 'a-b-c' })
    expect(parsePublicNoteSegment(encodeURIComponent(`गणित-${ID}`))).toEqual({ id: ID, slug: 'गणित' })
  })

  it('refuse segments without a note id', () => {
    for (const s of ['binary-search', `${ID}-x`, `x${ID.slice(1)}z`, '']) expect(parsePublicNoteSegment(s)).toBeNull()
  })
})
