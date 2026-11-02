import { describe, expect, it } from 'vitest'
import { captionsFromEvent, joinCaption, speechRecognitionCtor } from '@/features/notes/editor/captions'

describe('live captions', () => {
  it('joins a final phrase with the latest interim line', () => {
    const first = captionsFromEvent(
      { resultIndex: 0, results: [{ isFinal: true, 0: { transcript: 'binary search' }, length: 1 }] },
      '',
    )
    expect(first).toEqual({ finals: 'binary search', line: 'binary search' })
    const next = captionsFromEvent(
      {
        resultIndex: 1,
        results: [
          { isFinal: true, 0: { transcript: 'binary search' }, length: 1 },
          { isFinal: false, 0: { transcript: 'halves' }, length: 1 },
        ],
      },
      first.finals,
    )
    expect(next.line).toBe('binary search halves')
    expect(joinCaption('  a  ', '  b ')).toBe('a b')
  })

  it('has no speech recognition outside a browser', () => {
    expect(speechRecognitionCtor()).toBeNull()
  })
})
