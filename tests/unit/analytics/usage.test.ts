import { describe, expect, it, vi } from 'vitest'
import { apiProblem, reportClientError, scrubText, setErrorSink } from '@/lib/analytics'
import { createUsageTracker, pagePath, usageProps, type UsageSender } from '@/lib/analytics/usage'
import { uploadFailureMessage } from '@/features/notes/media'

describe('usage tracker', () => {
  it('keeps short props and drops personal details', () => {
    expect(pagePath('/notes/abc?token=secret#x')).toBe('/notes/abc')
    expect(usageProps({ words: 3, kind: 'data_export', feature: 'export', query: 'graphs', email: 'a@b.com', name: 'Asha', path: '/notes/1' })).toEqual({
      words: 3,
      kind: 'data_export',
      feature: 'export',
    })
  })

  it('does not send usage after an opt-out, and still sends errors through the same batch', async () => {
    const send = vi.fn<UsageSender>(async () => undefined)
    const tracker = createUsageTracker({ send, signedIn: () => true, now: () => '2026-10-25T00:00:00.000Z' })
    tracker.setPreference(false)
    tracker.track('page_view')
    tracker.track('search', { words: 2, query: 'private note title' })
    tracker.setPreference(true)
    tracker.track('note_open')
    tracker.report({ type: 'upload', message: 'The file could not be uploaded.', route: '/notes', stack: null, at: '2026-10-25T00:00:00.000Z' })
    await tracker.flush()
    expect(send).toHaveBeenCalledTimes(1)
    const batch = send.mock.calls[0]?.[0]
    expect(batch?.events).toEqual([])
    expect(batch?.errors).toEqual([{ code: 'upload', message: 'The file could not be uploaded.', platform: 'WEB', route: '/notes', occurredAt: '2026-10-25T00:00:00.000Z' }])
  })

  it('holds events until the person is known to allow analytics, and drops names the API refuses', async () => {
    const send = vi.fn<UsageSender>(async () => undefined)
    const tracker = createUsageTracker({ send, signedIn: () => true, now: () => '2026-10-25T00:00:00.000Z' })
    tracker.track('page_view', { email: 'a@b.com' })
    tracker.track('sign_out')
    tracker.track('note_create')
    await tracker.flush()
    expect(send).not.toHaveBeenCalled()
    tracker.setPreference(false)
    await tracker.flush()
    expect(send.mock.calls[0]?.[0]?.events).toEqual([{ name: 'page_view', platform: 'WEB', occurredAt: '2026-10-25T00:00:00.000Z', props: {} }])
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
    expect(apiProblem(200, { errors: [{ message: 'Enter the code emailed to you before using admin tools.', extensions: { code: 'ADMIN_MFA_REQUIRED' } }] }, 'AdminMetrics')).toBeNull()
    expect(apiProblem(200, { errors: [{ message: 'nope' }] }, 'IngestAnalytics')).toBeNull()
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
