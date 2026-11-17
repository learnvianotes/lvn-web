// @vitest-environment happy-dom
import { act, type ReactNode } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import * as docs from '@/graphql/generated/graphql'
import { AdminMfaPanel } from '@/features/admin/AdminMfa'
import { AdminShell } from '@/features/admin/AdminNav'
import { useSession } from '@/state/session'

;(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const api = vi.hoisted(() => ({
  role: 'PLATFORM_ADMIN' as string,
  required: true,
  satisfied: false,
  start: vi.fn(),
  verify: vi.fn(),
  onVerified: vi.fn(),
}))

vi.mock('next/navigation', () => ({
  usePathname: () => '/admin/users',
  useRouter: () => ({ replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}))

vi.mock('next/link', async () => {
  const { createElement: h } = await import('react')
  return { default: ({ href, children, ...rest }: { href: string; children?: ReactNode }) => h('a', { href, ...rest }, children) }
})

vi.mock('@/lib/auth/session', () => ({ signedIn: vi.fn() }))

vi.mock('@apollo/client/react', () => ({
  useQuery: (doc: unknown) => {
    if (doc === docs.ViewerDocument) return { data: { viewer: { globalRole: api.role, verified: true } }, loading: false, error: undefined }
    if (doc === docs.MfaStatusDocument) {
      return {
        data: { mfaStatus: { required: api.required, satisfied: api.satisfied, verifiedAt: null, allowedFactors: ['EMAIL_OTP'], factors: [] } },
        loading: false,
        error: undefined,
      }
    }
    return { data: undefined, loading: false, error: undefined }
  },
  useMutation: (doc: unknown) => [doc === docs.VerifyMfaChallengeDocument ? api.verify : api.start, { loading: false }],
  useApolloClient: () => ({ refetchQueries: vi.fn(), query: vi.fn(), readQuery: () => null, writeQuery: vi.fn() }),
}))

const challenge = {
  challengeId: '01920000-0000-7000-8000-0000000000c1',
  factor: 'EMAIL_OTP',
  expiresAt: '2026-11-17T08:10:00.000Z',
  userErrors: [] as { message: string; code: string; retryAfter: number | null; field: null; supportEmail: null }[],
}

function problem(message: string, code: string, retryAfter: number | null = null) {
  return { message, code, retryAfter, field: null, supportEmail: null }
}

async function mount(node: ReactNode) {
  const container = document.createElement('div')
  document.body.appendChild(container)
  const root = createRoot(container)
  await act(async () => {
    root.render(<NextIntlClientProvider locale="en" messages={messages}>{node}</NextIntlClientProvider>)
  })
  await act(async () => {
    await Promise.resolve()
  })
  return { container, root }
}

async function typeCode(container: HTMLElement, value: string) {
  const input = container.querySelector('input') as HTMLInputElement
  await act(async () => {
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set
    setter?.call(input, value)
    input.dispatchEvent(new Event('input', { bubbles: true }))
  })
}

describe('admin email code screen', () => {
  let root: Root | undefined
  let container: HTMLElement | undefined

  beforeEach(() => {
    api.role = 'PLATFORM_ADMIN'
    api.required = true
    api.satisfied = false
    api.onVerified.mockReset()
    api.start.mockReset()
    api.verify.mockReset()
    useSession.setState({ mfaPending: false, mfaVerified: false, role: null, status: 'unknown', accessToken: null, expiresAt: null })
    api.start.mockResolvedValue({ data: { startMfaChallenge: challenge } })
    api.verify.mockResolvedValue({
      data: {
        verifyMfaChallenge: {
          session: { accessToken: 'new-token', accessTokenExpiresAt: '2026-11-17T08:30:00.000Z', user: { globalRole: 'PLATFORM_ADMIN' } },
          userErrors: [],
        },
      },
    })
  })

  afterEach(() => {
    if (root) act(() => root!.unmount())
    container?.remove()
    root = undefined
    container = undefined
  })

  it('sends a code when it opens', async () => {
    const view = await mount(<AdminMfaPanel onVerified={api.onVerified} />)
    container = view.container
    root = view.root
    expect(api.start).toHaveBeenCalledWith({ variables: { factor: 'EMAIL_OTP' } })
    expect(container.textContent).toContain('Check your email')
    expect(container.textContent).toContain('This code expires at')
  })

  it('stores the new access token when the code is accepted', async () => {
    const { signedIn } = await import('@/lib/auth/session')
    const view = await mount(<AdminMfaPanel onVerified={api.onVerified} />)
    container = view.container
    root = view.root
    await typeCode(container, '123456')
    const submit = [...container.querySelectorAll('button')].find((button) => button.textContent === 'Continue') as HTMLButtonElement
    await act(async () => {
      submit.click()
      await Promise.resolve()
    })
    expect(api.verify).toHaveBeenCalledWith({ variables: { challengeId: challenge.challengeId, code: '123456' } })
    expect(signedIn).toHaveBeenCalledWith('new-token', '2026-11-17T08:30:00.000Z')
    expect(api.onVerified).toHaveBeenCalled()
  })

  it('says when the code is wrong', async () => {
    api.verify.mockResolvedValue({ data: { verifyMfaChallenge: { session: null, userErrors: [problem('That code is incorrect.', 'VALIDATION')] } } })
    const view = await mount(<AdminMfaPanel onVerified={api.onVerified} />)
    container = view.container
    root = view.root
    await typeCode(container, '000000')
    const submit = [...container.querySelectorAll('button')].find((button) => button.textContent === 'Continue') as HTMLButtonElement
    await act(async () => {
      submit.click()
      await Promise.resolve()
    })
    expect(container.querySelector('[role="alert"]')?.textContent).toBe('That code is incorrect.')
    expect(api.onVerified).not.toHaveBeenCalled()
  })

  it('holds resend for the retryAfter the API sends back', async () => {
    api.start.mockResolvedValue({ data: { startMfaChallenge: { ...challenge, challengeId: null, expiresAt: null, userErrors: [problem('Too many codes. Try again later.', 'RATE_LIMITED', 90)] } } })
    const view = await mount(<AdminMfaPanel onVerified={api.onVerified} />)
    container = view.container
    root = view.root
    const resend = [...container.querySelectorAll('button')].find((button) => button.textContent?.includes('Resend')) as HTMLButtonElement
    expect(resend.disabled).toBe(true)
    expect(resend.textContent).toContain('90')
    expect(container.querySelector('[role="alert"]')?.textContent).toContain('90')
  })

  it('keeps the code screen away from anyone who is not an admin', async () => {
    api.role = 'STUDENT'
    api.required = true
    api.satisfied = false
    const view = await mount(
      <AdminShell>
        <p>Notes</p>
      </AdminShell>,
    )
    container = view.container
    root = view.root
    expect(container.textContent).toContain('Notes')
    expect(container.textContent).not.toContain('Check your email')
    expect(api.start).not.toHaveBeenCalled()
  })

  it('replaces admin pages until the code is accepted', async () => {
    const view = await mount(
      <AdminShell>
        <p>Secret settings</p>
      </AdminShell>,
    )
    container = view.container
    root = view.root
    expect(container.textContent).toContain('Check your email')
    expect(container.textContent).not.toContain('Secret settings')
    expect(api.start).toHaveBeenCalled()
  })
})
