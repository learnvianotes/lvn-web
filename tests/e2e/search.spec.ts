import { expect, test } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'

/**
 * Search (lvn-backend §11, ADR-0056) on the web: Ctrl/⌘+K from anywhere in the app — notes, people, groups, classes
 * and topics — and the /search page with filters and more results.
 */

const owner = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar' }
const noteHit = (id: string, title: string, snippet = 'Always settle the closest vertex; \uE000heaps\uE001 make it fast.', kind = 'NOTE') => ({
  __typename: 'NoteSearchHit',
  snippet,
  note: { __typename: 'Note', id, title, kind, visibility: 'PUBLIC', viewerAccess: 'READER', publishedAt: new Date().toISOString(), owner },
})
const hit = noteHit(NOTE_ID, "Dijkstra's algorithm")
const topic = { __typename: 'Topic', id: '01920000-0000-7000-8000-00000000e101', title: 'Shortest paths', subject: { __typename: 'Subject', id: '01920000-0000-7000-8000-00000000e201', title: 'Algorithms' } }
const group = { __typename: 'Group', id: '01920000-0000-7000-8000-00000000f101', name: 'Graph theory circle', type: 'COMMUNITY', privacy: 'PUBLIC', memberCount: 12 }
const workspace = { __typename: 'Group', id: '01920000-0000-7000-8000-00000000f102', name: 'Graph visualiser', type: 'PROJECT', privacy: 'PRIVATE', memberCount: 3 }
const classroom = { __typename: 'Classroom', id: '01920000-0000-7000-8000-00000000f201', name: 'Graph algorithms, section B', memberCount: 40 }
const results = (over: Record<string, unknown> = {}) => ({ search: { __typename: 'SearchResults', resources: [], notes: [hit], notesCursor: null, people: [], topics: [topic], groups: [], classrooms: [], ...over } })
const nothing = results({ notes: [], topics: [] })
const answer = (v: Record<string, unknown>) => (String(v.query).startsWith('nothing') ? nothing : results())
const empty = { Organise: () => ({ myFolders: [], myTags: [] }), MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }) }
const PALETTE = 'Search notes, people, groups and topics'

test('Ctrl+K searches as you type, and Enter opens the note', async ({ page }) => {
  const calls = await mockApi(page, { ...empty, Search: answer, NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER' }), cards: page1(cards) } }) })
  await page.goto('/notes')
  await expect(page.getByText('Start your first note')).toBeVisible()
  await page.keyboard.press('Control+k')
  const palette = page.getByRole('dialog', { name: PALETTE })
  await expect(palette).toBeVisible()
  await palette.getByRole('combobox').fill('heap')
  await expect(palette.getByRole('option', { name: /Dijkstra's algorithm/ })).toBeVisible()
  await expect(palette.locator('mark')).toHaveText('heaps')
  expect(calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: 'heap', first: 8 })
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}$`))
})

test('the palette offers groups and classes, and a topic opens its notes', async ({ page }) => {
  const calls = await mockApi(page, { ...empty, Search: (v) => (v.filters ? results({ topics: [] }) : results({ notes: [], groups: [group, workspace], classrooms: [classroom] })) })
  await page.goto('/notes')
  await page.getByRole('button', { name: 'Search or ask Nova' }).click()
  const palette = page.getByRole('dialog', { name: PALETTE })
  await palette.getByRole('combobox').fill('graph')
  await expect(palette.getByRole('option', { name: /Graph theory circle · Group/ })).toBeVisible()
  await expect(palette.getByRole('option', { name: /Graph visualiser · Project workspace/ })).toBeVisible()
  await expect(palette.getByRole('option', { name: /Graph algorithms, section B · Class/ })).toBeVisible()
  await palette.getByRole('option', { name: /Shortest paths/ }).click()
  await expect(page).toHaveURL(/\/search\?topic=01920000-0000-7000-8000-00000000e101&topicTitle=Shortest\+paths$/)
  await expect(page.getByRole('heading', { name: 'Notes, newest first' })).toBeVisible()
  await expect(page.getByRole('link', { name: /Dijkstra's algorithm/ })).toBeVisible()
  expect(calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: '', first: 20, filters: { kinds: null, sources: null, topicId: topic.id } })
  await page.getByRole('button', { name: 'Stop filtering by Shortest paths' }).click()
  await expect(page).toHaveURL(/\/search$/)
  await expect(page.getByText('Type to search your notes')).toBeVisible()
})

test('a group or a class opens from the palette', async ({ page }) => {
  await mockApi(page, { ...empty, Search: () => results({ notes: [], topics: [], groups: [group], classrooms: [classroom] }), Classroom: () => ({ classroom: null }) })
  await page.goto('/notes')
  await expect(page.getByText('Start your first note')).toBeVisible()
  await page.keyboard.press('Control+k')
  const palette = page.getByRole('dialog', { name: PALETTE })
  await palette.getByRole('combobox').fill('graph')
  await palette.getByRole('option', { name: /section B/ }).click()
  await expect(page).toHaveURL(new RegExp(`/classes/${classroom.id}$`))
})

test('the search page lists notes with what matched, and says when nothing did', async ({ page }) => {
  await mockApi(page, { Search: answer })
  await page.goto('/search?q=heap')
  const result = page.getByRole('link', { name: /Dijkstra's algorithm/ })
  await expect(result).toHaveAttribute('href', `/notes/${NOTE_ID}`)
  await expect(result).toContainText('Public · by Ravi Kumar')
  await expect(page.getByRole('button', { name: /Shortest paths/ })).toBeVisible()
  await page.getByRole('textbox').fill('nothing here')
  await expect(page.getByText('Nothing found for “nothing here”.')).toBeVisible()
  await expect(page).toHaveURL(/\/search\?q=nothing\+here$/)
})

test('kind and source chips narrow the notes, and the address keeps them', async ({ page }) => {
  const project = noteHit('01920000-0000-7000-8000-00000000c0de', 'Graph visualiser', 'A tool that draws shortest paths.', 'PROJECT')
  const calls = await mockApi(page, { Search: (v) => results({ notes: (v.filters as { kinds?: string[] } | undefined)?.kinds?.includes('PROJECT') ? [project] : [hit], groups: [group], classrooms: [classroom] }) })
  await page.goto('/search?q=graph')
  const places = page.getByRole('region', { name: 'Groups and classes' })
  await expect(places.getByRole('link', { name: /Graph theory circle/ })).toHaveAttribute('href', `/groups/${group.id}`)
  await expect(places.getByRole('link', { name: /section B/ })).toContainText('Class · 40 members')
  await page.getByRole('button', { name: 'Projects' }).click()
  await expect(page.getByRole('button', { name: 'Projects' })).toHaveAttribute('aria-pressed', 'true')
  await page.getByRole('button', { name: 'Shared with me' }).click()
  await expect(page.getByRole('link', { name: /Graph visualiser/ })).toContainText('Projects')
  await expect(page).toHaveURL(/\/search\?q=graph&kind=PROJECT&from=SHARED$/)
  expect(calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: 'graph', first: 20, filters: { kinds: ['PROJECT'], sources: ['SHARED'], topicId: null } })
  await page.reload()
  await expect(page.getByRole('button', { name: 'Shared with me' })).toHaveAttribute('aria-pressed', 'true')
})

test('More results adds the next notes of the same search', async ({ page }) => {
  const second = noteHit('01920000-0000-7000-8000-00000000c0d2', 'Bellman-Ford', 'Negative edges need Bellman-Ford.')
  const calls = await mockApi(page, { Search: (v) => (v.after ? results({ notes: [second], notesCursor: null }) : results({ notesCursor: 'cursor-2' })) })
  await page.goto('/search?q=paths')
  await expect(page.getByRole('link', { name: /Dijkstra's algorithm/ })).toBeVisible()
  await page.getByRole('button', { name: 'More results' }).click()
  await expect(page.getByRole('link', { name: /Bellman-Ford/ })).toBeVisible()
  await expect(page.getByRole('link', { name: /Dijkstra's algorithm/ })).toBeVisible()
  await expect(page.getByRole('button', { name: 'More results' })).toHaveCount(0)
  expect(calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: 'paths', first: 20, after: 'cursor-2' })
})

test('tabs: All, Notes, Topics, Groups, Users and Resources each ask for their kind, and the address keeps the tab', async ({ page }) => {
  const person = { __typename: 'User', id: '01920000-0000-7000-8000-00000000cccc', displayName: 'Meera Iyer', handle: 'meera', globalRole: 'STUDENT' }
  const resource = { __typename: 'Resource', id: '01920000-0000-7000-8000-00000000d101', type: 'BOOK', title: 'Graph Algorithms', author: 'Sedgewick', host: 'nptel.ac.in', saveCount: 0 }
  const calls = await mockApi(page, { Search: () => results({ people: [person], groups: [group], classrooms: [classroom], resources: [resource] }) })
  await page.goto('/search?q=graph')
  const tabs = page.getByRole('tablist', { name: 'What to search' })
  await expect(tabs.getByRole('tab')).toHaveText(['All', 'Notes', 'Topics', 'Groups', 'Users', 'Resources'])
  await expect(tabs.getByRole('tab', { name: 'All' })).toHaveAttribute('aria-selected', 'true')
  // All: every kind, each section leading to its tab.
  await expect(page.getByRole('region', { name: 'People' }).getByRole('link', { name: /Meera Iyer/ })).toHaveAttribute('href', '/u/meera')
  await expect(page.getByRole('region', { name: 'Resources' }).getByRole('link', { name: /Graph Algorithms/ })).toHaveAttribute('href', `/resources/${resource.id}`)
  await page.getByRole('button', { name: 'See all Groups and classes' }).click()
  await expect(tabs.getByRole('tab', { name: 'Groups' })).toHaveAttribute('aria-selected', 'true')
  await expect(page).toHaveURL(/\/search\?q=graph&tab=groups$/)
  expect(calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: 'graph', first: 20, scopes: ['GROUPS', 'CLASSROOMS'] })
  // Groups: groups and classes only, no note filters.
  const places = page.getByRole('region', { name: 'Groups and classes' })
  await expect(places.getByRole('link', { name: /section B/ })).toBeVisible()
  await expect(page.getByRole('region', { name: 'People' })).toHaveCount(0)
  await expect(page.getByRole('region', { name: 'Notes' })).toHaveCount(0)
  await expect(page.getByRole('group', { name: 'Filters' })).toHaveCount(0)
  for (const [tab, scopes] of [['Users', ['PEOPLE']], ['Resources', ['RESOURCES']], ['Topics', ['TOPICS']], ['Notes', ['NOTES']]] as const) {
    await tabs.getByRole('tab', { name: tab }).click()
    await expect.poll(() => calls.filter((c) => c.op === 'Search').at(-1)?.variables.scopes).toEqual(scopes)
  }
  // Notes keeps the kind and source chips.
  await expect(page.getByRole('group', { name: 'Filters' })).toBeVisible()
  await expect(page.getByRole('link', { name: /Dijkstra's algorithm/ })).toBeVisible()
  await expect(page).toHaveURL(/\/search\?q=graph&tab=notes$/)
  await page.reload()
  await expect(page.getByRole('tablist', { name: 'What to search' }).getByRole('tab', { name: 'Notes' })).toHaveAttribute('aria-selected', 'true')
})

test('a topic from the Topics tab lists its notes in Notes; a tab with nothing found says so', async ({ page }) => {
  const calls = await mockApi(page, { Search: (v) => (String(v.query).startsWith('nothing') ? nothing : results()) })
  await page.goto('/search?tab=topics')
  await expect(page.getByText('Type to search topics; one lists its notes.')).toBeVisible()
  await page.getByRole('textbox').fill('paths')
  await page.getByRole('button', { name: /Shortest paths/ }).click()
  await expect(page.getByRole('tab', { name: 'Notes' })).toHaveAttribute('aria-selected', 'true')
  await expect(page).toHaveURL(/\/search\?tab=notes&topic=01920000-0000-7000-8000-00000000e101&topicTitle=Shortest\+paths$/)
  await expect.poll(() => calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: '', first: 20, scopes: ['NOTES'], filters: { kinds: null, sources: null, topicId: topic.id } })
  await page.getByRole('tab', { name: 'Users' }).click()
  await page.getByRole('textbox').fill('nothing at all')
  await expect(page.getByText('Nothing found for “nothing at all”.')).toBeVisible()
})
