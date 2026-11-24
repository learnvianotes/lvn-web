// @vitest-environment happy-dom
import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import { ageField, ConfirmAge, useAgeMessage } from '@/components/auth/AgeCheck'

/** The age the sign-up forms ask for (lvn-backend ADR-0104): the check, its words, and "Is this right?". */
describe('the age field', () => {
  it('turns the text typed into whole years, or names what is wrong with it', () => {
    expect(ageField.safeParse('22')).toEqual({ success: true, data: 22 })
    expect(ageField.safeParse('13')).toEqual({ success: true, data: 13 })
    expect(ageField.safeParse('17')).toEqual({ success: true, data: 17 })
    const problem = (text: string) => ageField.safeParse(text).error?.issues[0]?.message
    expect(problem('')).toBe('required')
    expect(problem('17.5')).toBe('whole')
    expect(problem('0')).toBe('range')
    expect(problem('8')).toBe('range')
    expect(problem('12')).toBe('range')
    expect(problem('121')).toBe('range')
  })
})

describe('the age check on screen', () => {
  let root: Root | undefined
  let container: HTMLDivElement | undefined

  beforeEach(() => {
    // happy-dom's <dialog> may not open modally; the attribute is what the component and the tests rely on.
    if (!HTMLDialogElement.prototype.showModal) HTMLDialogElement.prototype.showModal = function (this: HTMLDialogElement) { this.setAttribute('open', '') }
  })

  afterEach(() => {
    if (root) act(() => root!.unmount())
    container?.remove()
    root = undefined
    container = undefined
  })

  async function mount(ui: React.ReactNode) {
    container = document.createElement('div')
    document.body.appendChild(container)
    root = createRoot(container)
    await act(async () =>
      root!.render(
        <NextIntlClientProvider locale="en" messages={messages} timeZone="Asia/Kolkata">
          {ui}
        </NextIntlClientProvider>,
      ),
    )
    return container
  }

  function Messages({ errors }: { errors: ({ type?: string; message?: string } | undefined)[] }) {
    const message = useAgeMessage()
    return <ul>{errors.map((e, i) => <li key={i}>{message(e) ?? '-'}</li>)}</ul>
  }

  it('words each problem, and shows the API’s own message as it is', async () => {
    const view = await mount(
      <Messages errors={[undefined, { type: 'custom', message: 'required' }, { type: 'custom', message: 'whole' }, { type: 'custom', message: 'range' }, { type: 'server', message: 'Enter an age from 1 to 120.' }]} />,
    )
    expect([...view.querySelectorAll('li')].map((li) => li.textContent)).toEqual(['-', 'Enter your age.', 'Enter your age as a whole number.', 'Enter an age from 13 to 120.', 'Enter an age from 1 to 120.'])
    // The form names 13, not the old floors of 8 and 18.
    expect(view.textContent).not.toContain('8')
    expect(view.textContent).not.toContain('18')
  })

  it('asks "Is this right?" with the age typed, and sends nothing until confirmed', async () => {
    const onConfirm = vi.fn()
    const onChange = vi.fn()
    const view = await mount(<ConfirmAge age={17} busy={false} onConfirm={onConfirm} onChange={onChange} />)
    const dialog = view.querySelector('dialog')!
    expect(dialog.hasAttribute('open')).toBe(true)
    expect(dialog.textContent).toContain('Is this right?')
    expect(dialog.querySelector('strong')?.textContent).toBe('17 years old')
    expect(dialog.textContent).toContain('You are 17 years old.')
    const button = (name: string) => [...dialog.querySelectorAll('button')].find((b) => b.textContent === name)!
    await act(async () => button('Change it').click())
    expect(onChange).toHaveBeenCalledTimes(1)
    expect(onConfirm).not.toHaveBeenCalled()
    await act(async () => button('Yes, that’s right').click())
    expect(onConfirm).toHaveBeenCalledTimes(1)
  })

  it('says "1 year", and stays closed with no age', async () => {
    const one = await mount(<ConfirmAge age={1} busy={false} onConfirm={() => {}} onChange={() => {}} />)
    expect(one.textContent).toContain('You are 1 year old.')
    act(() => root!.unmount())
    one.remove()
    const none = await mount(<ConfirmAge age={null} busy={false} onConfirm={() => {}} onChange={() => {}} />)
    expect(none.querySelector('dialog')?.hasAttribute('open')).toBe(false)
  })
})
