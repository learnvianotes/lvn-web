import { describe, expect, it } from 'vitest'
import { meetHref } from '@/features/learning/meet'

describe('a Meet link shown to buddies', () => {
  it('keeps a Google Meet code and drops every other address', () => {
    expect(meetHref(' https://meet.google.com/abc-defg-hij ')).toBe('https://meet.google.com/abc-defg-hij')
    expect(meetHref('javascript:alert(1)')).toBeNull()
    expect(meetHref('https://evil.example/join')).toBeNull()
    expect(meetHref('https://meet.google.com/abc-defg-hij.evil.example')).toBeNull()
    expect(meetHref('')).toBeNull()
  })
})
