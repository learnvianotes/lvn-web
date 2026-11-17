// @vitest-environment happy-dom
import { act, useSyncExternalStore, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import * as docs from '@/graphql/generated/graphql'
import { AdminContent } from '@/features/admin/AdminContent'

;(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const nav = vi.hoisted(() => {
  let current = ''
  const listeners = new Set<() => void>()
  return {
    get: () => current,
    subscribe: (listener: () => void) => {
      listeners.add(listener)
      return () => listeners.delete(listener)
    },
    replace: (url: string) => {
      const next = url.includes('?') ? url.slice(url.indexOf('?') + 1) : ''
      if (next === current) return
      current = next
      listeners.forEach((listener) => listener())
    },
    reset: (search = '') => {
      current = search
      listeners.forEach((listener) => listener())
    },
  }
})

const author = (handle: string, email: string) => ({ id: '01920000-0000-7000-8000-0000000000aa', handle, email })

const note = {
  id: '01920000-0000-7000-8000-000000000001',
  type: 'NOTE' as const,
  title: 'Organic chemistry',
  excerpt: 'Alkenes add across the double bond.',
  author: author('asha', 'asha@example.com'),
  visibility: 'PUBLIC' as const,
  createdAt: '2026-11-01T08:30:00.000Z',
  updatedAt: '2026-11-02T08:30:00.000Z',
  moderation: 'OK',
  deepLink: '/notes/01920000-0000-7000-8000-000000000001',
}

const highlight = {
  id: '01920000-0000-7000-8000-000000000002',
  type: 'HIGHLIGHT' as const,
  title: null,
  excerpt: 'A quoted line from the note',
  author: author('ravi', 'ravi@example.com'),
  visibility: 'SHARED' as const,
  createdAt: '2026-11-03T08:30:00.000Z',
  updatedAt: '2026-11-03T09:30:00.000Z',
  moderation: null,
  deepLink: '/notes/01920000-0000-7000-8000-000000000009',
}

const comment = {
  id: '01920000-0000-7000-8000-000000000003',
  type: 'COMMENT' as const,
  title: null,
  excerpt: 'Second page comment',
  author: author('asha', 'asha@example.com'),
  visibility: 'MEMBERS' as const,
  createdAt: '2026-10-01T08:30:00.000Z',
  updatedAt: '2026-10-01T08:30:00.000Z',
  moderation: 'HIDDEN',
  deepLink: '/notes/01920000-0000-7000-8000-000000000001',
}

const api = vi.hoisted(() => ({
  role: 'PLATFORM_ADMIN' as string | null,
  empty: false,
  counts: [
    { type: 'NOTE' as const, count: 4 },
    { type: 'COMMENT' as const, count: 1 },
  ],
  calls: [] as { doc: unknown; variables: unknown; skip?: boolean }[],
  moderate: vi.fn(),
  refetch: vi.fn(async () => ({})),
}))

vi.mock('next/navigation', () => ({
  useRouter: () => ({ replace: (url: string) => nav.replace(url) }),
  usePathname: () => '/admin/content',
  useSearchParams: () => {
    const search = useSyncExternalStore(nav.subscribe, nav.get, nav.get)
    return new URLSearchParams(search)
  },
}))

vi.mock('next/link', async () => {
  const { createElement: h } = await import('react')
  return { default: ({ href, children, ...rest }: { href: string; children?: ReactNode }) => h('a', { href, ...rest }, children) }
})

vi.mock('@apollo/client/react', () => ({
  useQuery: (doc: unknown, options?: { variables?: { after?: string | null }; skip?: boolean }) => {
    api.calls.push({ doc, variables: options?.variables, skip: options?.skip })
    const idle = { data: undefined, loading: false, error: undefined, refetch: api.refetch }
    if (doc === docs.ViewerDocument) return { data: { viewer: { globalRole: api.role } }, loading: false, error: undefined, refetch: api.refetch }
    if (options?.skip) return idle
    if (doc === docs.AdminContentCountsDocument) return { data: { adminContentCounts: { from: null, to: null, counts: api.counts } }, loading: false, error: undefined, refetch: api.refetch }
    if (doc === docs.AdminContentDocument) {
      const page = api.empty ? { edges: [], pageInfo: { hasNextPage: false, endCursor: null } } : options?.variables?.after ? { edges: [{ cursor: 'c2', node: comment }], pageInfo: { hasNextPage: false, endCursor: null } } : { edges: [{ cursor: 'c1', node: note }, { cursor: 'c2', node: highlight }], pageInfo: { hasNextPage: true, endCursor: 'page-2' } }
      return { data: { adminContent: page }, loading: false, error: undefined, refetch: api.refetch }
    }
    return idle
  },
  useMutation: () => [api.moderate, { loading: false }],
}))

const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!

describe('admin content browser', () => {
  let root: Root | undefined
  let container: HTMLDivElement | undefined

  beforeEach(() => {
    api.role = 'PLATFORM_ADMIN'
    api.empty = false
    api.calls = []
    api.moderate.mockReset().mockResolvedValue({ data: { moderateContent: { ok: true, userErrors: [] } } })
    api.refetch.mockClear()
    nav.reset()
  })

  afterEach(() => {
    if (root) act(() => root!.unmount())
    container?.remove()
    root = undefined
    container = undefined
  })

  async function mount() {
    container = document.createElement('div')
    document.body.appendChild(container)
    root = createRoot(container)
    await act(async () => {
      root!.render(
        <NextIntlClientProvider locale="en" messages={messages} timeZone="UTC">
          <AdminContent />
        </NextIntlClientProvider>,
      )
    })
    return container!
  }

  const last = (doc: unknown) => [...api.calls].reverse().find((call) => call.doc === doc)
  const row = (text: string) => [...container!.querySelectorAll('tbody tr')].find((tr) => tr.textContent?.includes(text))
  const cells = (text: string) => [...(row(text)?.querySelectorAll('td') ?? [])]
  const button = (name: string) => [...container!.querySelectorAll('button')].find((el) => el.textContent === name) as HTMLButtonElement | undefined

  async function typeInto(input: HTMLInputElement, value: string) {
    await act(async () => {
      setter.call(input, value)
      input.dispatchEvent(new Event('input', { bubbles: true }))
      input.dispatchEvent(new Event('change', { bubbles: true }))
    })
  }

  async function choose(select: HTMLSelectElement, value: string) {
    await act(async () => {
      select.value = value
      select.dispatchEvent(new Event('change', { bubbles: true }))
    })
  }

  it('renders counts, the table and the private-note note', async () => {
    const view = await mount()
    expect(view.querySelector('h1')?.textContent).toBe('Content')
    expect(view.textContent).toContain("Private notes aren't shown.")
    const counts = view.querySelector('[aria-label="Counts in this range"]')
    expect(counts?.textContent).toContain('Note')
    expect(counts?.textContent).toContain('4')
    expect(counts?.textContent).toContain('Comment')
    expect(counts?.textContent).toContain('1')

    const noteCells = cells('Organic chemistry')
    expect(noteCells[0]?.textContent).toBe('Note')
    expect(noteCells[1]?.textContent).toContain('Organic chemistry')
    expect(noteCells[2]?.textContent).toContain('@asha')
    expect(noteCells[2]?.textContent).toContain('asha@example.com')
    expect(noteCells[3]?.textContent).toBe('Public')
    expect(noteCells[4]?.textContent).toBe('Public')
    expect(noteCells[5]?.textContent).toContain('2026')
    expect(noteCells[6]?.textContent).toContain('2026')
    expect(noteCells[5]?.textContent).not.toBe(noteCells[6]?.textContent)
    expect(noteCells[7]?.querySelector('a')?.getAttribute('href')).toBe('/notes/01920000-0000-7000-8000-000000000001')
    expect(noteCells[7]?.textContent).toBe('Open')
    expect(noteCells[8]?.textContent).toContain('Hide')

    const quote = cells('A quoted line')
    expect(quote[0]?.textContent).toBe('Highlight')
    expect(quote[1]?.textContent).toContain('A quoted line from the note')
    expect(quote[4]?.textContent).toBe('None')
    expect(quote[8]?.textContent).toBe('No moderation actions')
    expect(last(docs.AdminContentDocument)?.variables).toMatchObject({ first: 20, after: null, filter: null })
    expect(last(docs.AdminContentCountsDocument)?.skip).toBe(false)
  })

  it('keeps type, user, dates and visibility in the URL and on the queries', async () => {
    const view = await mount()
    await choose(view.querySelector('select[name="type"]') as HTMLSelectElement, 'NOTE')
    expect(nav.get()).toBe('type=NOTE')
    expect(last(docs.AdminContentDocument)?.variables).toMatchObject({ filter: { type: 'NOTE' }, after: null, first: 20 })

    await act(async () => nav.reset('after=page-2&type=NOTE'))
    await typeInto(view.querySelector('input[name="user"]') as HTMLInputElement, 'asha')
    expect(nav.get()).toContain('type=NOTE')
    expect(nav.get()).toContain('user=asha')
    expect(nav.get()).not.toContain('after=')
    expect(last(docs.AdminContentDocument)?.variables).toMatchObject({ filter: { type: 'NOTE', handle: 'asha' }, after: null })

    await typeInto(view.querySelector('input[name="user"]') as HTMLInputElement, '01920000-0000-7000-8000-0000000000aa')
    expect(last(docs.AdminContentDocument)?.variables).toMatchObject({ filter: { type: 'NOTE', userId: '01920000-0000-7000-8000-0000000000aa' } })
    expect(JSON.stringify(last(docs.AdminContentDocument)?.variables)).not.toContain('handle')

    await typeInto(view.querySelector('input[name="from"]') as HTMLInputElement, '2026-11-01')
    await typeInto(view.querySelector('input[name="to"]') as HTMLInputElement, '2026-11-17')
    await choose(view.querySelector('select[name="visibility"]') as HTMLSelectElement, 'SHARED')
    const from = new Date('2026-11-01T00:00:00.000+05:30').toISOString()
    const to = new Date('2026-11-17T23:59:59.999+05:30').toISOString()
    expect(nav.get()).toContain('from=2026-11-01')
    expect(nav.get()).toContain('to=2026-11-17')
    expect(nav.get()).toContain('visibility=SHARED')
    expect(last(docs.AdminContentDocument)?.variables).toMatchObject({ filter: { type: 'NOTE', userId: '01920000-0000-7000-8000-0000000000aa', from, to, visibility: 'SHARED' } })
    expect(last(docs.AdminContentCountsDocument)?.variables).toEqual({ from, to })
  })

  it('pages forward with the cursor and can return to the first page', async () => {
    const view = await mount()
    expect(row('Organic chemistry')).toBeTruthy()
    await act(async () => button('Next page')!.click())
    expect(nav.get()).toBe('after=page-2')
    expect(last(docs.AdminContentDocument)?.variables).toMatchObject({ after: 'page-2' })
    expect(row('Second page comment')).toBeTruthy()
    expect(row('Organic chemistry')).toBeFalsy()
    await act(async () => button('First page')!.click())
    expect(nav.get()).toBe('')
    expect(row('Organic chemistry')).toBeTruthy()
    expect(view.textContent).toContain('Next page')
  })

  it('hides a note through moderateContent and shows an empty list', async () => {
    const view = await mount()
    await act(async () => button('Hide')!.click())
    expect(view.querySelector('[role="alert"]')?.textContent).toBe('Write a reason first: the author is told.')
    expect(api.moderate).not.toHaveBeenCalled()

    const reason = view.querySelector('input[placeholder="e.g. Copied from a textbook without permission"]') as HTMLInputElement
    await typeInto(reason, 'Copied from a textbook')
    await act(async () => button('Hide')!.click())
    expect(api.moderate).toHaveBeenCalledWith({
      variables: { input: { entityType: 'NOTE', entityId: note.id, action: 'HIDE', reason: 'Copied from a textbook' } },
    })

    api.empty = true
    await act(async () => {
      root!.render(
        <NextIntlClientProvider locale="en" messages={messages} timeZone="UTC">
          <AdminContent />
        </NextIntlClientProvider>,
      )
    })
    expect(view.textContent).toContain('Nothing matches these filters.')
    expect(view.querySelector('tbody')).toBeNull()
    expect(view.textContent).toContain("Private notes aren't shown.")
  })

  it('does not query content for someone who is not a platform admin', async () => {
    api.role = 'TEACHER'
    const view = await mount()
    expect(view.textContent).toContain('Only platform admins can browse content.')
    expect(view.querySelector('table')).toBeNull()
    expect(last(docs.AdminContentDocument)?.skip).toBe(true)
    expect(last(docs.AdminContentCountsDocument)?.skip).toBe(true)
  })
})
