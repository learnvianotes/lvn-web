// @vitest-environment happy-dom
import { act, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, describe, expect, it } from 'vitest'
import messages from '@/messages/en.json'
import { CardView } from '@/features/notes/render/CardView'
import { Markdown } from '@/features/notes/render/Markdown'

const LINE = 'Fraction(int n, int d) : num_(n), den_(d) {} friend std::ostream& operator<<(std::ostream& os, const Fraction& f);'

describe('note code blocks scroll sideways', () => {
  const roots: Root[] = []
  afterEach(() => {
    act(() => roots.splice(0).forEach((root) => root.unmount()))
  })

  function render(node: ReactNode) {
    const host = document.createElement('div')
    document.body.appendChild(host)
    const root = createRoot(host)
    roots.push(root)
    act(() => {
      root.render(
        <NextIntlClientProvider locale="en" messages={messages} timeZone="Asia/Kolkata">
          {node}
        </NextIntlClientProvider>,
      )
    })
    return host
  }

  it('keeps a language-labelled code card on one line inside a sideways scroller', () => {
    const host = render(<CardView id="c1" type="code" content={{ language: 'cpp', filename: 'fraction.cpp', code: LINE }} />)
    const section = host.querySelector('section')
    const figure = host.querySelector('figure')
    const pre = host.querySelector('pre')
    const code = host.querySelector('code')
    expect(section?.className).toContain('min-w-0')
    expect(section?.className).toContain('max-w-full')
    expect(figure?.className).not.toContain('overflow-hidden')
    expect(pre?.className).toContain('lvn-code-scroll')
    expect(host.querySelector('figcaption')?.textContent).toBe('fraction.cpp')
    expect(code?.textContent).toBe(LINE)
  })

  it('scrolls an Output fence the same way', () => {
    const host = render(<Markdown source={'```\nOutput: 1/2\n' + LINE + '\n```'} />)
    const pre = host.querySelector('pre')
    expect(pre?.className).toContain('lvn-code-scroll')
    expect(pre?.querySelector('code')?.textContent).toContain('Output: 1/2')
    expect(pre?.querySelector('code')?.textContent).toContain(LINE)
    expect(host.querySelector('div')?.className).toContain('min-w-0')
  })
})
