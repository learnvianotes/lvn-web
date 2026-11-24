import { describe, expect, it } from 'vitest'
import { LEGAL } from '@/config/legal'
import { SITE_DESCRIPTION, SITE_KEYWORDS, SUPPORT_EMAIL } from '@/lib/site'
import robots from '@/app/robots'

describe('support email', () => {
  it('is the one published address, and the legal pages use it', () => {
    expect(SUPPORT_EMAIL).toBe('support@learnvianotes.in')
    expect(LEGAL.email).toBe(SUPPORT_EMAIL)
  })
})

describe('site description', () => {
  it('stays within a search snippet and names student notes', () => {
    expect(SITE_DESCRIPTION.length).toBeLessThanOrEqual(160)
    expect(SITE_DESCRIPTION).toMatch(/student notes/)
    expect(SITE_KEYWORDS).toEqual(['student notes', 'notes', 'learn', 'share notes', 'study notes', 'class notes', 'LearnViaNotes'])
  })
})

describe('robots.txt', () => {
  it('allows the public site, disallows private areas, and names the sitemap', () => {
    const body = robots()
    expect(body.sitemap).toBe('http://localhost:3000/sitemap.xml')
    const rule = Array.isArray(body.rules) ? body.rules[0] : body.rules
    expect(rule?.userAgent).toBe('*')
    expect(rule?.allow).toBe('/')
    const disallow = rule?.disallow
    expect(disallow).toEqual(expect.arrayContaining(['/admin', '/dashboard', '/home', '/settings', '/api', '/oauth', '/__/']))
    expect(disallow).not.toContain('/')
  })
})
