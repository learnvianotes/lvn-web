import { describe, expect, it } from 'vitest'
import { SHARING_ROOT_CAUSE, audienceDisabled, audienceOf, linkEnabled, wireVisibility } from '@/features/notes/share/visibility'

describe('share audience', () => {
  it('keeps Private, Shared, Unlisted and Public as their own wire values', () => {
    expect(audienceOf('PRIVATE')).toBe('PRIVATE')
    expect(audienceOf('SHARED')).toBe('SHARED')
    expect(audienceOf('UNLISTED')).toBe('UNLISTED')
    expect(audienceOf('PUBLIC')).toBe('PUBLIC')
    expect(wireVisibility('UNLISTED')).toBe('UNLISTED')
    expect(wireVisibility('SHARED')).toBe('SHARED')
  })

  it('lets Public be chosen before a note is published when verification is not required', () => {
    expect(audienceDisabled({ changeVisibility: true, offPublic: false, audience: 'PUBLIC', publicHeld: false })).toBe(false)
    expect(audienceDisabled({ changeVisibility: true, offPublic: false, audience: 'UNLISTED' })).toBe(false)
  })

  it('gates Public when the setting holds this account, and on moderation', () => {
    expect(audienceDisabled({ changeVisibility: true, offPublic: false, audience: 'PUBLIC', publicHeld: true })).toBe(true)
    expect(audienceDisabled({ changeVisibility: true, offPublic: false, audience: 'PUBLIC', publicHeld: false })).toBe(false)
    expect(audienceDisabled({ changeVisibility: true, offPublic: true, audience: 'PUBLIC' })).toBe(true)
    expect(audienceDisabled({ changeVisibility: false, offPublic: false, audience: 'PRIVATE' })).toBe(true)
  })

  it('enables the link once the note is no longer private', () => {
    expect(linkEnabled('PRIVATE')).toBe(false)
    expect(linkEnabled('SHARED')).toBe(true)
    expect(linkEnabled('UNLISTED')).toBe(true)
    expect(linkEnabled('PUBLIC')).toBe(true)
  })

  it('records why a draft stayed on Private', () => {
    expect(SHARING_ROOT_CAUSE).toMatch(/sr-only/)
    expect(SHARING_ROOT_CAUSE).toMatch(/published/)
  })
})
