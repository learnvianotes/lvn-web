import { expect, test } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'

/** Search (lvn-backend §10.4) on the web: Ctrl/⌘+K from anywhere in the app, and the /search page. */

const hit = { __typename: 'NoteSearchHit', snippet: 'Always settle the closest vertex; heaps make it fast.', note: { __typename: 'Note', id: NOTE_ID, title: "Dijkstra's algorithm", visibility: 'PUBLIC', viewerAccess: 'READER', publishedAt: new Date().toISOString(), owner: { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar' } } }
const topic = { __typename: 'Topic', id: '01920000-0000-7000-8000-00000000e101', title: 'Shortest paths', subject: { __typename: 'Subject', id: '01920000-0000-7000-8000-00000000e201', title: 'Algorithms' } }
const answer = (v: Record<string, unknown>) => ({ search: { __typename: 'SearchResults', notes: String(v.query).startsWith('nothing') ? [] : [hit], topics: String(v.query).startsWith('nothing') ? [] : [topic], people: [] } })
const empty = { Organise: () => ({ myFolders: [], myTags: [] }), MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }) }

test('Ctrl+K searches as you type, and Enter opens the note', async ({ page }) => {
  const calls = await mockApi(page, { ...empty, Search: answer, NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER' }), cards: page1(cards) } }) })
  await page.goto('/notes')
  await expect(page.getByText('Start your first note')).toBeVisible()
  await page.keyboard.press('Control+k')
  const palette = page.getByRole('dialog', { name: 'Search notes, people and topics' })
  await expect(palette).toBeVisible()
  await palette.getByRole('combobox').fill('heap')
  await expect(palette.getByRole('option', { name: /Dijkstra's algorithm/ })).toBeVisible()
  await expect(palette.locator('mark')).toHaveText('heaps')
  expect(calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: 'heap', first: 8 })
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}$`))
})

test('the header button opens search, and a topic searches for its notes', async ({ page }) => {
  const calls = await mockApi(page, { ...empty, Search: answer })
  await page.goto('/notes')
  await page.getByRole('button', { name: 'Search' }).click()
  const palette = page.getByRole('dialog', { name: 'Search notes, people and topics' })
  await palette.getByRole('combobox').fill('short')
  await palette.getByRole('option', { name: /Shortest paths/ }).click()
  await expect(palette.getByRole('combobox')).toHaveValue('Shortest paths')
  await expect.poll(() => calls.filter((c) => c.op === 'Search').at(-1)?.variables).toEqual({ query: 'Shortest paths', first: 8 })
  await palette.getByRole('button', { name: /All results for/ }).click()
  await expect(page).toHaveURL(/\/search\?q=Shortest%20paths$/)
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
  await expect(page).toHaveURL(/\/search\?q=nothing%20here$/)
})
