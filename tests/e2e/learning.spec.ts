import { expect, test, type Page } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'

/**
 * Learning events from the web (lvn-backend ADR-0067): a note opened and the time it was read go to `trackEvents`;
 * events made while the API cannot be reached wait in the browser, survive a reload, and go out when the connection
 * is back (Phase 6's exit: events survive offline).
 */
const hide = (page: Page) =>
  page.evaluate(() => {
    Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' })
    document.dispatchEvent(new Event('visibilitychange'))
  })
const queued = (page: Page) => page.evaluate(() => (JSON.parse(localStorage.getItem('lvn.learning.queue') ?? '[]') as { type: string }[]).map((e) => e.type))

test('a note read offline is recorded, survives a reload, and goes out when the connection is back', async ({ page }) => {
  let offline = false
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    TrackEvents: (v) => ({ trackEvents: { __typename: 'TrackEventsPayload', accepted: (v.input as { events: unknown[] }).events.length, duplicates: 0, rejected: [], userErrors: [] } }),
  })
  // A mocked API answers even when the browser is offline, so the outage is made here.
  await page.route('**/graphql', async (route) => {
    const op = (route.request().postDataJSON() as { operationName?: string }).operationName
    if (offline && op === 'TrackEvents') return route.abort('internetdisconnected')
    return route.fallback()
  })
  await page.clock.install()
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('Halve the range each step.')).toBeVisible()
  offline = true
  // Half a minute of reading; the batch due after 10 s cannot go.
  await page.clock.runFor(30_000)
  await hide(page)
  await expect.poll(() => queued(page)).toEqual(['NOTE_OPENED', 'TIME_SPENT'])
  expect(calls.filter((c) => c.op === 'TrackEvents').every((c) => c.variables)).toBe(true)

  await page.reload()
  await expect(page.getByText('Halve the range each step.')).toBeVisible()
  await expect.poll(() => queued(page)).toEqual(['NOTE_OPENED', 'TIME_SPENT', 'NOTE_OPENED'])

  offline = false
  await page.evaluate(() => window.dispatchEvent(new Event('online')))
  await expect.poll(() => queued(page)).toEqual([])
  const sent = calls.filter((c) => c.op === 'TrackEvents').at(-1)!.variables.input as { events: { type: string; entityId: string; durationMs?: number; metadata?: { activity: string }; platform: string }[]; timeZone: string }
  expect(sent.events.map((e) => e.type)).toEqual(['NOTE_OPENED', 'TIME_SPENT', 'NOTE_OPENED'])
  expect(sent.events.every((e) => e.entityId === NOTE_ID && e.platform === 'WEB')).toBe(true)
  expect(sent.events[1]!.durationMs).toBeGreaterThanOrEqual(30_000)
  expect(sent.events[1]!.metadata).toEqual({ activity: 'READING' })
  expect(sent.timeZone).toBeTruthy()
})

test('a search left in place is recorded, without its words', async ({ page }) => {
  const calls = await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    Search: () => ({ search: { __typename: 'SearchResults', notes: [], notesCursor: null, people: [], topics: [], groups: [], classrooms: [], resources: [] } }),
    TrackEvents: (v) => ({ trackEvents: { __typename: 'TrackEventsPayload', accepted: (v.input as { events: unknown[] }).events.length, duplicates: 0, rejected: [], userErrors: [] } }),
  })
  await page.clock.install()
  await page.goto('/notes')
  await expect(page.getByText('Start your first note')).toBeVisible()
  await page.getByRole('button', { name: 'Search notes, topics, people, or ask AI' }).click()
  const palette = page.getByRole('dialog', { name: 'Search notes, people, groups and topics' })
  await palette.getByRole('combobox').fill('binary search trees')
  await page.clock.runFor(3_000)
  // The palette is still open: the words were left in place.
  await expect(palette).toBeVisible()
  await page.clock.runFor(12_000)
  await expect.poll(() => calls.filter((c) => c.op === 'TrackEvents').length).toBeGreaterThan(0)
  const events = calls.filter((c) => c.op === 'TrackEvents').flatMap((c) => (c.variables.input as { events: { type: string; metadata: Record<string, unknown> }[] }).events)
  const search = events.find((e) => e.type === 'SEARCH_PERFORMED')!
  expect(search.metadata).toMatchObject({ words: 3 })
  expect(JSON.stringify(events)).not.toContain('binary')
})
