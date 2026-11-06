import { describe, expect, it } from 'vitest'
import { safeLinkHref } from '@/lib/http-url'

describe('safeLinkHref', () => {
  it('keeps http, https, and mailto when mail is allowed', () => {
    expect(safeLinkHref('https://books.example.com/clean-code')).toBe('https://books.example.com/clean-code')
    expect(safeLinkHref('http://localhost:3000/file')).toBe('http://localhost:3000/file')
    expect(safeLinkHref('mailto:ada@example.com')).toBeNull()
    expect(safeLinkHref('mailto:ada@example.com', { mailto: true })).toBe('mailto:ada@example.com')
  })

  it.each([
    'javascript:alert(1)',
    'JAVASCRIPT:alert(1)',
    'java\tscript:alert(1)',
    'data:text/html,<script>alert(1)</script>',
    '//evil.example',
    '/notes/1',
    'https://evil.example\\\n.good.example',
    ' javascript:alert(1)',
    'https://user:pass@books.example.com/clean-code',
    '',
  ])('rejects %j', (href) => {
    expect(safeLinkHref(href, { mailto: true })).toBeNull()
  })

  it('returns the canonical URL, so a raw value cannot disagree with the parsed one', () => {
    expect(safeLinkHref('https://books.example.com')).toBe('https://books.example.com/')
  })
})
