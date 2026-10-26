// @vitest-environment happy-dom
import { act, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { HomeLink } from '@/components/brand/HomeLink'
import { useSession } from '@/state/session'

vi.mock('next/link', async () => {
  const { createElement: h } = await import('react')
  return {
    default: ({ href, children, ...rest }: { href: string; children?: ReactNode }) => h('a', { href, ...rest }, children),
  }
})

describe('HomeLink', () => {
  let root: Root
  let host: HTMLDivElement

  beforeEach(() => {
    useSession.setState({ status: 'unknown', accessToken: null, expiresAt: null })
    host = document.createElement('div')
    document.body.appendChild(host)
    root = createRoot(host)
  })

  afterEach(() => {
    act(() => root.unmount())
    host.remove()
  })

  function render() {
    act(() => {
      root.render(<HomeLink label="LearnViaNotes">LearnViaNotes</HomeLink>)
    })
  }

  it('sends a visitor to the marketing home', () => {
    useSession.getState().clear()
    render()
    expect(host.querySelector('a')?.getAttribute('href')).toBe('/')
  })

  it('sends a signed-in learner to the app home', () => {
    useSession.getState().set('token', new Date(Date.now() + 60_000).toISOString())
    render()
    expect(host.querySelector('a')?.getAttribute('href')).toBe('/home')
    expect(host.querySelector('a')?.getAttribute('aria-label')).toBe('LearnViaNotes')
  })
})
