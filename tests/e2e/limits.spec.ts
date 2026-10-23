import { expect, test, type Route } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'

const PNG = Buffer.from('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360f8cfc0f01f0005000201a1d0f3a50000000049454e44ae426082', 'hex')

/**
 * A plan limit is shown in the API's words where notes, AI and uploads fail, not as a generic failure.
 */

const NOTES = "You've reached your plan's limit for notes."
const STORAGE = "You've reached your plan's limit for storage."
const ASKS = "You've reached your plan's limit for AI asks a day."

test('creating a note shows the plan limit instead of a generic failure', async ({ page }) => {
  await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    CreateNote: () => ({ createNote: { note: null, userErrors: [{ __typename: 'UserError', field: null, message: NOTES, code: 'RATE_LIMITED' }] } }),
  })
  await page.goto('/notes')
  await page.getByRole('button', { name: 'New note' }).first().click()
  await expect(page.getByRole('alert').filter({ hasText: 'limit for notes' })).toHaveText(NOTES)
  await expect(page.getByText('The note could not be created')).toHaveCount(0)
})

test('an upload refused by the plan shows that message', async ({ page }) => {
  await mockApi(page, { NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }) })
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { operationName?: string }
    if (body.operationName !== 'CreateNoteUpload') return route.fallback()
    return route.fulfill({ json: { data: null, errors: [{ message: STORAGE, extensions: { code: 'FORBIDDEN' } }] } })
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  const chooser = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: /^Image/ }).click()
  await (await chooser).setFiles({ name: 'graph.png', mimeType: 'image/png', buffer: PNG })
  await expect(page.getByRole('alert').filter({ hasText: 'limit for storage' })).toHaveText(STORAGE)
  await expect(page.getByText('could not be uploaded', { exact: false })).toHaveCount(0)
})

test('asking AI shows a limit refusal in the API’s words', async ({ page }) => {
  await mockApi(page, {
    AiState: () => ({ aiStatus: { __typename: 'AiStatus', available: true, reason: null }, myAiAllowance: { __typename: 'AiAllowance', usedToday: 1, limitToday: 20, resetsAt: '2026-10-24T00:00:00.000Z' } }),
    MyAiAnswers: () => ({ myAiAnswers: [] }),
    AskAi: () => ({ askAi: { __typename: 'AskAiPayload', answer: null, userErrors: [{ __typename: 'UserError', field: null, message: ASKS, code: 'FORBIDDEN' }] } }),
  })
  await page.goto('/ask')
  await page.getByLabel('Your question', { exact: true }).fill('What is a heap?')
  await page.getByRole('button', { name: 'Ask', exact: true }).click()
  await expect(page.getByRole('alert').filter({ hasText: 'AI asks a day' })).toHaveText(ASKS)
  await expect(page.getByText('Something went wrong')).toHaveCount(0)
})
