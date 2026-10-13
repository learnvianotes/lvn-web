import { expect, test, type Page } from '@playwright/test'
import { cards, meta, mockApi, NOTE_ID, page1 } from './support/notes-api'

/**
 * Voice notes on the web (lvn-backend ADR-0062): recorded in the browser with MediaRecorder from Chromium's fake
 * microphone, listened to, then uploaded as an audio card like a dropped file.
 */
test.use({ launchOptions: { args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] }, permissions: ['microphone'] })

const FILE_ID = '01920000-0000-7000-8000-00000000f0a1'
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT', 'access-control-allow-headers': '*' }

async function mockStorage(page: Page) {
  const puts: { type: string | undefined; size: number }[] = []
  await page.route('http://storage.test/**', async (route) => {
    const req = route.request()
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: CORS })
    puts.push({ type: req.headers()['content-type'], size: req.postDataBuffer()?.length ?? 0 })
    return route.fulfill({ status: 200, headers: CORS })
  })
  return puts
}

test('records a voice note, plays it back, and adds it to the note as an audio card', async ({ page }) => {
  const puts = await mockStorage(page)
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    CreateNoteUpload: (v) => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: FILE_ID, uploadUrl: 'http://storage.test/put/original', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: (v.input as { mimeType: string }).mimeType }] }, userErrors: [] } }),
    CompleteNoteUpload: () => ({ completeUpload: { ok: true, userErrors: [] } }),
    UpdateNoteDraft: (v) => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: ((v.input as { ops?: { id: string }[] }).ops ?? []).map((o) => ({ __typename: 'CardOpResult', id: o.id, status: 'APPLIED', revision: 1, message: null })), conflictVersion: null, userErrors: [] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('Halve the range each step.')).toBeVisible()
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  await page.getByRole('button', { name: /^Record a voice note/ }).click()
  const dialog = page.getByRole('dialog', { name: 'Record a voice note' })
  await dialog.getByRole('button', { name: 'Start recording' }).click()
  await expect(dialog.getByRole('status')).toHaveText(/0:0[1-9]/, { timeout: 5_000 })
  await dialog.getByRole('button', { name: 'Stop' }).click()
  await expect(dialog.getByLabel('Your recording')).toBeVisible()
  await dialog.getByRole('button', { name: 'Add to the note' }).click()
  await expect(dialog).toBeHidden()

  // Uploaded like any audio card, as WebM, then saved as one.
  await expect.poll(() => calls.find((c) => c.op === 'CreateNoteUpload')?.variables, { timeout: 10_000 }).toMatchObject({ input: { mimeType: 'audio/webm', purpose: 'ATTACHMENT', parentId: NOTE_ID, fileName: expect.stringMatching(/^Voice note .*\.webm$/) } })
  await expect.poll(() => puts.length).toBe(1)
  expect(puts[0]!.size).toBeGreaterThan(1000)
  await expect
    .poll(() => calls.filter((c) => c.op === 'UpdateNoteDraft').flatMap((c) => (c.variables.input as { ops?: { type: string; content: unknown }[] }).ops ?? []).find((o) => o.type === 'audio')?.content, { timeout: 10_000 })
    .toEqual({ fileId: FILE_ID })
})
