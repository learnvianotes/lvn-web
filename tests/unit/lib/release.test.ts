import { afterEach, describe, expect, it, vi } from 'vitest'
import { releaseInfo } from '@/lib/release'

describe('releaseInfo', () => {
  it('reports the package version and the first 12 characters of the git SHA', () => {
    expect(releaseInfo({ version: '0.5.0', commit: '31e81150d2d5a196460744ee8312258490551bb4' })).toEqual({
      version: '0.5.0',
      commit: '31e81150d2d5',
    })
  })

  it('keeps a short SHA, drops a leading v, and lowercases hex', () => {
    expect(releaseInfo({ version: 'v0.5.0', commit: 'ABCDEF0' })).toEqual({ version: '0.5.0', commit: 'abcdef0' })
  })

  it('uses unknown when the version or commit was not provided', () => {
    expect(releaseInfo({ version: '  ', commit: '' })).toEqual({ version: 'unknown', commit: 'unknown' })
    expect(releaseInfo({ version: '0.5.0', commit: 'not-a-sha' })).toEqual({ version: '0.5.0', commit: 'unknown' })
    expect(releaseInfo({ version: '0.5.0', commit: 'unknown' })).toEqual({ version: '0.5.0', commit: 'unknown' })
  })
})

describe('GET /version', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it('returns the build identity as JSON and asks clients not to cache it', async () => {
    vi.stubEnv('NEXT_PUBLIC_APP_VERSION', '0.5.0')
    vi.stubEnv('NEXT_PUBLIC_GIT_SHA', '31e81150d2d5a196460744ee8312258490551bb4')
    const { GET } = await import('@/app/(site)/version/route')
    const response = GET()
    expect(response.headers.get('content-type')).toMatch(/application\/json/)
    expect(response.headers.get('cache-control')).toBe('no-store')
    expect(await response.json()).toEqual({ version: '0.5.0', commit: '31e81150d2d5' })
  })
})
