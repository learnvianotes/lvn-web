// @vitest-environment happy-dom
import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import { NotificationSettings } from '@/features/settings/NotificationSettings'

;(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true

type Settings = {
  quietStart: string
  quietEnd: string
  timeZone: string
  weeklyDigest: boolean
  productEmails: boolean
  pushAvailable: boolean
  devices: number
  categories: { category: 'FOLLOW'; push: boolean; email: null }[]
}

const base = (): Settings => ({
  quietStart: '22:00',
  quietEnd: '07:00',
  timeZone: 'Asia/Kolkata',
  weeklyDigest: true,
  productEmails: true,
  pushAvailable: false,
  devices: 0,
  categories: [{ category: 'FOLLOW', push: true, email: null }],
})

const api = vi.hoisted(() => ({
  settings: null as unknown,
  inputs: [] as unknown[],
}))

vi.mock('@apollo/client/react', () => ({
  useQuery: () => ({ data: api.settings ? { notificationSettings: api.settings } : undefined, loading: !api.settings, error: undefined, refetch: vi.fn() }),
  useMutation: () => [
    async (options: { variables: { input: unknown }; optimisticResponse?: { updateNotificationSettings: { settings: unknown } } }) => {
      api.inputs.push(options.variables.input)
      const settings = options.optimisticResponse?.updateNotificationSettings.settings
      if (settings) api.settings = settings
      return { data: { updateNotificationSettings: { settings, userErrors: [] } } }
    },
    { loading: false },
  ],
}))

describe('product update emails', () => {
  let root: Root | undefined
  let container: HTMLDivElement | undefined

  beforeEach(() => {
    api.settings = base()
    api.inputs = []
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
        <NextIntlClientProvider locale="en" messages={messages} timeZone="Asia/Kolkata">
          <NotificationSettings />
        </NextIntlClientProvider>,
      )
    })
    return container!
  }

  const box = () => container!.querySelector('input[name="productEmails"]') as HTMLInputElement

  it('is on by default and turns off when the person unchecks it', async () => {
    const view = await mount()
    expect(view.textContent).toContain('Product updates by email')
    expect(view.textContent).toContain('News about LearnViaNotes. Turn this off to stop those emails.')
    expect(box().checked).toBe(true)
    expect(box().getAttribute('aria-labelledby')).toBe('product-emails')

    await act(async () => box().click())
    expect(api.inputs).toEqual([{ productEmails: false }])
    expect(box().checked).toBe(false)
    expect(view.querySelector('[role="status"]')?.textContent).toBe('Saved.')

    await act(async () => box().click())
    expect(api.inputs[1]).toEqual({ productEmails: true })
    expect(box().checked).toBe(true)
  })
})
