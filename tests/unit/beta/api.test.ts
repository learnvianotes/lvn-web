import { describe, expect, it } from 'vitest'
import { ASSUMPTIONS, quizLink } from '@/features/beta/api'

describe('beta API assumptions', () => {
  it('names the operations the backend is adding', () => {
    const text = ASSUMPTIONS.join('\n')
    for (const name of ['setNoteVisibility', 'forkNote', 'shareQuiz', 'sharedQuiz', 'submitSharedQuiz', 'notePages', 'saveNotePages', 'transcribeVoiceNote', 'notesFromTranscript']) {
      expect(text).toContain(name)
    }
    expect(text).toMatch(/SHARED/)
    expect(text).toMatch(/forkingEnabled/)
  })

  it('builds an absolute quiz link from a token or a path', () => {
    expect(quizLink({ token: 'abc', url: 'https://learn.example/quiz/abc' }, 'http://localhost:3100')).toBe('https://learn.example/quiz/abc')
    expect(quizLink({ token: 'abc', url: '/quiz/abc' }, 'http://localhost:3100')).toBe('http://localhost:3100/quiz/abc')
    expect(quizLink({ token: 'abc', url: '' }, 'http://localhost:3100')).toBe('http://localhost:3100/quiz/abc')
  })
})
