import type { ErrorEvent } from '@sentry/nextjs'
import { describe, expect, it } from 'vitest'
import { scrubBreadcrumb, scrubEvent, sentryOptions } from '@/lib/observability'

describe('Sentry scrubbing', () => {
  it('sends no personal data and no performance or replay data', () => {
    const options = sentryOptions('https://key@o1.ingest.sentry.io/2', 'production', '0.1.0')
    expect(options).toMatchObject({
      environment: 'production',
      release: '0.1.0',
      dataCollection: {
        userInfo: false,
        cookies: false,
        httpBodies: [],
        urlQueryParams: false,
        genAI: { inputs: false, outputs: false },
        mcp: { inputs: false, outputs: false },
        databaseQueryData: false,
        stackFrameVariables: false,
        frameContextLines: 0,
      },
    })
    expect(options).not.toHaveProperty('sendDefaultPii')
    expect(options).not.toHaveProperty('includeLocalVariables')
    expect(options).not.toHaveProperty('tracesSampleRate')
    expect(options).not.toHaveProperty('replaysSessionSampleRate')
  })

  it('removes emailed tokens, cookies, bodies, headers and the user from an event', () => {
    const event = scrubEvent({
      type: undefined,
      user: { email: 'asha@example.com', ip_address: '1.2.3.4' },
      request: {
        url: 'https://www.learnvianotes.in/reset?token=emailed-secret',
        query_string: 'token=emailed-secret',
        cookies: { lvn_rt: 'cookie-secret' },
        data: { password: 'typed-secret' },
        headers: { cookie: 'lvn_rt=cookie-secret', authorization: 'Bearer header-secret', 'user-agent': 'Firefox' },
      },
      breadcrumbs: [
        { category: 'navigation', data: { from: '/sign-in', to: '/verify?token=emailed-secret' } },
        { category: 'console', message: 'debug asha@example.com' },
        { category: 'fetch', data: { url: 'https://api.learnvianotes.in/graphql?x=1', method: 'POST' } },
      ],
    } as ErrorEvent)
    const text = JSON.stringify(event)
    for (const secret of ['emailed-secret', 'cookie-secret', 'typed-secret', 'header-secret', 'asha@example.com', '1.2.3.4']) expect(text).not.toContain(secret)
    expect(event.request).toEqual({ url: 'https://www.learnvianotes.in/reset', headers: { 'user-agent': 'Firefox' } })
    expect(event.breadcrumbs).toEqual([
      { category: 'navigation', data: { from: '/sign-in', to: '/verify' } },
      { category: 'fetch', data: { url: 'https://api.learnvianotes.in/graphql', method: 'POST' } },
    ])
  })

  it('drops console breadcrumbs and keeps others without their query strings', () => {
    expect(scrubBreadcrumb({ category: 'console', message: 'x' })).toBeNull()
    expect(scrubBreadcrumb({ category: 'ui.click', message: 'button.primary' })).toEqual({ category: 'ui.click', message: 'button.primary' })
  })
})
