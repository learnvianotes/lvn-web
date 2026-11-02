import { describe, expect, it } from 'vitest'
import { ASSUMPTIONS, GAPS, absoluteUrl, noteSharePath, quizPath } from '@/features/beta/api'

describe('beta API contracts 0.74.0', () => {
  it('names the operations from lvn-backend PR #47', () => {
    const text = [...ASSUMPTIONS, ...GAPS].join('\n')
    for (const name of ['setNoteVisibility', 'UNLISTED', 'publicNotesRequireVerification', 'allowForks', 'forkCount', 'sharedQuiz', 'sharedQuizByLink', 'myQuizzes', 'publicQuizzes', 'PAGE_IMAGE', 'drawing', 'VOICE_NOTE', 'voiceCapture', 'transcribeCaptionClip', 'transcribeAudio', 'makeNotesFromTranscript']) {
      expect(text).toContain(name)
    }
  })

  it('builds absolute urls from the relative share paths', () => {
    expect(noteSharePath({ id: '01920000-0000-7000-8000-00000000a001', slug: 'searching', visibility: 'UNLISTED' })).toBe('/n/searching-01920000-0000-7000-8000-00000000a001')
    expect(noteSharePath({ id: '01920000-0000-7000-8000-00000000a001', slug: 'searching', visibility: 'SHARED' })).toBe('/notes/01920000-0000-7000-8000-00000000a001')
    expect(quizPath('abc')).toBe('/q/abc')
    expect(quizPath('abc', '/q/abc')).toBe('/q/abc')
    expect(absoluteUrl('/q/abc', 'http://localhost:3100')).toBe('http://localhost:3100/q/abc')
    expect(absoluteUrl('https://learn.example/q/abc', 'http://localhost:3100')).toBe('https://learn.example/q/abc')
  })
})
