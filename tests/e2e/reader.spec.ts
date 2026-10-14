import { expect, test, type Page } from '@playwright/test'
import { NOTE_ID, meta, mockApi, p, page1 } from './support/notes-api'
import { PDF_TEXT, samplePdf } from './support/sample-pdf'

/**
 * The PDF reader (lvn-backend ADR-0040) against a mocked API and a real PDF: reading, highlighting, adding passages
 * and snipped areas to the note with their page, page chips back into the PDF, and readers starting notes of their
 * own. On phones the note is a sheet over the PDF.
 */

const PDF_ID = '01920000-0000-7000-8000-00000000f0a1'
const FILE_CARD = '01920000-0000-7000-8000-00000000c0a1'
const PIC_ID = '01920000-0000-7000-8000-00000000f0a2'
const PDF = samplePdf()
const PNG = Buffer.from('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360f8cfc0f01f0005000201a1d0f3a50000000049454e44ae426082', 'hex')
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT, GET', 'access-control-allow-headers': '*', 'access-control-expose-headers': 'Accept-Ranges, Content-Range, Content-Length' }
const noProblems = { userErrors: [] }
const READER_URL = `/notes/${NOTE_ID}/read/${PDF_ID}`

const media = (id: string, fileName: string, mimeType: string, size: number) => ({ __typename: 'MediaFile', id, url: `http://storage.test/get/${fileName}`, expiresAt: new Date(Date.now() + 3_600_000).toISOString(), mimeType, fileName, sizeBytes: size, width: null, height: null, durationMs: null, pageCount: null, thumbUrl: null, mediumUrl: null, largeUrl: null, posterUrl: null, playbackUrl: null })
const pdfFile = media(PDF_ID, 'Biology chapter 3.pdf', 'application/pdf', PDF.length)
const fileCard = { __typename: 'Card', id: FILE_CARD, type: 'file', position: 'a0', revision: 1, content: { fileId: PDF_ID }, media: pdfFile }

type Highlight = { id: string; fileId: string; page: number; kind: string; color: string; rects: number[][]; quote: string | null; comment: string | null; cardId: string | null }

/** Storage: the PDF, and PUTs of snipped pictures. */
async function mockStorage(page: Page) {
  const puts: { url: string; type: string | undefined; size: number }[] = []
  await page.route('http://storage.test/**', async (route) => {
    const req = route.request()
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: CORS })
    if (req.method() === 'PUT') {
      puts.push({ url: req.url(), type: req.headers()['content-type'], size: req.postDataBuffer()?.length ?? 0 })
      return route.fulfill({ status: 200, headers: CORS })
    }
    if (req.url().endsWith('.pdf')) return route.fulfill({ status: 200, headers: { ...CORS, 'content-type': 'application/pdf' }, body: PDF })
    return route.fulfill({ status: 200, headers: { ...CORS, 'content-type': 'image/png' }, body: PNG })
  })
  return puts
}

/** The API of a note with a PDF, highlights kept in memory. */
async function mockReader(page: Page, opts: { reader?: boolean; cards?: unknown[] } = {}) {
  const highlights: Highlight[] = []
  let n = 0
  const calls = await mockApi(page, {
    NoteToEdit: () => ({
      note: {
        ...meta(
          opts.reader
            ? { viewerAccess: 'READER', owner: { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar', handle: 'ravi' }, viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true } }
            : { title: 'Biology' },
        ),
        cards: page1(opts.cards ?? [fileCard]),
      },
    }),
    NoteFile: () => ({ noteFile: pdfFile }),
    NoteHighlights: () => ({ note: { __typename: 'Note', id: NOTE_ID, highlights: highlights.map((h) => ({ __typename: 'PdfHighlight', ...h })) } }),
    AddPdfHighlight: (v) => {
      const input = v.input as Omit<Highlight, 'id'> & { noteId: string }
      const made: Highlight = { id: `01920000-0000-7000-8000-0000000e${String(++n).padStart(4, '0')}`, fileId: input.fileId, page: input.page, kind: input.kind, color: input.color ?? 'YELLOW', rects: input.rects, quote: input.quote ?? null, comment: null, cardId: input.cardId ?? null }
      highlights.push(made)
      return { addPdfHighlight: { highlight: { __typename: 'PdfHighlight', ...made }, ...noProblems } }
    },
    UpdatePdfHighlight: (v) => {
      const input = v.input as { highlightId: string; color?: string; comment?: string; cardId?: string | null }
      const h = highlights.find((x) => x.id === input.highlightId)!
      if (input.color) h.color = input.color
      if (input.comment !== undefined) h.comment = input.comment.trim() || null
      if (input.cardId !== undefined) h.cardId = input.cardId
      return { updatePdfHighlight: { highlight: { __typename: 'PdfHighlight', ...h }, ...noProblems } }
    },
    RemovePdfHighlight: (v) => {
      highlights.splice(highlights.findIndex((x) => x.id === v.highlightId), 1)
      return { removePdfHighlight: { ok: true, ...noProblems } }
    },
    UpdateNoteDraft: (v) => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta({ title: 'Biology' }), results: ((v.input as { ops?: { id: string }[] }).ops ?? []).map((o) => ({ __typename: 'CardOpResult', id: o.id, status: 'APPLIED', revision: 1, message: null })), conflictVersion: null, ...noProblems } }),
    CreateNoteUpload: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: PIC_ID, uploadUrl: 'http://storage.test/put/snip', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: 'image/png' }] }, ...noProblems } }),
    CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...noProblems } }),
    StudyPdf: () => ({ studyPdf: { note: { __typename: 'Note', id: '01920000-0000-7000-8000-00000000a0ff' }, ...noProblems } }),
    NotePdfConversion: () => ({ note: { __typename: 'Note', id: NOTE_ID, pdfConversion: null } }),
  })
  return { calls, highlights }
}

const isPhone = () => test.info().project.name === 'phone'

/** Selects the words of one line of the PDF, as a reader dragging over them would. */
async function select(page: Page, text: string) {
  await page.evaluate((words) => {
    const span = [...document.querySelectorAll('.textLayer span')].find((s) => s.textContent === words)
    if (!span) throw new Error(`no text "${words}"`)
    const range = document.createRange()
    range.selectNodeContents(span)
    const sel = document.getSelection()!
    sel.removeAllRanges()
    sel.addRange(range)
  }, text)
}

const savedOps = (calls: { op: string; variables: Record<string, unknown> }[]) => calls.filter((c) => c.op === 'UpdateNoteDraft').flatMap((c) => (c.variables.input as { ops: { kind: string; type?: string; content?: Record<string, unknown> }[] }).ops)

test('a PDF opens beside its note with pages, contents and find', async ({ page }) => {
  await mockStorage(page)
  await mockReader(page)
  await page.goto(READER_URL)
  const reader = page.getByTestId('pdf-reader')
  await expect(reader.getByRole('heading', { name: 'Biology' })).toBeVisible()
  await expect(reader.locator('header').getByText('Biology chapter 3.pdf')).toBeVisible()
  await expect(page.locator('.textLayer').getByText(PDF_TEXT.page1[1]!)).toBeAttached({ timeout: 15_000 })
  await expect(reader.getByText('of 2')).toBeVisible()

  if (isPhone()) await reader.getByRole('button', { name: 'Show notes' }).click()
  await reader.getByRole('tab', { name: 'Contents' }).click()
  await reader.getByRole('button', { name: 'Respiration' }).click()
  await expect(reader.getByLabel('Page', { exact: true })).toHaveValue('2')

  await reader.getByRole('button', { name: 'Find in the PDF' }).click()
  await reader.getByRole('searchbox', { name: 'Find in the PDF' }).fill('energy')
  // Found from the page being read (page 2) on: its match first.
  await expect(reader.getByRole('search').getByRole('status')).toHaveText('2 of 2')
  await reader.getByRole('button', { name: 'Next match' }).click()
  await expect(reader.getByRole('search').getByRole('status')).toHaveText('1 of 2')
})

test('a reading link that has expired is renewed, and the PDF opens without a reload (lvn-backend ADR-0090)', async ({ page }) => {
  // Read URLs live 15 minutes: storage refuses the old one, the reader asks the API again and carries on.
  const signed = (sig: string) => `http://storage.test/get/bio.pdf?X-Amz-Expires=900&X-Amz-Signature=${sig}`
  const fetched: string[] = []
  await page.route('http://storage.test/**', async (route) => {
    const req = route.request()
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: CORS })
    fetched.push(req.url())
    if (req.url().endsWith('=old')) return route.fulfill({ status: 403, headers: CORS, body: '<Error><Code>AccessDenied</Code><Message>Request has expired</Message></Error>' })
    return route.fulfill({ status: 200, headers: { ...CORS, 'content-type': 'application/pdf' }, body: PDF })
  })
  let asked = 0
  await mockApi(page, {
    // The card and noteFile are one file in Apollo's cache: both carry the link that has expired, as the API's would.
    NoteToEdit: () => ({ note: { ...meta({ title: 'Biology' }), cards: page1([{ ...fileCard, media: { ...pdfFile, url: signed('old') } }]) } }),
    NoteFile: () => ({ noteFile: { ...pdfFile, url: signed(++asked === 1 ? 'old' : 'new') } }),
    NoteHighlights: () => ({ note: { __typename: 'Note', id: NOTE_ID, highlights: [] } }),
  })
  await page.goto(READER_URL)
  await expect(page.locator('.textLayer').getByText(PDF_TEXT.page1[1]!)).toBeAttached({ timeout: 15_000 })
  expect(asked).toBe(2)
  // The refused link, then the renewed one: the document was not loaded a second time.
  expect(fetched.map((u) => u.split('=').pop())).toEqual(['old', 'new'])
})

test('selected words become a highlight, with a colour and a comment, and can be removed', async ({ page }) => {
  await mockStorage(page)
  const { calls, highlights } = await mockReader(page)
  await page.goto(READER_URL)
  await expect(page.locator('.textLayer').getByText(PDF_TEXT.page1[1]!)).toBeAttached({ timeout: 15_000 })

  await select(page, PDF_TEXT.page1[1]!)
  await page.getByRole('dialog', { name: 'Selected words' }).getByRole('button', { name: 'Highlight in green' }).click()
  await expect(page.locator('.lvn-mark-highlight[data-color="GREEN"]')).toHaveCount(1)
  const added = calls.find((c) => c.op === 'AddPdfHighlight')!.variables.input as { rects: number[][] }
  expect(added).toMatchObject({ noteId: NOTE_ID, fileId: PDF_ID, page: 1, kind: 'TEXT', color: 'GREEN', quote: PDF_TEXT.page1[1] })
  expect(added.rects).toHaveLength(1)
  for (const v of added.rects[0]!) expect(v).toBeGreaterThanOrEqual(0)

  // Clicking the highlight opens it: another colour, a comment, then away.
  const box = (await page.locator('.lvn-mark-highlight').boundingBox())!
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2)
  const card = page.getByRole('dialog', { name: 'Highlight' })
  await card.getByRole('button', { name: 'Highlight in pink' }).click()
  await expect(page.locator('.lvn-mark-highlight[data-color="PINK"]')).toHaveCount(1)
  await card.getByPlaceholder('Add a thought about this…').fill('Exam question!')
  await card.getByRole('button', { name: 'Save comment' }).click()
  await expect.poll(() => highlights[0]?.comment).toBe('Exam question!')
  await card.getByRole('button', { name: 'Close' }).click()

  // The Highlights list has it; choosing it goes back to it (and, on phones, out of the sheet).
  if (isPhone()) await page.getByRole('button', { name: 'Show notes' }).click()
  await page.getByRole('tab', { name: 'Highlights' }).click()
  await page.getByRole('button', { name: /Exam question!/ }).click()
  const again = (await page.locator('.lvn-mark-highlight').boundingBox())!
  await page.mouse.click(again.x + again.width / 2, again.y + again.height / 2)
  await page.getByRole('dialog', { name: 'Highlight' }).getByRole('button', { name: 'Remove highlight' }).click()
  await expect(page.locator('.lvn-mark-highlight')).toHaveCount(0)
  expect(highlights).toHaveLength(0)
})

test('a passage added to the note keeps its page, and its chip brings the PDF back to it', async ({ page }) => {
  await mockStorage(page)
  const { calls } = await mockReader(page)
  await page.goto(READER_URL)
  await expect(page.locator('.textLayer').getByText(PDF_TEXT.page1[2]!)).toBeAttached({ timeout: 15_000 })

  await select(page, PDF_TEXT.page1[2]!)
  await page.getByRole('dialog', { name: 'Selected words' }).getByRole('button', { name: 'Add to notes' }).click()
  if (isPhone()) await page.getByRole('status').getByRole('button', { name: 'Show' }).click()
  const notes = page.getByRole('textbox', { name: 'Note content' })
  await expect(notes.getByText(PDF_TEXT.page1[2]!)).toBeVisible()
  await expect(page.locator('.lvn-anchor-chip')).toHaveText('↗ p. 1')
  // The passage is marked in the PDF as part of the notes.
  await expect(page.locator('.lvn-mark-anchor')).toHaveCount(1)

  await expect
    .poll(() => savedOps(calls).find((o) => o.type === 'quote')?.content, { timeout: 10_000 })
    .toMatchObject({ doc: { type: 'doc', content: [p(PDF_TEXT.page1[2]!)] }, anchor: { fileId: PDF_ID, page: 1, quote: PDF_TEXT.page1[2] } })

  await page.locator('.lvn-anchor-chip').click()
  await expect(page.locator('.lvn-mark-flash').first()).toBeAttached()
})

test('a snipped area becomes a picture card with its page', async ({ page }) => {
  await mockStorage(page)
  const { calls } = await mockReader(page)
  await page.goto(READER_URL)
  await expect(page.locator('.textLayer').getByText(PDF_TEXT.page1[0]!)).toBeAttached({ timeout: 15_000 })

  await page.getByRole('button', { name: 'Snip an area' }).click()
  const surface = (await page.locator('.page[data-page-number="1"] .textLayer').boundingBox())!
  await page.mouse.move(surface.x + surface.width * 0.1, surface.y + surface.height * 0.05)
  await page.mouse.down()
  await page.mouse.move(surface.x + surface.width * 0.6, surface.y + surface.height * 0.2, { steps: 5 })
  await page.mouse.up()
  await page.getByRole('dialog', { name: 'Snipped area' }).getByRole('button', { name: 'Add to notes' }).click()

  await expect
    .poll(() => savedOps(calls).filter((o) => o.type === 'image').at(-1)?.content, { timeout: 15_000 })
    .toMatchObject({ fileId: PIC_ID, alt: 'Page 1 of Biology chapter 3.pdf', anchor: { fileId: PDF_ID, page: 1 } })
  const anchor = savedOps(calls).filter((o) => o.type === 'image').at(-1)!.content!.anchor as { rects: number[][] }
  expect(anchor.rects[0]![0]).toBeCloseTo(0.1, 1)
  expect(anchor.rects[0]![2]).toBeCloseTo(0.6, 1)
  expect(calls.find((c) => c.op === 'CreateNoteUpload')?.variables).toMatchObject({ input: { mimeType: 'image/png', purpose: 'ATTACHMENT', parentId: NOTE_ID } })
})

test('a reader reads the PDF beside the published cards and can start notes of their own', async ({ page }) => {
  await mockStorage(page)
  const quote = { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c0a2', type: 'quote', position: 'a1', revision: 1, content: { doc: { type: 'doc', content: [p('Chlorophyll is green')] }, anchor: { fileId: PDF_ID, page: 2, rects: [[0.1, 0.1, 0.5, 0.12]] } }, media: null }
  const { calls } = await mockReader(page, { reader: true, cards: [fileCard, quote] })
  await page.goto(READER_URL)
  await expect(page.locator('.textLayer').getByText(PDF_TEXT.page1[1]!)).toBeAttached({ timeout: 15_000 })
  // No highlighting for readers: copying and their own notes only.
  await select(page, PDF_TEXT.page1[1]!)
  const actions = page.getByRole('dialog', { name: 'Selected words' })
  await expect(actions.getByRole('button', { name: 'Copy' })).toBeVisible()
  await expect(actions.getByRole('button', { name: 'Highlight in yellow' })).toHaveCount(0)
  expect(calls.some((c) => c.op === 'NoteHighlights')).toBe(false)
  await page.keyboard.press('Escape')
  await expect(actions).toHaveCount(0)

  if (isPhone()) await page.getByRole('button', { name: 'Show notes' }).click()
  await expect(page.getByText('Chlorophyll is green')).toBeVisible()
  await page.getByRole('button', { name: '↗ p. 2' }).click()
  await expect(page.getByLabel('Page', { exact: true })).toHaveValue('2')

  if (isPhone()) await page.getByRole('button', { name: 'Show notes' }).click()
  await page.getByRole('button', { name: 'Start my notes on this PDF' }).click()
  await expect(page).toHaveURL(new RegExp(`/notes/01920000-0000-7000-8000-00000000a0ff/read/${PDF_ID}$`))
  expect(calls.find((c) => c.op === 'StudyPdf')?.variables).toEqual({ noteId: NOTE_ID, fileId: PDF_ID })
})

test('Read a PDF makes a note with the PDF and opens it in the reader', async ({ page }) => {
  const puts = await mockStorage(page)
  const calls = await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    CreateNote: () => ({ createNote: { note: { __typename: 'Note', id: NOTE_ID }, ...noProblems } }),
    CreateNoteUpload: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: PDF_ID, uploadUrl: 'http://storage.test/put/pdf', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: 'application/pdf' }] }, ...noProblems } }),
    CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...noProblems } }),
    UpdateNoteDraft: () => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: [], conflictVersion: null, ...noProblems } }),
    NoteToEdit: () => ({ note: { ...meta({ title: 'Biology chapter 3' }), cards: page1([fileCard]) } }),
    NoteFile: () => ({ noteFile: pdfFile }),
    NoteHighlights: () => ({ note: { __typename: 'Note', id: NOTE_ID, highlights: [] } }),
  })
  await page.goto('/notes')
  await page.getByTestId('read-pdf-input').setInputFiles({ name: 'Biology_chapter_3.pdf', mimeType: 'application/pdf', buffer: PDF })
  await expect(page).toHaveURL(new RegExp(`${READER_URL}$`), { timeout: 15_000 })
  expect(calls.find((c) => c.op === 'CreateNote')?.variables).toEqual({ input: { title: 'Biology chapter 3' } })
  expect(puts).toEqual([{ url: 'http://storage.test/put/pdf', type: 'application/pdf', size: PDF.length }])
  expect(savedOps(calls)).toEqual([expect.objectContaining({ kind: 'UPSERT', type: 'file', content: { fileId: PDF_ID } })])
  await expect(page.locator('.textLayer').getByText(PDF_TEXT.page1[0]!)).toBeAttached({ timeout: 15_000 })
})

test('a PDF card in a note opens the reader', async ({ page }) => {
  await mockStorage(page)
  await mockReader(page)
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('link', { name: /Read & make notes/ }).click()
  await expect(page).toHaveURL(new RegExp(`${READER_URL}$`))
  await expect(page.getByTestId('pdf-reader')).toBeVisible()
})

test('converting a PDF makes a note that opens beside it, shows its progress and gets its cards', async ({ page }) => {
  await mockStorage(page)
  const NEW = '01920000-0000-7000-8000-00000000a0cc'
  const conversion = (status: string, extra: object = {}) => ({ __typename: 'PdfConversion', id: '01920000-0000-7000-8000-0000000c0001', status, progress: status === 'DONE' ? 100 : 15, pages: 1, scannedPages: 0, cards: null, aiPages: null, aiRejected: null, error: null, ...extra })
  let checks = 0
  const converted = [
    fileCard,
    { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c0b1', type: 'heading', position: 'a1', revision: 1, content: { level: 1, content: [{ type: 'text', text: 'Photosynthesis' }], anchor: { fileId: PDF_ID, page: 1, rects: [[0.12, 0.08, 0.4, 0.11]] } }, media: null },
    { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c0b2', type: 'text', position: 'a2', revision: 1, content: { doc: { type: 'doc', content: [p(PDF_TEXT.page1[1]!)] }, anchor: { fileId: PDF_ID, page: 1, rects: [[0.12, 0.12, 0.6, 0.14]] } }, media: null },
  ]
  const calls = await mockApi(page, {
    NoteToEdit: (v) => ({ note: { ...meta({ id: v.id, title: v.id === NEW ? 'Biology chapter 3' : 'Biology' }), cards: page1(v.id === NEW && checks > 2 ? converted : [fileCard]) } }),
    NoteFile: () => ({ noteFile: pdfFile }),
    NoteHighlights: (v) => ({ note: { __typename: 'Note', id: v.id, highlights: [] } }),
    PdfPagesThisMonth: () => ({ pdfPagesThisMonth: { __typename: 'PdfPagesUsage', used: 3, limit: 100 } }),
    ConvertPdfToNote: () => ({ convertPdfToNote: { __typename: 'PdfConversionPayload', conversion: { ...conversion('TRIAGE'), note: { __typename: 'Note', id: NEW } }, ...noProblems } }),
    NotePdfConversion: (v) => {
      if (v.id !== NEW) return { note: { __typename: 'Note', id: v.id, pdfConversion: null } }
      checks++
      // A scanned page the OCR was unsure of, read again by AI (lvn-backend ADR-0063).
      return { note: { __typename: 'Note', id: NEW, pdfConversion: checks > 2 ? conversion('DONE', { cards: 2, scannedPages: 1, aiPages: 1, aiRejected: 0 }) : conversion('PARSING') } }
    },
  })
  await page.goto(READER_URL)
  await page.getByRole('button', { name: 'Convert to cards' }).click()
  const dialog = page.getByRole('dialog', { name: 'Convert this PDF into cards' })
  await expect(dialog.getByText('You have converted 3 of 100 pages this month.')).toBeVisible()
  await dialog.getByRole('button', { name: 'Convert' }).click()

  await expect(page).toHaveURL(new RegExp(`/notes/${NEW}/read/${PDF_ID}$`))
  await expect(page.getByText('Reading the PDF: layout, tables, pictures and scans…')).toBeVisible()
  expect(calls.find((c) => c.op === 'ConvertPdfToNote')?.variables).toEqual({ noteId: NOTE_ID, fileId: PDF_ID })
  await expect(page.getByText(/Made 2 cards from 1 page\./)).toBeVisible({ timeout: 15_000 })
  await expect(page.getByText(/AI read 1 unclear page again\./)).toBeVisible()
  await expect(page.getByText(/use Clean up the text in the AI panel/)).toBeVisible()
  if (isPhone()) await page.getByRole('button', { name: 'Show notes' }).click()
  await expect(page.getByRole('textbox', { name: 'Note content' }).getByText(PDF_TEXT.page1[1]!)).toBeVisible()
  await expect(page.locator('.lvn-anchor-chip')).toHaveCount(2)
})
