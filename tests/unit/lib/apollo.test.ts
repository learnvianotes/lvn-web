import { afterEach, describe, expect, it, vi } from 'vitest'
import { scrubText, setErrorSink, type ClientError } from '@/lib/analytics'
import { authFetch, isIntentionalAbort } from '@/lib/apollo'

const request = { method: 'POST', body: JSON.stringify({ operationName: 'Viewer' }) }

describe('isIntentionalAbort', () => {
  it('is a cancelled request: a bare AbortError, or Chromium aborting with no reason', () => {
    expect(isIntentionalAbort(new DOMException('aborted', 'AbortError'))).toBe(true)
    expect(isIntentionalAbort(new DOMException('The operation was aborted.', 'AbortError'))).toBe(true)
    expect(isIntentionalAbort(new Error('signal is aborted without reason'))).toBe(true)
    expect(isIntentionalAbort(new DOMException('The user aborted a request.', 'AbortError'))).toBe(true)
  })

  it('is not a failed fetch or a timeout, even when the message also says the operation was aborted', () => {
    expect(isIntentionalAbort(new TypeError('Failed to fetch'))).toBe(false)
    expect(isIntentionalAbort(new DOMException('session-check timeout', 'TimeoutError'))).toBe(false)
    expect(isIntentionalAbort(new DOMException('The operation was aborted.', 'TimeoutError'))).toBe(false)
    expect(isIntentionalAbort(new DOMException('The operation was aborted due to timeout', 'AbortError'))).toBe(false)
  })
})

describe('authFetch network errors', () => {
  const seen: ClientError[] = []

  afterEach(() => {
    seen.length = 0
    setErrorSink(() => undefined)
    vi.unstubAllGlobals()
  })

  async function rejected(error: unknown) {
    setErrorSink((event) => seen.push(event))
    vi.stubGlobal('fetch', () => Promise.reject(error))
    await expect(authFetch('http://localhost:4000/graphql', request)).rejects.toBe(error)
  }

  it('does not report an intentional abort, and still rejects with it', async () => {
    await rejected(new DOMException('aborted', 'AbortError'))
    await rejected(new Error('signal is aborted without reason'))
    expect(seen).toEqual([])
  })

  it('reports a failed fetch and a timeout, with the operation name and the stack', async () => {
    const failed = new TypeError('Failed to fetch')
    const timedOut = new DOMException('session-check timeout', 'TimeoutError')
    await rejected(failed)
    await rejected(timedOut)
    expect(seen).toEqual([
      { type: 'api.network', message: 'Failed to fetch', route: 'Viewer', stack: scrubText(failed.stack ?? '', 2000), at: expect.any(String) },
      { type: 'api.network', message: 'session-check timeout', route: 'Viewer', stack: scrubText(timedOut.stack ?? '', 2000), at: expect.any(String) },
    ])
  })
})
