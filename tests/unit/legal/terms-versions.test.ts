import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { isPublishedTermsVersion, PUBLISHED_TERMS_VERSIONS, publishedTermsVersion, TERMS_VERSION } from '@/features/legal/documents'
import { LegalPage } from '@/features/legal/LegalPage'
import { displayedTermsVersion, fetchTermsVersion, getDisplayedTermsVersion, TERMS_VERSION_REVALIDATE_SECONDS } from '@/features/legal/terms-version'

/** The API's rule for a version (lvn-backend contexts/users/src/domain/terms.ts isTermsVersion): a real YYYY-MM-DD. */
const isRealDate = (v: string) => /^\d{4}-\d{2}-\d{2}$/.test(v) && new Date(`${v}T00:00:00Z`).toISOString().slice(0, 10) === v

describe('PUBLISHED_TERMS_VERSIONS (lvn-backend ADR-0103)', () => {
  const versions = PUBLISHED_TERMS_VERSIONS.map((v) => v.version)

  it('is sorted oldest first, without duplicates', () => {
    expect(versions.length).toBeGreaterThan(0)
    expect([...versions].sort()).toEqual(versions)
    expect(new Set(versions).size).toBe(versions.length)
  })

  it('holds real YYYY-MM-DD dates, as the API accepts, each with a short summary', () => {
    for (const v of PUBLISHED_TERMS_VERSIONS) {
      expect(isRealDate(v.version), v.version).toBe(true)
      expect(v.summary.trim().length, v.version).toBeGreaterThan(0)
      expect(v.summary.length, v.version).toBeLessThanOrEqual(160)
    }
  })

  it('ends with TERMS_VERSION, the version of the text the pages ship', () => {
    expect(versions).toContain(TERMS_VERSION)
    expect(versions.at(-1)).toBe(TERMS_VERSION)
  })

  it('keeps every version people have accepted', () => {
    // The API's built-in allowlist (DEFAULT_PUBLISHED_TERMS_VERSIONS) is 2026-10-08,2026-11-03; dropping one here
    // would make the admin page refuse a version the API still allows.
    expect(versions).toEqual(expect.arrayContaining(['2026-10-08', '2026-11-03']))
  })

  it('answers whether a version is published', () => {
    expect(isPublishedTermsVersion(TERMS_VERSION)).toBe(true)
    expect(isPublishedTermsVersion('2026-10-08')).toBe(true)
    expect(isPublishedTermsVersion('2099-01-01')).toBe(false)
    expect(isPublishedTermsVersion('')).toBe(false)
    expect(publishedTermsVersion('2026-10-08')?.summary).toMatch(/First/)
    expect(publishedTermsVersion('2099-01-01')).toBeUndefined()
  })
})

describe('the legal pages’ version label', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.restoreAllMocks()
  })

  const answer = (body: unknown, status = 200) => vi.fn(async () => new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } }))

  it('shows the API’s version when this web build published it', () => {
    const warn = vi.fn()
    expect(displayedTermsVersion('2026-10-08', warn)).toBe('2026-10-08')
    expect(displayedTermsVersion(TERMS_VERSION, warn)).toBe(TERMS_VERSION)
    expect(warn).not.toHaveBeenCalled()
  })

  it('falls back to the newest local version when the API cannot answer', () => {
    const warn = vi.fn()
    expect(displayedTermsVersion(null, warn)).toBe(TERMS_VERSION)
    expect(warn).not.toHaveBeenCalled()
  })

  it('shows the newest local version and warns when the API’s version has no text here', () => {
    const warn = vi.fn()
    expect(displayedTermsVersion('2099-01-01', warn)).toBe(TERMS_VERSION)
    expect(warn).toHaveBeenCalledOnce()
    expect(warn.mock.calls[0]?.[0]).toMatch(/2099-01-01.*PUBLISHED_TERMS_VERSIONS/)
  })

  it('asks the API anonymously for Query.termsVersion, cached for a minute', async () => {
    const fetch = answer({ data: { termsVersion: '2026-10-08' } })
    vi.stubGlobal('fetch', fetch)
    await expect(fetchTermsVersion()).resolves.toBe('2026-10-08')
    expect(TERMS_VERSION_REVALIDATE_SECONDS).toBe(60)
    const [url, init] = fetch.mock.calls[0] as unknown as [string, RequestInit & { next: { revalidate: number; tags: string[] } }]
    expect(url).toBe('http://localhost:4000/graphql')
    expect(init.method).toBe('POST')
    expect(new Headers(init.headers).has('authorization')).toBe(false)
    expect(init.credentials).toBeUndefined()
    expect(JSON.parse(init.body as string).query).toMatch(/query LegalTermsVersion\s*\{\s*termsVersion\s*\}/)
    expect(init.next).toEqual({ revalidate: 60, tags: ['terms-version'] })
    expect(init.signal).toBeInstanceOf(AbortSignal)
  })

  it('treats an HTTP failure, a GraphQL error, a missing value or a network error as no answer', async () => {
    vi.stubGlobal('fetch', answer({ errors: [{ message: 'down' }] }, 503))
    await expect(fetchTermsVersion()).resolves.toBeNull()
    vi.stubGlobal('fetch', answer({ errors: [{ message: 'boom' }], data: null }))
    await expect(fetchTermsVersion()).resolves.toBeNull()
    vi.stubGlobal('fetch', answer({ data: { termsVersion: '' } }))
    await expect(fetchTermsVersion()).resolves.toBeNull()
    vi.stubGlobal('fetch', answer({ data: { termsVersion: 20261103 } }))
    await expect(fetchTermsVersion()).resolves.toBeNull()
    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('fetch failed') }))
    await expect(fetchTermsVersion()).resolves.toBeNull()
    await expect(getDisplayedTermsVersion()).resolves.toBe(TERMS_VERSION)
  })

  it('renders the label on the page, never crashing on an unknown version', async () => {
    const page = async () => renderToStaticMarkup(await LegalPage({ doc: 'terms', children: createElement('p', null, 'text') }))
    vi.stubGlobal('fetch', answer({ data: { termsVersion: '2026-10-08' } }))
    expect(await page()).toContain('Version 2026-10-08')

    const warn = vi.spyOn(console, 'warn').mockImplementation(() => undefined)
    vi.stubGlobal('fetch', answer({ data: { termsVersion: '2099-01-01' } }))
    expect(await page()).toContain(`Version ${TERMS_VERSION}`)
    expect(warn).toHaveBeenCalledOnce()

    vi.stubGlobal('fetch', vi.fn(async () => { throw new TypeError('fetch failed') }))
    expect(await page()).toContain(`Version ${TERMS_VERSION}`)
  })
})
