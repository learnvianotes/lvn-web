// @vitest-environment happy-dom
import { act, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { AppearanceControls } from '@/components/theme/AppearanceControls'
import { AppearanceMenu } from '@/components/theme/AppearanceMenu'
import messages from '@/messages/en.json'
import { ACCENT_KEY, THEME_KEY } from '@/lib/theme'
import { useAppearance } from '@/state/theme'

vi.mock('next/link', async () => {
  const { createElement: h } = await import('react')
  return { default: ({ href, children, ...rest }: { href: string; children?: ReactNode }) => h('a', { href, ...rest }, children) }
})

function buttonNamed(host: HTMLElement, name: string) {
  return [...host.querySelectorAll('button')].find((button) => button.textContent?.includes(name) || button.getAttribute('aria-label') === name)
}

describe('appearance picker', () => {
  let root: Root
  let host: HTMLDivElement

  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    document.documentElement.removeAttribute('data-accent')
    document.documentElement.removeAttribute('data-mode')
    useAppearance.setState({ mode: 'system', accent: 'navy', resolved: 'light' })
    window.matchMedia = vi.fn().mockImplementation((query: string) => ({
      media: query,
      matches: false,
      onchange: null,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: () => undefined,
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }))
    host = document.createElement('div')
    document.body.appendChild(host)
    root = createRoot(host)
  })

  afterEach(() => {
    act(() => root.unmount())
    host.remove()
  })

  function render(node: ReactNode) {
    act(() => {
      root.render(
        <NextIntlClientProvider locale="en" messages={messages}>
          {node}
        </NextIntlClientProvider>,
      )
    })
  }

  it('saves the accent and the mode from the settings controls', () => {
    render(<AppearanceControls />)
    act(() => {
      buttonNamed(host, 'Forest')?.click()
      buttonNamed(host, 'Dark')?.click()
    })
    expect(localStorage.getItem(ACCENT_KEY)).toBe(JSON.stringify('forest'))
    expect(localStorage.getItem(THEME_KEY)).toBe(JSON.stringify('dark'))
    expect(document.documentElement.dataset).toMatchObject({ accent: 'forest', theme: 'dark', mode: 'dark' })
    expect(buttonNamed(host, 'Forest')?.getAttribute('aria-checked')).toBe('true')
    expect(buttonNamed(host, 'Dark')?.getAttribute('aria-checked')).toBe('true')
  })

  it('opens Appearance from the header without using the name Menu', () => {
    render(<AppearanceMenu />)
    const opener = buttonNamed(host, 'Appearance')
    expect(opener).toBeTruthy()
    expect(host.textContent).not.toMatch(/Menu/)
    act(() => opener?.click())
    expect(opener?.getAttribute('aria-expanded')).toBe('true')
    expect(host.querySelector('[role="dialog"]')?.getAttribute('aria-label')).toBe('Appearance')
    act(() => buttonNamed(host, 'Teal')?.click())
    expect(document.documentElement.dataset.accent).toBe('teal')
    expect(host.querySelector('[role="dialog"]')).toBeTruthy()
  })
})
