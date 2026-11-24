// @vitest-environment happy-dom
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ACCENT_KEY, THEME_KEY, applyAppearance, readAccent, readMode, resolveAppearance, themeBootScript } from '@/lib/theme'
import { useAppearance } from '@/state/theme'

function media(matches: boolean) {
  return vi.fn().mockImplementation((query: string) => ({
    media: query,
    matches,
    onchange: null,
    addListener: () => undefined,
    removeListener: () => undefined,
    addEventListener: () => undefined,
    removeEventListener: () => undefined,
    dispatchEvent: () => false,
  }))
}

describe('theme storage', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    document.documentElement.removeAttribute('data-accent')
    document.documentElement.removeAttribute('data-mode')
    useAppearance.setState({ mode: 'system', accent: 'navy', resolved: 'light' })
    window.matchMedia = media(false)
  })

  it('keeps a saved light or dark mode and treats anything else as system', () => {
    expect(readMode(null)).toBe('system')
    expect(readMode(JSON.stringify('light'))).toBe('light')
    expect(readMode(JSON.stringify('dark'))).toBe('dark')
    expect(readMode(JSON.stringify('system'))).toBe('system')
    expect(readMode('nope')).toBe('system')
    expect(readMode('{')).toBe('system')
    expect(readAccent(null)).toBe('ink')
    expect(readAccent(JSON.stringify('forest'))).toBe('forest')
    expect(readAccent(JSON.stringify('purple'))).toBe('ink')
  })

  it('resolves system from the OS and leaves an explicit mode alone', () => {
    expect(resolveAppearance('system', false)).toBe('light')
    expect(resolveAppearance('system', true)).toBe('dark')
    expect(resolveAppearance('light', true)).toBe('light')
    expect(applyAppearance('dark', 'teal', false)).toBe('dark')
    expect(document.documentElement.dataset).toMatchObject({ theme: 'dark', accent: 'teal', mode: 'dark' })
  })

  it('paints from storage before paint and follows the OS only while mode is system', () => {
    let listener: (() => void) | undefined
    const query = {
      media: '(prefers-color-scheme: dark)',
      matches: false,
      onchange: null,
      addListener: () => undefined,
      removeListener: () => undefined,
      addEventListener: (_type: string, cb: () => void) => {
        listener = cb
      },
      removeEventListener: () => undefined,
      dispatchEvent: () => false,
    }
    window.matchMedia = vi.fn().mockReturnValue(query)
    localStorage.setItem(THEME_KEY, JSON.stringify('system'))
    localStorage.setItem(ACCENT_KEY, JSON.stringify('amber'))
    // The string is the inline head script. Run it as the browser would.
    const run = new Function(themeBootScript())
    run()
    expect(document.documentElement.dataset).toMatchObject({ theme: 'light', accent: 'amber', mode: 'system' })

    query.matches = true
    listener?.()
    expect(document.documentElement.dataset.theme).toBe('dark')
    expect(document.documentElement.dataset.accent).toBe('amber')

    localStorage.setItem(THEME_KEY, JSON.stringify('light'))
    listener?.()
    expect(document.documentElement.dataset.theme).toBe('light')
    expect(document.documentElement.dataset.mode).toBe('light')
  })

  it('persists mode and accent without dropping a previous explicit choice', () => {
    localStorage.setItem(THEME_KEY, JSON.stringify('dark'))
    useAppearance.getState().sync()
    expect(useAppearance.getState()).toMatchObject({ mode: 'dark', accent: 'ink', resolved: 'dark' })

    useAppearance.getState().setAccent('slate')
    useAppearance.getState().setMode('system')
    expect(localStorage.getItem(THEME_KEY)).toBe(JSON.stringify('system'))
    expect(localStorage.getItem(ACCENT_KEY)).toBe(JSON.stringify('slate'))
    expect(document.documentElement.dataset).toMatchObject({ theme: 'light', accent: 'slate', mode: 'system' })
  })
})
