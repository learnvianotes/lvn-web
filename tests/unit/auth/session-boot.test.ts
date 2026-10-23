import { afterEach, describe, expect, it, vi } from 'vitest'
import { refreshSession, SESSION_CHECK_MS } from '@/lib/auth/session'
import { useSession } from '@/state/session'

describe('refreshSession when the API does not answer', () => {
  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
    useSession.setState({ status: 'unknown', accessToken: null, expiresAt: null })
  })

  it('marks the session unreachable after the check times out, instead of staying unknown', async () => {
    vi.useFakeTimers()
    vi.stubGlobal(
      'fetch',
      (_url: string, init?: RequestInit) =>
        new Promise((_resolve, reject) => {
          init?.signal?.addEventListener('abort', () => reject(new DOMException('The operation was aborted.', 'AbortError')))
        }),
    )
    const pending = refreshSession()
    await vi.advanceTimersByTimeAsync(SESSION_CHECK_MS)
    await expect(pending).resolves.toBe(false)
    expect(useSession.getState().status).toBe('unreachable')
  })
})
