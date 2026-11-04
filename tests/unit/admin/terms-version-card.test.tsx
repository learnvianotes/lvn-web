// @vitest-environment happy-dom
import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import { AdminTermsStatusDocument, type AdminTermsStatusQuery } from '@/graphql/generated/graphql'
import { TERMS_VERSION } from '@/features/legal/documents'
import { TermsVersionCard } from '@/features/admin/AdminTermsVersion'

type Status = AdminTermsStatusQuery['adminTermsStatus']

const api = vi.hoisted(() => ({
  status: null as unknown,
  error: undefined as unknown,
  refetch: vi.fn(async () => ({})),
  update: vi.fn(),
  reset: vi.fn(),
  queried: [] as unknown[],
}))

vi.mock('@apollo/client/react', async () => {
  const docs = await import('@/graphql/generated/graphql')
  return {
    useQuery: (doc: unknown) => {
      api.queried.push(doc)
      return { data: api.status ? { adminTermsStatus: api.status } : undefined, previousData: undefined, error: api.error, loading: false, refetch: api.refetch }
    },
    useMutation: (doc: unknown) => (doc === docs.ResetAdminSettingDocument ? [api.reset, { loading: false }] : [api.update, { loading: false }]),
  }
})

const status = (over: Partial<Status> = {}): Status => ({
  current: '2026-11-03',
  source: 'DEFAULT',
  publishedVersions: ['2026-10-08', '2026-11-03'],
  acceptedCurrent: 42,
  acceptedOlder: null,
  lastChange: null,
  ...over,
})

describe('terms version card (lvn-backend ADR-0103)', () => {
  let root: Root | undefined
  let container: HTMLDivElement | undefined
  const onSaved = vi.fn()

  beforeEach(() => {
    api.status = status()
    api.error = undefined
    api.queried = []
    api.refetch.mockClear()
    api.update.mockReset().mockResolvedValue({ data: { updateAdminSetting: { setting: null, userErrors: [] } } })
    api.reset.mockReset().mockResolvedValue({ data: { resetAdminSetting: { setting: null, userErrors: [] } } })
    onSaved.mockReset()
    // happy-dom's <dialog> may not open modally; the attribute is what the component and the tests rely on.
    if (!HTMLDialogElement.prototype.showModal) HTMLDialogElement.prototype.showModal = function (this: HTMLDialogElement) { this.setAttribute('open', '') }
  })

  afterEach(() => {
    if (root) act(() => root!.unmount())
    container?.remove()
    root = undefined
    container = undefined
  })

  async function mount(overridden = false) {
    container = document.createElement('div')
    document.body.appendChild(container)
    root = createRoot(container)
    await act(async () =>
      root!.render(
        <NextIntlClientProvider locale="en" messages={messages} timeZone="Asia/Kolkata">
          <TermsVersionCard overridden={overridden} onSaved={onSaved} />
        </NextIntlClientProvider>,
      ),
    )
    return container
  }

  const select = () => container!.querySelector('select') as HTMLSelectElement
  const button = (name: string | RegExp) => [...container!.querySelectorAll('button')].find((b) => (typeof name === 'string' ? b.textContent === name : name.test(b.textContent ?? ''))) as HTMLButtonElement | undefined
  const dialog = () => container!.querySelector('dialog') as HTMLDialogElement
  const choose = async (version: string) =>
    act(async () => {
      select().value = version
      select().dispatchEvent(new Event('change', { bubbles: true }))
    })

  it('shows the version in effect, where it comes from, who accepted it and the last change', async () => {
    api.status = status({ source: 'SETTING', acceptedCurrent: 1234, acceptedOlder: null, lastChange: { actorId: '01920000-0000-7000-8000-00000000aaaa', actorDisplayName: 'Asha Admin', at: '2026-11-03T10:00:00.000Z', previous: '2026-10-08' } })
    const view = await mount(true)
    expect(api.queried).toContain(AdminTermsStatusDocument)
    const text = view.textContent ?? ''
    expect(text).toContain('Terms version')
    expect(text).toContain('2026-11-03')
    expect(text).toContain('Saved on this page.')
    expect(text).toContain('Accepted 2026-11-03')
    expect(text).toContain('1,234')
    // k-anonymity: the API sends null below 5.
    expect(text).toContain('Fewer than 5')
    expect(text).toContain('Asha Admin changed it from 2026-10-08')
    expect(view.querySelector('time')?.getAttribute('dateTime')).toBe('2026-11-03T10:00:00.000Z')
    expect(view.querySelector('article')?.getAttribute('aria-labelledby')).toBe('terms-version-title')
  })

  it('offers only versions both the web and the API publish, the one in effect first and selected', async () => {
    api.status = status({ publishedVersions: ['2026-10-08', '2026-11-03', '2027-01-01'] })
    const view = await mount()
    const options = [...select().options].map((o) => o.value)
    expect(options).toEqual(['2026-11-03', '2026-10-08'])
    expect(select().value).toBe('2026-11-03')
    expect(select().selectedOptions[0]?.textContent).toMatch(/^2026-11-03 \(in effect\)/)
    // The select is labelled for screen readers.
    const label = view.querySelector(`label[for="${select().id}"]`)
    expect(label?.textContent).toBe('Version people accept')
    expect(view.textContent).toContain('Allowed by the API but not published by this web build: 2027-01-01')
    expect(button('Switch version')?.disabled).toBe(true)
  })

  it('confirms before switching, saying everyone is asked again, and only saves on confirm', async () => {
    await mount()
    await choose('2026-10-08')
    const go = button('Switch to 2026-10-08')!
    expect(go.disabled).toBe(false)
    await act(async () => go.click())
    expect(api.update).not.toHaveBeenCalled()
    expect(dialog().open).toBe(true)
    expect(dialog().textContent).toContain('Switch the terms to 2026-10-08?')
    expect(dialog().textContent).toContain('Every signed-in person will be asked to accept the Terms, Privacy Policy and content licence again')
    expect(dialog().textContent).toContain('People who accepted 2026-11-03: 42.')

    await act(async () => button('Cancel')!.click())
    expect(api.update).not.toHaveBeenCalled()
    expect(container!.querySelector('dialog')?.textContent ?? '').not.toContain('Every signed-in person')

    await act(async () => button('Switch to 2026-10-08')!.click())
    await act(async () => [...dialog().querySelectorAll('button')].find((b) => b.textContent === 'Switch to 2026-10-08')!.click())
    expect(api.update).toHaveBeenCalledOnce()
    expect(api.update).toHaveBeenCalledWith({ variables: { input: { key: 'terms_version', value: '2026-10-08' } } })
    expect(api.refetch).toHaveBeenCalled()
    expect(onSaved).toHaveBeenCalledOnce()
    expect(container!.textContent).toContain('Switched to 2026-10-08.')
  })

  it('shows the API’s refusal and does not report a save', async () => {
    api.update.mockResolvedValue({ data: { updateAdminSetting: { setting: null, userErrors: [{ code: 'VALIDATION', field: ['input', 'value'], message: '2026-10-08 is not a published terms version.' }] } } })
    await mount()
    await choose('2026-10-08')
    await act(async () => button('Switch to 2026-10-08')!.click())
    await act(async () => [...dialog().querySelectorAll('button')].find((b) => b.textContent === 'Switch to 2026-10-08')!.click())
    expect(onSaved).not.toHaveBeenCalled()
    expect(container!.querySelector('[role="alert"]')?.textContent).toBe('2026-10-08 is not a published terms version.')
  })

  it('resets to the server default only after a confirm, and only when a version is saved here', async () => {
    await mount(false)
    expect(button('Use the server default')).toBeUndefined()
    act(() => root!.unmount())
    container!.remove()

    api.status = status({ source: 'SETTING' })
    await mount(true)
    await act(async () => button('Use the server default')!.click())
    expect(api.reset).not.toHaveBeenCalled()
    expect(dialog().textContent).toContain('If the default is a different version, every signed-in person will be asked to accept')
    await act(async () => button('Use the default')!.click())
    expect(api.reset).toHaveBeenCalledWith({ variables: { key: 'terms_version' } })
    expect(api.update).not.toHaveBeenCalled()
    expect(onSaved).toHaveBeenCalledOnce()
  })

  it('warns when the version in effect has no text in this web build, and makes the admin choose', async () => {
    api.status = status({ current: '2027-01-01', source: 'ENV', publishedVersions: ['2026-10-08', '2026-11-03', '2027-01-01'] })
    const view = await mount()
    expect(view.textContent).toContain(`2027-01-01 is in effect, but this web build has no text for it, so the legal pages show ${TERMS_VERSION}.`)
    expect(view.textContent).toContain('The server’s TERMS_VERSION variable.')
    expect(select().value).toBe('')
    expect(select().options[0]?.disabled).toBe(true)
    expect(button('Switch version')?.disabled).toBe(true)
    await choose('2026-11-03')
    expect(button('Switch to 2026-11-03')?.disabled).toBe(false)
  })

  it('names web versions the API does not allow yet, and says when nothing can be chosen', async () => {
    api.status = status({ current: '2026-11-03', publishedVersions: ['2026-11-03'] })
    let view = await mount()
    expect(view.textContent).toContain('Published on the web but not allowed by the API yet: 2026-10-08. Add it to “Published terms versions” below')
    expect([...select().options].map((o) => o.value)).toEqual(['2026-11-03'])
    act(() => root!.unmount())
    container!.remove()

    api.status = status({ current: '2027-01-01', publishedVersions: ['2027-01-01'] })
    view = await mount()
    expect(view.querySelector('select')).toBeNull()
    expect(view.textContent).toContain('No version is both published on the web and allowed by the API.')
  })

  it('tells a non-admin they cannot change it', async () => {
    const { CombinedGraphQLErrors } = await import('@apollo/client/errors')
    api.status = null
    api.error = new CombinedGraphQLErrors({ errors: [{ message: 'Forbidden', extensions: { code: 'FORBIDDEN' } }] })
    const view = await mount()
    expect(view.textContent).toBe('Only platform admins change the terms version.')
  })
})
