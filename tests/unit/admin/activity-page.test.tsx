// @vitest-environment happy-dom
import { act, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import * as docs from '@/graphql/generated/graphql'
import { AdminActivity } from '@/features/admin/AdminActivity'

;(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const summary = {
  from: '2026-10-18T08:00:00.000Z',
  to: '2026-11-17T08:00:00.000Z',
  total: 3,
  byAction: [
    { action: 'settings.updated', count: 2 },
    { action: 'mfa.verified', count: 1 },
  ],
  byDay: [
    { day: '2026-11-16T00:00:00.000Z', count: 1 },
    { day: '2026-11-17T00:00:00.000Z', count: 2 },
  ],
}

const firstEntry = {
  id: '01920000-0000-7000-8000-0000000000a1',
  actorId: '01920000-0000-7000-8000-0000000000b1',
  actorEmail: 'admin@example.com',
  action: 'settings.updated',
  targetType: 'AdminSetting',
  targetId: '01920000-0000-7000-8000-0000000000d1',
  details: { key: 'terms_version' },
  ip: '203.0.113.10',
  userAgent: 'TestBrowser',
  createdAt: '2026-11-17T07:30:00.000Z',
}

const secondEntry = { ...firstEntry, id: '01920000-0000-7000-8000-0000000000a2', actorEmail: 'staff@example.com', action: 'mfa.verified', createdAt: '2026-11-17T06:00:00.000Z' }

const api = vi.hoisted(() => ({
  role: 'PLATFORM_ADMIN' as string | null,
  query: vi.fn(),
  calls: [] as { doc: unknown; variables: unknown }[],
}))

const params = vi.hoisted(() => ({ value: 'action=settings.updated' }))

vi.mock('next/navigation', () => ({
  useSearchParams: () => new URLSearchParams(params.value),
  useRouter: () => ({ replace: vi.fn() }),
  usePathname: () => '/admin/activity',
}))

vi.mock('@apollo/client/react', () => ({
  useQuery: (doc: unknown, options?: { variables?: unknown }) => {
    api.calls.push({ doc, variables: options?.variables })
    if (doc === docs.ViewerDocument) return { data: { viewer: { globalRole: api.role } }, loading: false, error: undefined }
    if (doc === docs.AdminActivitySummaryDocument) return { data: { adminActivitySummary: summary }, loading: false, error: undefined }
    if (doc === docs.AdminActivityDocument) return { data: { adminActivity: { entries: [firstEntry], nextCursor: 'cursor-2' } }, loading: false, error: undefined }
    return { data: undefined, loading: false, error: undefined }
  },
  useApolloClient: () => ({ query: api.query }),
}))

function render(node: ReactNode) {
  const container = document.createElement('div')
  document.body.appendChild(container)
  const root = createRoot(container)
  return { container, root, draw: () => root.render(<NextIntlClientProvider locale="en" messages={messages}>{node}</NextIntlClientProvider>) }
}

describe('admin activity page', () => {
  let root: Root | undefined
  let container: HTMLElement | undefined

  beforeEach(() => {
    api.role = 'PLATFORM_ADMIN'
    api.calls = []
    params.value = 'action=settings.updated'
    api.query.mockReset()
    api.query.mockResolvedValue({ data: { adminActivity: { entries: [secondEntry], nextCursor: null } } })
  })

  afterEach(() => {
    if (root) act(() => root!.unmount())
    container?.remove()
    root = undefined
    container = undefined
  })

  it('shows the summary, the day bars and the newest rows for the filters in the URL', async () => {
    const view = render(<AdminActivity />)
    container = view.container
    root = view.root
    await act(async () => view.draw())

    expect(container.querySelector('h1')?.textContent).toBe('Activity')
    expect(container.textContent).toContain('3 events')
    expect(container.querySelector('[data-testid="activity-days"]')?.children.length).toBe(2)
    expect(container.textContent).toContain('settings.updated')
    expect(container.textContent).toContain('mfa.verified')
    const row = [...container.querySelectorAll('tbody tr')].find((tr) => tr.textContent?.includes('admin@example.com'))
    expect(row?.textContent).toContain('settings.updated')
    expect(row?.textContent).toContain('AdminSetting')
    expect(row?.textContent).toContain('203.0.113.10')
    expect(row?.querySelector('time')?.getAttribute('dateTime')).toBe('2026-11-17T07:30:00.000Z')
    expect(row?.querySelector('time')?.textContent).not.toBe('2026-11-17T07:30:00.000Z')

    const details = row?.querySelector('summary') as HTMLElement
    await act(async () => details.click())
    expect(row?.textContent).toContain('terms_version')
    expect(row?.textContent).toContain('TestBrowser')

    const listCall = api.calls.find((call) => call.doc === docs.AdminActivityDocument)
    expect(listCall?.variables).toMatchObject({ filter: { action: 'settings.updated' }, limit: 50 })

    const more = [...container.querySelectorAll('button')].find((button) => button.textContent === 'Load more') as HTMLButtonElement
    await act(async () => {
      more.click()
      await Promise.resolve()
    })
    expect(api.query).toHaveBeenCalledWith(expect.objectContaining({ variables: expect.objectContaining({ cursor: 'cursor-2' }) }))
    expect(container.textContent).toContain('staff@example.com')
  })
})
