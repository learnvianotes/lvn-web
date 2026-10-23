// @vitest-environment happy-dom
import { existsSync, readdirSync } from 'node:fs'
import { join } from 'node:path'
import { act, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import { ADMIN_SECTIONS, AdminNav, activeAdminSection, canSeeAdminNav } from '@/features/admin/AdminNav'

const nav = vi.hoisted(() => ({ pathname: '/admin/ai' }))

vi.mock('next/navigation', () => ({
  usePathname: () => nav.pathname,
}))

vi.mock('next/link', async () => {
  const { createElement: h } = await import('react')
  return {
    default: ({ href, children, onClick, ...rest }: { href: string; children?: ReactNode; onClick?: (e: { preventDefault: () => void }) => void }) =>
      h(
        'a',
        {
          href,
          ...rest,
          onClick: (e: { preventDefault: () => void }) => {
            e.preventDefault()
            onClick?.(e)
          },
        },
        children,
      ),
  }
})

const SECTIONS: [group: string, label: string, href: string][] = [
  ['People', 'Proof of study to review', '/admin/verification'],
  ['People', 'Google sign-in', '/admin/sign-in'],
  ['Content', 'Moderation queue', '/admin/moderation'],
  ['Content', 'Weekly contests', '/admin/contests'],
  ['AI', 'AI providers', '/admin/ai'],
]

/** Pages that live under the admin route, including nested ones. `/admin` itself when it has a page. */
function adminPageRoutes(dir = 'app/(site)/(app)/admin', prefix = '/admin'): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
    const path = join(dir, entry.name)
    if (entry.isDirectory()) return adminPageRoutes(path, `${prefix}/${entry.name}`)
    return entry.name === 'page.tsx' && existsSync(path) ? [prefix] : []
  })
}

function renderNav() {
  const container = document.createElement('div')
  document.body.appendChild(container)
  const root = createRoot(container)
  const draw = () => {
    root.render(
      <NextIntlClientProvider locale="en" messages={messages}>
        <AdminNav />
      </NextIntlClientProvider>,
    )
  }
  return { container, root, draw }
}

describe('admin settings sidebar', () => {
  let root: Root | undefined
  let container: HTMLDivElement | undefined

  beforeEach(() => {
    nav.pathname = '/admin/ai'
  })

  afterEach(() => {
    if (root) act(() => root!.unmount())
    container?.remove()
    root = undefined
    container = undefined
  })

  async function mount() {
    const view = renderNav()
    container = view.container
    root = view.root
    await act(async () => view.draw())
    return view
  }

  it('lists every admin page, grouped, with its address', async () => {
    expect(ADMIN_SECTIONS.map((section) => section.href).sort()).toEqual(adminPageRoutes().sort())
    await mount()
    const aside = container!.querySelector('aside')!
    const links = [...aside.querySelectorAll('a')].map((a) => ({
      group: a.closest('div')?.querySelector('p')?.textContent,
      label: a.textContent,
      href: a.getAttribute('href'),
    }))
    expect(links).toEqual(SECTIONS.map(([group, label, href]) => ({ group, label, href })))
    for (const [group] of SECTIONS) expect(aside.textContent).toContain(group)
  })

  it('marks the open section and nothing else', async () => {
    expect(activeAdminSection('/admin/ai')?.href).toBe('/admin/ai')
    expect(activeAdminSection('/admin/ai/models')?.href).toBe('/admin/ai')
    expect(activeAdminSection('/admin/moderation')?.key).toBe('moderation')
    expect(activeAdminSection('/notes')).toBeUndefined()

    await mount()
    const links = [...container!.querySelector('aside')!.querySelectorAll('a')]
    const current = links.filter((a) => a.getAttribute('aria-current') === 'page')
    expect(current.map((a) => a.getAttribute('href'))).toEqual(['/admin/ai'])
    expect(current[0]?.className).toContain('bg-accent-soft')
    expect(current[0]?.className).toContain('text-accent')
    expect(current[0]?.className).not.toMatch(/purple|violet|indigo|lavender/)
    expect(links.filter((a) => a.getAttribute('href') !== '/admin/ai').every((a) => !a.hasAttribute('aria-current'))).toBe(true)
  })

  it('opens the section list from the mobile control and closes it again', async () => {
    await mount()
    const open = () => [...container!.querySelectorAll('button')].find((b) => b.textContent === 'Admin settings')!
    expect(open().getAttribute('aria-expanded')).toBe('false')
    expect(container!.querySelector('[role="dialog"]')).toBeNull()

    await act(async () => open().click())
    const dialog = container!.querySelector('[role="dialog"]')!
    expect(open().getAttribute('aria-expanded')).toBe('true')
    expect(dialog.getAttribute('aria-label')).toBe('Admin settings')
    expect([...dialog.querySelectorAll('a')].map((a) => a.textContent)).toEqual(SECTIONS.map(([, label]) => label))
    expect(dialog.querySelector('a[href="/admin/ai"]')?.getAttribute('aria-current')).toBe('page')

    const close = dialog.querySelector('#admin-settings-drawer button') as HTMLButtonElement
    await act(async () => close.click())
    expect(container!.querySelector('[role="dialog"]')).toBeNull()
    expect(open().getAttribute('aria-expanded')).toBe('false')

    await act(async () => open().click())
    await act(async () => {
      window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    })
    expect(container!.querySelector('[role="dialog"]')).toBeNull()

    await act(async () => open().click())
    const link = container!.querySelector('[role="dialog"] a[href="/admin/moderation"]') as HTMLAnchorElement
    await act(async () => link.click())
    expect(container!.querySelector('[role="dialog"]')).toBeNull()
  })

  it('is for platform admins', () => {
    expect(canSeeAdminNav('PLATFORM_ADMIN')).toBe(true)
    expect(canSeeAdminNav('STUDENT')).toBe(false)
    expect(canSeeAdminNav('TEACHER')).toBe(false)
    expect(canSeeAdminNav(undefined)).toBe(false)
    expect(canSeeAdminNav(null)).toBe(false)
  })
})
