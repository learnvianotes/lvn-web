import { describe, expect, it, vi } from 'vitest'
import { firebaseAuthUpstream, proxyFirebaseAuth, rewriteFirebaseLocation } from '@/lib/auth/firebase-auth-proxy'
import { siteHeaderRules } from '@/lib/security-headers'

const project = 'learnvia-test'

describe('the Firebase auth helper upstream', () => {
  it('points at that project’s firebaseapp.com host and keeps the query', () => {
    expect(firebaseAuthUpstream(project, ['iframe.js'], '?apiKey=test-key')?.toString()).toBe(
      'https://learnvia-test.firebaseapp.com/__/auth/iframe.js?apiKey=test-key',
    )
    expect(firebaseAuthUpstream(project, ['handler'], '')?.pathname).toBe('/__/auth/handler')
  })

  it('refuses an empty project, the e2e stand-in, and a path that leaves /__/auth', () => {
    expect(firebaseAuthUpstream(undefined, ['iframe'], '')).toBeNull()
    expect(firebaseAuthUpstream('lvn-e2e', ['iframe'], '')).toBeNull()
    expect(firebaseAuthUpstream('Bad_Project', ['iframe'], '')).toBeNull()
    expect(firebaseAuthUpstream(project, ['..', 'etc'], '')).toBeNull()
    expect(firebaseAuthUpstream(project, ['iframe'], '?x=\n')).toBeNull()
  })
})

describe('redirects the helper asks the browser to follow', () => {
  it('keeps Google and rewrites a hop back to firebaseapp.com onto this origin', () => {
    expect(rewriteFirebaseLocation('https://accounts.google.com/o/oauth2/auth?client_id=test', project)).toBe(
      'https://accounts.google.com/o/oauth2/auth?client_id=test',
    )
    expect(rewriteFirebaseLocation(`https://${project}.firebaseapp.com/__/auth/handler?apiKey=test-key`, project)).toBe(
      '/__/auth/handler?apiKey=test-key',
    )
    expect(rewriteFirebaseLocation('/__/auth/handler?apiKey=test-key', project)).toBe('/__/auth/handler?apiKey=test-key')
  })

  it('drops any other host', () => {
    expect(rewriteFirebaseLocation('https://evil.example/__/auth/handler', project)).toBeNull()
    expect(rewriteFirebaseLocation('http://accounts.google.com/o/oauth2/auth', project)).toBeNull()
  })
})

describe('proxying the helper', () => {
  it('does not forward the site cookie, and returns the helper for the sign-in page to frame', async () => {
    const fetchImpl = vi.fn(async () => new Response('<html></html>', { status: 200, headers: { 'content-type': 'text/html', 'set-cookie': 'session=secret' } }))
    const response = await proxyFirebaseAuth({
      projectId: project,
      segments: ['iframe'],
      search: '?apiKey=test-key',
      method: 'GET',
      requestHeaders: new Headers({ cookie: 'lvn_rt=secret', accept: 'text/html' }),
      body: null,
      fetchImpl,
    })
    expect(response.status).toBe(200)
    expect(response.headers.get('content-type')).toContain('text/html')
    expect(response.headers.get('set-cookie')).toBeNull()
    expect(response.headers.get('x-frame-options')).toBe('SAMEORIGIN')
    expect(response.headers.get('content-security-policy')).toContain("frame-ancestors 'self'")
    const invocation = fetchImpl.mock.calls[0] as unknown as [URL, RequestInit] | undefined
    expect(String(invocation?.[0])).toBe('https://learnvia-test.firebaseapp.com/__/auth/iframe?apiKey=test-key')
    expect(new Headers(invocation?.[1]?.headers).get('cookie')).toBeNull()
    expect(invocation?.[1]?.redirect).toBe('manual')
  })

  it('passes a redirect to Google through, and refuses one to anywhere else', async () => {
    const google = vi.fn(async () => new Response(null, { status: 302, headers: { location: 'https://accounts.google.com/o/oauth2/auth' } }))
    const ok = await proxyFirebaseAuth({
      projectId: project,
      segments: ['handler'],
      search: '',
      method: 'GET',
      requestHeaders: new Headers(),
      body: null,
      fetchImpl: google,
    })
    expect(ok.status).toBe(302)
    expect(ok.headers.get('location')).toBe('https://accounts.google.com/o/oauth2/auth')

    const elsewhere = await proxyFirebaseAuth({
      projectId: project,
      segments: ['handler'],
      search: '',
      method: 'GET',
      requestHeaders: new Headers(),
      body: null,
      fetchImpl: async () => new Response(null, { status: 302, headers: { location: 'https://evil.example/' } }),
    })
    expect(elsewhere.status).toBe(502)
    expect(elsewhere.headers.get('location')).toBeNull()
  })

  it('answers 404 for the e2e project so tests never call Firebase', async () => {
    const fetchImpl = vi.fn()
    const response = await proxyFirebaseAuth({
      projectId: 'lvn-e2e',
      segments: ['iframe'],
      search: '',
      method: 'GET',
      requestHeaders: new Headers(),
      body: null,
      fetchImpl,
    })
    expect(response.status).toBe(404)
    expect(fetchImpl).not.toHaveBeenCalled()
  })
})

describe('site headers around the helper', () => {
  const rules = siteHeaderRules({ siteUrl: 'https://beta.learnvianotes.in', storageOrigins: 'https://storage.example', nodeEnv: 'production' })
  const header = (source: string, key: string) => rules.find((rule) => rule.source === source)?.headers.find((item) => item.key === key)?.value

  it('lets the sign-in page frame /__/auth and post to Google, and still refuses other framing', () => {
    const page = header('/:path*', 'Content-Security-Policy') ?? ''
    expect(page).toContain("frame-src 'self' https://*.firebaseapp.com https://accounts.google.com")
    expect(page).toContain("form-action 'self' https://accounts.google.com")
    expect(page).toContain("frame-ancestors 'none'")
    expect(header('/:path*', 'X-Frame-Options')).toBe('DENY')
    expect(rules.findIndex((rule) => rule.source === '/__/auth/:path*')).toBeGreaterThan(rules.findIndex((rule) => rule.source === '/:path*'))
    expect(header('/__/auth/:path*', 'X-Frame-Options')).toBe('SAMEORIGIN')
    expect(header('/__/auth/:path*', 'Content-Security-Policy')).toContain("frame-ancestors 'self'")
    expect(header('/__/auth/:path*', 'Content-Security-Policy')).not.toContain("frame-ancestors 'none'")
  })
})
