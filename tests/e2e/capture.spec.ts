import { expect, test, type Page } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, page1 } from './support/notes-api'
import { samplePdf } from './support/sample-pdf'

/**
 * Notes from photos and PDFs (lvn-backend ADR-0084) against a mocked API and storage: the tray takes chosen files,
 * makes a large picture smaller in the browser, turns away a PDF over the limit, then puts everything in one new note,
 * has AI make notes of it and opens the note with the AI panel.
 */

const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT, GET', 'access-control-allow-headers': '*' }
const noProblems = { userErrors: [] }
const fileId = (n: number) => `01920000-0000-7000-8000-00000000f0b${n}`

/** A JPEG's width and height, from its start-of-frame marker. */
function jpegSize(bytes: Buffer): { width: number; height: number } | null {
  for (let i = 2; i < bytes.length - 9; ) {
    if (bytes[i] !== 0xff) return null
    const marker = bytes[i + 1]!
    if (marker >= 0xc0 && marker <= 0xc3) return { height: bytes.readUInt16BE(i + 5), width: bytes.readUInt16BE(i + 7) }
    i += 2 + bytes.readUInt16BE(i + 2)
  }
  return null
}

async function mockStorage(page: Page) {
  const puts: { url: string; type: string | undefined; body: Buffer }[] = []
  await page.route('http://storage.test/**', async (route) => {
    const req = route.request()
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: CORS })
    puts.push({ url: req.url(), type: req.headers()['content-type'], body: req.postDataBuffer() ?? Buffer.alloc(0) })
    return route.fulfill({ status: 200, headers: CORS })
  })
  return puts
}

test('photos and PDFs become one note: pictures made smaller, a large PDF turned away, AI asked once', async ({ page }) => {
  const puts = await mockStorage(page)
  let uploads = 0
  const calls = await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    CreateNote: () => ({ createNote: { note: { __typename: 'Note', id: NOTE_ID }, ...noProblems } }),
    CreateNoteUpload: (v) => {
      const n = ++uploads
      const type = (v.input as { mimeType: string }).mimeType
      return { createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: fileId(n), uploadUrl: `http://storage.test/put/${n}`, uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: type }] }, ...noProblems } }
    },
    CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...noProblems } }),
    UpdateNoteDraft: () => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: [], conflictVersion: null, ...noProblems } }),
    RunAiTask: () => ({ runAiTask: { __typename: 'RunAiTaskPayload', artifact: null, ...noProblems } }),
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    AiState: () => ({ aiStatus: { __typename: 'AiStatus', available: true, reason: null }, myAiAllowance: { __typename: 'AiAllowance', usedToday: 0, limitToday: null, resetsAt: new Date(Date.now() + 3_600_000).toISOString() } }),
    NoteAiArtifacts: () => ({ note: { __typename: 'Note', id: NOTE_ID, cards: { __typename: 'CardConnection', edges: [] }, aiArtifacts: [] } }),
  })
  await page.goto('/notes')
  await page.getByRole('button', { name: 'Notes from photos' }).filter({ visible: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Notes from photos and PDFs' })
  await expect(dialog.getByRole('button', { name: 'Make notes' })).toBeDisabled()

  // A 3,000 × 2,000 photo, as a phone's camera makes them.
  await page.evaluate(async () => {
    const canvas = document.createElement('canvas')
    canvas.width = 3000
    canvas.height = 2000
    const ctx = canvas.getContext('2d')!
    ctx.fillStyle = '#16a34a'
    ctx.fillRect(0, 0, 3000, 2000)
    const blob = await new Promise<Blob>((resolve) => canvas.toBlob((b) => resolve(b!), 'image/png'))
    const files = new DataTransfer()
    files.items.add(new File([blob], 'whiteboard.png', { type: 'image/png' }))
    const input = document.querySelector<HTMLInputElement>('[data-testid="capture-input"]')!
    input.files = files.files
    input.dispatchEvent(new Event('change', { bubbles: true }))
  })
  await expect(dialog.getByRole('img', { name: 'Photo 1' })).toBeVisible()
  await dialog.getByTestId('capture-input').setInputFiles([
    { name: 'handout.pdf', mimeType: 'application/pdf', buffer: samplePdf() },
    { name: 'textbook.pdf', mimeType: 'application/pdf', buffer: Buffer.concat([Buffer.from('%PDF-1.7\n'), Buffer.alloc(21 * 1024 ** 2)]) },
  ])
  await expect(dialog.getByRole('alert')).toHaveText('textbook.pdf is 21.0 MB; a PDF can be at most 20 MB.')
  await expect(dialog.getByText('2 of 10')).toBeVisible()

  await dialog.getByRole('button', { name: 'Make notes from 2' }).click()
  await expect(page.getByRole('dialog', { name: 'AI tasks' })).toBeVisible({ timeout: 15_000 })
  await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}$`))

  expect(calls.find((c) => c.op === 'CreateNote')?.variables).toEqual({ input: { title: expect.stringMatching(/^Quick note, /) } })
  expect(puts.map((p) => p.type)).toEqual(['image/jpeg', 'application/pdf'])
  expect(jpegSize(puts[0]!.body)).toEqual({ width: 2048, height: 1365 })
  const ops = (calls.find((c) => c.op === 'UpdateNoteDraft')?.variables.input as { ops: { type: string; content: unknown }[] }).ops
  expect(ops.map((o) => [o.type, o.content])).toEqual([
    ['image', { fileId: fileId(1), alt: '' }],
    ['file', { fileId: fileId(2) }],
  ])
  expect(calls.filter((c) => c.op === 'RunAiTask').map((c) => c.variables)).toEqual([{ input: { noteId: NOTE_ID, task: 'QUICK_NOTE' } }])
})
