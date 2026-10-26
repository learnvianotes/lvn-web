import { describe, expect, it } from 'vitest'
import { SHARING_ROOT_CAUSE, audienceDisabled, audienceOf, linkEnabled, wireVisibility } from '@/features/notes/share/visibility'

describe('share audience', () => {
  it('maps the wire visibility onto Private, Unlisted and Public', () => {
    expect(audienceOf('PRIVATE')).toBe('PRIVATE')
    expect(audienceOf('SHARED')).toBe('UNLISTED')
    expect(audienceOf('PUBLIC')).toBe('PUBLIC')
    expect(wireVisibility('UNLISTED')).toBe('SHARED')
    expect(wireVisibility('PUBLIC')).toBe('PUBLIC')
    expect(wireVisibility('PRIVATE')).toBe('PRIVATE')
  })

  it('lets Public be chosen before a note is published', () => {
    expect(audienceDisabled({ changeVisibility: true, offPublic: false, audience: 'PUBLIC' })).toBe(false)
    expect(audienceDisabled({ changeVisibility: true, offPublic: false, audience: 'UNLISTED' })).toBe(false)
  })

  it('keeps Public off when moderation hides the note, and blocks every choice without permission', () => {
    expect(audienceDisabled({ changeVisibility: true, offPublic: true, audience: 'PUBLIC' })).toBe(true)
    expect(audienceDisabled({ changeVisibility: true, offPublic: true, audience: 'UNLISTED' })).toBe(false)
    expect(audienceDisabled({ changeVisibility: false, offPublic: false, audience: 'PRIVATE' })).toBe(true)
  })

  it('enables the link once the note is no longer private', () => {
    expect(linkEnabled('PRIVATE')).toBe(false)
    expect(linkEnabled('SHARED')).toBe(true)
    expect(linkEnabled('PUBLIC')).toBe(true)
  })

  it('records why a draft stayed on Private', () => {
    expect(SHARING_ROOT_CAUSE).toMatch(/sr-only/)
    expect(SHARING_ROOT_CAUSE).toMatch(/published/)
  })
})
