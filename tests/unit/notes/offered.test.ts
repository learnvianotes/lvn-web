import { describe, expect, it } from 'vitest'
import { offeredTabs, type TabInputs } from '@/features/notes/view/offered'

const base: TabInputs = { canEdit: false, reader: true, published: true, ai: false, cardTypes: [], tasks: [] }

describe('the tabs a note offers (lvn-backend ADR-0076): never an empty tab with nothing to do', () => {
  it('a reader with AI off sees the content and the discussion, and a study tab only when it has something', () => {
    expect(offeredTabs(base)).toEqual(['content', 'discussions'])
    expect(offeredTabs({ ...base, cardTypes: ['text', 'flashcard'] })).toEqual(['content', 'flashcards', 'discussions'])
    expect(offeredTabs({ ...base, cardTypes: ['question'] })).toEqual(['content', 'quiz', 'discussions'])
    expect(offeredTabs({ ...base, tasks: ['SUMMARIZE', 'QUIZ'] })).toEqual(['content', 'summary', 'quiz', 'discussions'])
  })

  it('with AI on, every study tab can make something', () => {
    expect(offeredTabs({ ...base, ai: true })).toEqual(['content', 'summary', 'flashcards', 'quiz', 'discussions'])
  })

  it('its editors can always add flashcards and quiz cards; the discussion opens once published', () => {
    const owner = { ...base, reader: false, canEdit: true, published: false }
    expect(offeredTabs(owner)).toEqual(['content', 'flashcards', 'quiz'])
    expect(offeredTabs({ ...owner, published: true })).toEqual(['content', 'flashcards', 'quiz', 'discussions'])
  })
})
