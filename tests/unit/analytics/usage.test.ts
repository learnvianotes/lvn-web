import { describe, expect, it, vi } from 'vitest'
import { apiProblem, reportClientError, scrubText, setErrorSink } from '@/lib/analytics'
import { createUsageTracker, pagePath, usageProps, type UsageSender } from '@/lib/analytics/usage'
import { uploadFailureMessage } from '@/features/notes/media'

describe('usage tracker', () => {
  it('keeps the path and drops personal details from props', () => {
    expect(pagePath('/notes/abc?token=secret#x')).toBe('/notes/abc')
    expect(usageProps({ words: 3, kind: 'data_export', query: 'graphs', email: 'a@b.com', name: 'Asha', path: '/notes/1' })).toEqual([
      { key: 'words', value: '3' },
      { key: 'kind', value: 'data_export' },
    ])
  })

  it('does not send usage after an opt-out, and still sends errors', async () => {
    const send = vi.fn<UsageSender>(async () => undefined)
    const tracker = createUsageTracker({ send, signedIn: () => true, now: () => '2026-10-25T00:00:00.000Z', path: () => '/home' })
    tracker.setPreference(false)
    tracker.track('page_view')
    tracker.track('search', { words: 2, query: 'private note title' })
    tracker.setPreference(true)
    tracker.track('note_open')
    tracker.report({ type: 'upload', message: 'The file could not be uploaded.', route: '/notes', stack: null, at: '2026-10-25T00:00:00.000Z' })
    await tracker.flush()
    expect(send).toHaveBeenCalledTimes(1)
    const batch = send.mock.calls[0]?.[0]
    expect(batch?.usage).toEqual([])
    expect(batch?.errors).toEqual([{ type: 'upload', message: 'The file could not be uploaded.', route: '/notes', stack: null, at: '2026-10-25T00:00:00.000Z' }])
  })

  it('holds events until the person is known to allow analytics', async () => {
    const send = vi.fn<UsageSender>(async () => undefined)
    const tracker = createUsageTracker({ send, signedIn: () => true, now: () => '2026-10-25T00:00:00.000Z', path: () => '/search?q=secret' })
    tracker.track('page_view', { email: 'a@b.com' })
    await tracker.flush()
    expect(send).not.toHaveBeenCalled()
    tracker.setPreference(false)
    await tracker.flush()
    expect(send.mock.calls[0]?.[0]?.usage[0]).toMatchObject({ name: 'page_view', path: '/search', props: [] })
  })
})

describe('client errors', () => {
  it('strips email addresses before anything is stored', () => {
    expect(scrubText('failed for Asha <asha@college.edu>')).toBe('failed for Asha <[email]>')
    const seen: { message: string }[] = []
    setErrorSink((event) => seen.push(event))
    reportClientError({ type: 'api', message: 'boom for user@x.com', route: '/notes?token=1' }, false)
    expect(seen[0]).toMatchObject({ message: 'boom for [email]', route: '/notes' })
    setErrorSink(() => undefined)
  })

  it('ignores expected API refusals and the ingest call itself', () => {
    expect(apiProblem(200, { errors: [{ message: 'Sign in', extensions: { code: 'UNAUTHENTICATED' } }] }, 'Viewer')).toBeNull()
    expect(apiProblem(200, { errors: [{ message: 'nope' }] }, 'IngestEvents')).toBeNull()
    expect(apiProblem(500, {}, 'Viewer')).toBe('API request failed (500)')
    expect(apiProblem(200, { errors: [{ message: 'database down for a@b.com' }] }, 'Viewer')).toBe('database down for [email]')
  })
})

describe('upload failures', () => {
  it('says what went wrong instead of a bare network word', () => {
    expect(uploadFailureMessage('network')).toMatch(/could not be uploaded/)
    expect(uploadFailureMessage('network')).not.toBe('network')
    expect(uploadFailureMessage('status', 403)).toContain('403')
  })
})
