import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

/**
 * The learning-event batcher (lvn-backend ADR-0067): nothing signed out; events wait in localStorage; a batch at 20
 * events or after 10 s; kept while offline or refused for now, sent when the connection returns; sent events and
 * refused ones leave the queue; sign-out drops what was not sent.
 */
const mutate = vi.fn()
vi.mock('@/lib/apollo', () => ({ apolloClient: () => ({ mutate }) }))

const storage = new Map<string, string>()
const listeners = new Map<string, (() => void)[]>()
const on = (type: string, fn: () => void) => listeners.set(type, [...(listeners.get(type) ?? []), fn])
const fire = (type: string) => listeners.get(type)?.forEach((fn) => fn())
let online = true

async function fresh() {
  vi.resetModules()
  const session = await import('@/state/session')
  const learning = await import('@/lib/learning')
  return { session: session.useSession, ...learning }
}

beforeEach(() => {
  vi.useFakeTimers()
  storage.clear()
  listeners.clear()
  online = true
  mutate.mockReset()
  mutate.mockImplementation(async ({ variables }) => ({ data: { trackEvents: { accepted: variables.input.events.length, duplicates: 0, rejected: [], userErrors: [] } } }))
  vi.stubGlobal('localStorage', { getItem: (k: string) => storage.get(k) ?? null, setItem: (k: string, v: string) => void storage.set(k, v) })
  vi.stubGlobal('window', { addEventListener: on })
  vi.stubGlobal('document', { addEventListener: on, visibilityState: 'visible' })
  vi.stubGlobal('navigator', { get onLine() { return online } })
})

afterEach(() => {
  vi.useRealTimers()
  vi.unstubAllGlobals()
})

describe('learning events', () => {
  it('records nothing for a signed-out visitor', async () => {
    const { track, pending } = await fresh()
    track('NOTE_OPENED', { entityType: 'NOTE', entityId: 'n1' })
    expect(pending()).toEqual([])
  })

  it('sends after 10 s, or at once at 20 events, with the device time zone', async () => {
    const { session, track, pending } = await fresh()
    session.getState().set('token', new Date(Date.now() + 900_000).toISOString())
    track('NOTE_OPENED', { entityType: 'NOTE', entityId: 'n1' })
    expect(pending()).toHaveLength(1)
    expect(mutate).not.toHaveBeenCalled()
    await vi.advanceTimersByTimeAsync(10_000)
    expect(mutate).toHaveBeenCalledTimes(1)
    const input = mutate.mock.calls[0]![0].variables.input
    expect(input.events[0]).toMatchObject({ type: 'NOTE_OPENED', entityId: 'n1', platform: 'WEB' })
    expect(input.events[0].id).toMatch(/^[0-9a-f]{8}-[0-9a-f]{4}-7/)
    expect(typeof input.timeZone).toBe('string')
    expect(pending()).toEqual([])
    for (let i = 0; i < 20; i++) track('CARD_VIEWED', { entityId: `c${i}` })
    await vi.advanceTimersByTimeAsync(0)
    expect(mutate).toHaveBeenCalledTimes(2)
    expect(mutate.mock.calls[1]![0].variables.input.events).toHaveLength(20)
  })

  it('keeps events while offline, across a reload, and sends them when the connection returns', async () => {
    const first = await fresh()
    first.session.getState().set('token', new Date(Date.now() + 900_000).toISOString())
    online = false
    first.track('NOTE_OPENED', { entityId: 'n1' })
    first.track('TIME_SPENT', { entityId: 'n1', durationMs: 60_000, metadata: { activity: 'READING' } })
    await vi.advanceTimersByTimeAsync(10_000)
    expect(mutate).not.toHaveBeenCalled()
    // The tab is reloaded while still offline: the events are in localStorage.
    const second = await fresh()
    second.session.getState().set('token', new Date(Date.now() + 900_000).toISOString())
    expect(second.pending().map((e) => e.type)).toEqual(['NOTE_OPENED', 'TIME_SPENT'])
    online = true
    second.track('CARD_VIEWED', { entityId: 'c1' })
    fire('online')
    await vi.advanceTimersByTimeAsync(0)
    expect(mutate.mock.calls.at(-1)![0].variables.input.events.map((e: { type: string }) => e.type)).toEqual(['NOTE_OPENED', 'TIME_SPENT', 'CARD_VIEWED'])
    expect(second.pending()).toEqual([])
  })

  it('keeps a batch the API refused for now, and drops what it refused for good', async () => {
    const { session, track, flush, pending } = await fresh()
    session.getState().set('token', new Date(Date.now() + 900_000).toISOString())
    mutate.mockResolvedValueOnce({ data: { trackEvents: { accepted: 0, duplicates: 0, rejected: [], userErrors: [{ message: 'Too many learning events.', code: 'RATE_LIMITED' }] } } })
    track('NOTE_OPENED', { entityId: 'n1' })
    await flush()
    expect(pending()).toHaveLength(1)
    mutate.mockResolvedValueOnce({ data: { trackEvents: { accepted: 0, duplicates: 0, rejected: [{ index: 0, message: 'bad' }], userErrors: [] } } })
    await flush()
    expect(pending()).toEqual([])
    mutate.mockRejectedValueOnce(new Error('Failed to fetch'))
    track('NOTE_OPENED', { entityId: 'n2' })
    await flush()
    expect(pending()).toHaveLength(1)
  })

  it('drops what was not sent at sign-out', async () => {
    const { session, track, pending } = await fresh()
    session.getState().set('token', new Date(Date.now() + 900_000).toISOString())
    online = false
    track('NOTE_OPENED', { entityId: 'n1' })
    session.getState().clear()
    expect(pending()).toEqual([])
  })
})
