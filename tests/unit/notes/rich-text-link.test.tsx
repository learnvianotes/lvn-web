// @vitest-environment happy-dom
import { act, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { RichDoc } from '@/features/notes/render/RichText'
import type { Doc } from '@/lib/contracts/validation'

vi.mock('next/link', () => ({
  default: ({ href, children }: { href: string; children?: ReactNode }) => <a href={href}>{children}</a>,
}))

const doc = (href: string): Doc =>
  ({
    type: 'doc',
    content: [{ type: 'paragraph', content: [{ type: 'text', text: 'click', marks: [{ type: 'link', attrs: { href } }] }] }],
  }) as Doc

describe('rich text links', () => {
  const roots: Root[] = []
  afterEach(() => {
    act(() => roots.splice(0).forEach((root) => root.unmount()))
  })

  const render = async (href: string) => {
    const el = document.createElement('div')
    document.body.appendChild(el)
    const root = createRoot(el)
    roots.push(root)
    await act(async () => {
      root.render(<RichDoc doc={doc(href)} />)
    })
    return el
  }

  it('renders an https link and leaves a javascript URL as text', async () => {
    const safe = await render('https://example.com/docs')
    expect(safe.querySelector('a')?.getAttribute('href')).toBe('https://example.com/docs')
    expect(safe.querySelector('a')?.getAttribute('rel')).toContain('noopener')

    const unsafe = await render('javascript:alert(1)')
    expect(unsafe.querySelector('a')).toBeNull()
    expect(unsafe.textContent).toContain('click')
  })
})
