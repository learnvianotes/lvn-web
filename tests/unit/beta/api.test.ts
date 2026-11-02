import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { ASSUMPTIONS, GAPS, absoluteUrl, noteSharePath, quizPath } from '@/features/beta/api'

describe('beta API against the vendored schema', () => {
  it('names the real operations and the gaps the schema leaves', () => {
    const text = [...ASSUMPTIONS, ...GAPS].join('\n')
    for (const name of ['changeNoteVisibility', 'UNLISTED', 'publicNotesRequireVerification', 'allowForks', 'forkCount', 'createSharedQuiz', 'sharedQuiz', 'sharedQuizByLink', 'myQuizzes', 'publicQuizzes', 'PAGE_IMAGE', 'saveNotePages', 'VOICE_NOTE', 'voiceCapture', 'transcribeCaptionClip', 'transcribeAudio', 'makeNotesFromTranscript', 'sharePath', 'choiceIds']) {
      expect(text).toContain(name)
    }
    expect(text).toContain('There is no shareQuiz')
    const api = readFileSync('features/beta/api.ts', 'utf8')
    expect(api).not.toMatch(/from 'graphql'/)
    expect(api).not.toMatch(/(?:query|mutation)\s+[A-Z][A-Za-z0-9_]*\s*(\(|\{)/)
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
