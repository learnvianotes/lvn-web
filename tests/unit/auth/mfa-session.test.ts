import { afterEach, describe, expect, it, vi } from 'vitest'
import { refreshSession, signedOut } from '@/lib/auth/session'
import { useSession } from '@/state/session'

const expires = () => new Date(Date.now() + 900_000).toISOString()

function json(body: unknown): Response {
  return { ok: true, json: async () => body } as Response
}

describe('refreshSession and the admin code', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    signedOut()
    useSession.setState({ status: 'unknown', accessToken: null, expiresAt: null, role: null, mfaPending: false, mfaVerified: false })
  })

  it('keeps the new access token and asks an admin for a code', async () => {
    vi.stubGlobal('fetch', () => json({
      data: {
        refreshSession: {
          mfaRequired: true,
          session: { accessToken: 'admin-token', accessTokenExpiresAt: expires(), user: { globalRole: 'PLATFORM_ADMIN' } },
        },
      },
    }))
    await expect(refreshSession()).resolves.toBe(true)
    expect(useSession.getState().accessToken).toBe('admin-token')
    expect(useSession.getState().mfaPending).toBe(true)
    expect(useSession.getState().role).toBe('PLATFORM_ADMIN')
  })

  it('does not ask anyone else, even when the API says a code is required', async () => {
    vi.stubGlobal('fetch', () => json({
      data: {
        refreshSession: {
          mfaRequired: true,
          session: { accessToken: 'student-token', accessTokenExpiresAt: expires(), user: { globalRole: 'STUDENT' } },
        },
      },
    }))
    await expect(refreshSession()).resolves.toBe(true)
    expect(useSession.getState().accessToken).toBe('student-token')
    expect(useSession.getState().mfaPending).toBe(false)
  })

  it('signs in with the older query when the API has no MFA fields yet', async () => {
    const queries: string[] = []
    vi.stubGlobal('fetch', (_url: string, init?: RequestInit) => {
      const query = (JSON.parse(String(init?.body)) as { query: string }).query
      queries.push(query)
      if (query.includes('mfaRequired')) return json({ errors: [{ message: 'Cannot query field "mfaRequired" on type "AuthPayload".' }] })
      return json({ data: { refreshSession: { session: { accessToken: 'plain-token', accessTokenExpiresAt: expires() } } } })
    })
    await expect(refreshSession()).resolves.toBe(true)
    expect(queries).toHaveLength(2)
    expect(queries[1]).not.toContain('mfaRequired')
    expect(useSession.getState().accessToken).toBe('plain-token')
    expect(useSession.getState().mfaPending).toBe(false)
  })
})
