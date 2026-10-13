import { expect, test, type Route } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1, p } from './support/notes-api'

/**
 * Flashcard reviews on the web (lvn-backend ADR-0068): a session shows each front, Space shows the back, keys 1–4
 * grade and move on at once; Again brings the card back at the end; a grade that cannot go waits in the browser and
 * goes when the connection is back; a reader adds a note's flashcards to their reviews.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const doc = (text: string) => ({ type: 'doc', content: [p(text)] })
const card = (n: number) => ({ __typename: 'ReviewCard', cardId: `01920000-0000-7000-8000-0000000fc00${n}`, noteId: NOTE_ID, noteTitle: 'Heaps', front: doc(`Front ${n}`), back: doc(`Back ${n}`), state: 'NEW', due: null })
const queue = { __typename: 'ReviewQueue', due: 0, new: 2, doneToday: 0, waiting: 3, cards: [card(1), card(2)] }
const reviewed = (v: Record<string, unknown>) => ({ reviewCard: { __typename: 'ReviewCardPayload', review: { __typename: 'CardReviewResult', cardId: (v.input as { cardId: string }).cardId, due: new Date(Date.now() + 86_400_000).toISOString(), state: 'REVIEW', intervalDays: 1 }, userErrors: [] } })

test('a session: front, Space for the back, keys to grade; Again comes back at the end', async ({ page }) => {
  const calls = await mockApi(page, { ReviewQueue: () => ({ reviewQueue: queue }), ReviewCard: reviewed }, viewerExtras)
  await page.goto('/profile')
  await page.getByRole('link', { name: /Review flashcards/ }).click()
  await expect(page).toHaveURL(/\/review$/)
  const session = page.getByRole('region', { name: 'Review session' })
  await expect(session.getByText('Front 1')).toBeVisible()
  await expect(session.getByText('1 of 2')).toBeVisible()
  await expect(session.getByText('Back 1')).toHaveCount(0)
  await page.keyboard.press('Space')
  await expect(session.getByText('Back 1')).toBeVisible()
  await page.keyboard.press('3')
  await expect(session.getByText('Front 2')).toBeVisible()
  await session.getByRole('button', { name: 'Show the answer' }).click()
  await session.getByRole('button', { name: 'Again' }).click()
  // Again: card 2 is back, last.
  await expect(session.getByText('Front 2')).toBeVisible()
  await expect(session.getByText('3 of 3')).toBeVisible()
  await page.keyboard.press('Space')
  await page.keyboard.press('4')
  await expect(page.getByText('3 cards reviewed.')).toBeVisible()
  await expect(page.getByText('3 more cards wait for the next days.')).toBeVisible()
  await expect.poll(() => calls.filter((c) => c.op === 'ReviewCard').map((c) => (c.variables.input as { rating: string }).rating)).toEqual(['GOOD', 'AGAIN', 'EASY'])
  const ids = calls.filter((c) => c.op === 'ReviewCard').map((c) => (c.variables.input as { clientOpId: string }).clientOpId)
  expect(new Set(ids).size).toBe(3)
})

test('a grade made while the API cannot be reached waits in the browser and goes when the connection is back', async ({ page }) => {
  let offline = true
  const calls = await mockApi(page, { ReviewQueue: () => ({ reviewQueue: { ...queue, cards: [card(1)], waiting: 0 } }), ReviewCard: reviewed }, viewerExtras)
  await page.route('**/graphql', async (route: Route) => {
    const op = (route.request().postDataJSON() as { operationName?: string }).operationName
    if (offline && op === 'ReviewCard') return route.abort('internetdisconnected')
    return route.fallback()
  })
  await page.goto('/review')
  await expect(page.getByText('Front 1')).toBeVisible()
  await page.keyboard.press('Space')
  await page.keyboard.press('3')
  await expect(page.getByText('1 grade waits to be sent.')).toBeVisible()
  expect(await page.evaluate(() => (JSON.parse(localStorage.getItem('lvn.reviews.pending') ?? '[]') as unknown[]).length)).toBe(1)
  offline = false
  await page.evaluate(() => window.dispatchEvent(new Event('online')))
  await expect(page.getByText('1 grade waits to be sent.')).toHaveCount(0)
  expect(await page.evaluate(() => localStorage.getItem('lvn.reviews.pending'))).toBe('[]')
  // The tries cut off never reached the API; the one that went is the grade made offline.
  expect(calls.filter((c) => c.op === 'ReviewCard').map((c) => (c.variables.input as { rating: string }).rating)).toEqual(['GOOD'])
})

test('nothing to review says where cards come from', async ({ page }) => {
  await mockApi(page, { ReviewQueue: () => ({ reviewQueue: { ...queue, cards: [], new: 0, waiting: 0 } }) }, viewerExtras)
  await page.goto('/review')
  await expect(page.getByRole('heading', { name: 'Nothing to review' })).toBeVisible()
})

test('a reader adds a note’s flashcards to their reviews, and can stop', async ({ page }) => {
  let studying = false
  const flash = { __typename: 'Card', id: '01920000-0000-7000-8000-0000000fc0aa', type: 'flashcard', position: 'a3', revision: 1, content: { front: doc('What is a heap?'), back: doc('A tree with the smallest on top.') } }
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER', viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true }, draftRevision: null, publishedAt: new Date().toISOString() }), cards: page1([...cards, flash]) } }),
    NoteStudying: () => ({ note: { __typename: 'Note', id: NOTE_ID, viewerStudying: studying } }),
    StudyNoteCards: () => ((studying = true), { studyNoteCards: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
    StopStudyingNoteCards: () => ((studying = false), { stopStudyingNoteCards: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  }, viewerExtras)
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Study these cards' }).click()
  await expect(page.getByRole('link', { name: 'Studying these cards' })).toHaveAttribute('href', '/review')
  expect(calls.find((c) => c.op === 'StudyNoteCards')!.variables).toEqual({ input: { noteId: NOTE_ID } })
  await page.getByRole('button', { name: 'Stop studying' }).click()
  await expect(page.getByRole('button', { name: 'Study these cards' })).toBeVisible()
})
