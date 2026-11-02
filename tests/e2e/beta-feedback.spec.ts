import { expect, test, type Page } from '@playwright/test'
import { mkdir } from 'node:fs/promises'
import { NOTE_ID, cards, meta, mockApi, p, page1 } from './support/notes-api'

/**
 * Owner beta feedback: the page editor, share dialog, voice notes, distinct studio pages,
 * quiz sharing and subjects. The API is mocked. Screenshots are taken on desktop at 375, 768 and 1440.
 */

const SHOTS = '/opt/cursor/artifacts/screenshots'
const WIDTHS = [375, 768, 1440] as const
const noProblems = { userErrors: [] }
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT, OPTIONS', 'access-control-allow-headers': '*' }

async function mockStorage(page: Page) {
  await page.route('http://storage.test/**', async (route) => {
    const req = route.request()
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: CORS })
    return route.fulfill({ status: 200, headers: CORS })
  })
}
const quizCard = {
  __typename: 'Card',
  id: '01920000-0000-7000-8000-00000000c003',
  type: 'quiz',
  position: 'a2',
  revision: 1,
  content: { question: { type: 'doc', content: [p('Its running time?')] }, choices: [{ id: 'a', content: [{ type: 'text', text: 'O(n)' }] }, { id: 'b', content: [{ type: 'text', text: 'O(log n)' }] }], correct: ['b'], multiple: false },
}
const png = Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==', 'base64')

test.use({ launchOptions: { args: ['--use-fake-ui-for-media-stream', '--use-fake-device-for-media-stream'] }, permissions: ['microphone', 'camera'] })

test.beforeAll(async () => {
  await mkdir(SHOTS, { recursive: true })
})

async function shot(page: Page, name: string, width: number) {
  await page.setViewportSize({ width, height: width < 700 ? 812 : 900 })
  await page.screenshot({ path: `${SHOTS}/${name}-${width}.png` })
}

test.describe('beta feedback', () => {
  test.beforeEach(({}, info) => {
    test.skip(info.project.name !== 'desktop', 'fixed widths cover phone and desktop')
  })

  test('the page editor draws, and screenshots at 375, 768 and 1440', async ({ page }) => {
    await mockStorage(page)
    const calls = await mockApi(page, {
      NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
      NotePages: () => ({ note: { pages: [] } }),
      SaveNotePages: () => ({ saveNotePages: noProblems }),
      CreatePageImage: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: '01920000-0000-7000-8000-00000000f0b1', uploadUrl: 'http://storage.test/put/page', uploadHeaders: [] }, ...noProblems } }),
      CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...noProblems } }),
    })
    await page.goto(`/notes/${NOTE_ID}`)
    await page.getByRole('button', { name: 'Pages', exact: true }).click()
    const board = page.getByRole('application', { name: 'Drawing page' })
    await expect(board).toBeVisible()
    await expect(page.getByRole('toolbar', { name: 'Drawing tools' })).toBeVisible()
    await expect(page.getByRole('status').filter({ hasText: 'Pages saved' })).toBeVisible()
    for (const width of WIDTHS) await shot(page, 'editor', width)

    await page.setViewportSize({ width: 1440, height: 900 })
    const box = (await board.boundingBox())!
    await page.mouse.move(box.x + 40, box.y + 40)
    await page.mouse.down()
    await page.mouse.move(box.x + 180, box.y + 220, { steps: 8 })
    await page.mouse.up()
    await expect(board).toHaveAttribute('data-strokes', '1')
    await expect.poll(() => calls.some((c) => c.op === 'SaveNotePages' && Array.isArray((c.variables.pages as { strokes?: unknown[] }[])?.[0]?.strokes) && ((c.variables.pages as { strokes: unknown[] }[])[0]?.strokes.length ?? 0) > 0)).toBe(true)

    await page.getByRole('button', { name: 'Ruler', exact: true }).click()
    await page.mouse.move(box.x + 30, box.y + 30)
    await page.mouse.down()
    await page.mouse.move(box.x + box.width * 0.5, box.y + 40, { steps: 4 })
    await page.mouse.up()
    await expect(page.getByText(/Scale \d+% of the page/)).toBeVisible()

    await page.getByLabel('Insert picture').setInputFiles({ name: 'diagram.png', mimeType: 'image/png', buffer: png })
    await expect(page.getByRole('img', { name: 'diagram.png' })).toBeVisible()
    await expect.poll(() => calls.find((c) => c.op === 'CreatePageImage')?.variables).toMatchObject({ input: { purpose: 'PAGE_IMAGE', parentId: NOTE_ID, mimeType: 'image/png' } })
    await page.getByRole('button', { name: 'Rotate' }).click()
    await page.getByRole('button', { name: 'Undo', exact: true }).click()
    await expect(page.getByRole('img', { name: 'diagram.png' })).toBeVisible()
    await page.getByRole('button', { name: 'Redo', exact: true }).click()

    await page.getByRole('button', { name: 'Scan photo' }).click()
    const scan = page.getByRole('dialog', { name: 'Scan a photo' })
    await expect(scan.getByText('Use the camera, then crop and enhance')).toBeVisible()
    await scan.getByLabel('Choose a photo').setInputFiles({ name: 'board.png', mimeType: 'image/png', buffer: png })
    await expect(scan.getByRole('img', { name: 'Photo to crop' })).toBeVisible()
    await shot(page, 'photo-scan', 1440)
    await scan.getByRole('button', { name: 'Enhance and add' }).click()
    await expect(scan).toBeHidden()
    await expect(page.getByRole('img', { name: 'Scan.png' })).toBeVisible()
  })

  test('Unlisted and Public leave Private, and the share dialog screenshots at three widths', async ({ page }) => {
    let visibility = 'PRIVATE'
    const calls = await mockApi(page, {
      NoteToEdit: () => ({ note: { ...meta({ visibility }), cards: page1(cards) } }),
      NoteShares: () => ({ note: { __typename: 'Note', id: NOTE_ID, visibility, shares: [] } }),
      ChangeNoteVisibility: (v) => {
        visibility = v.visibility as string
        return { changeNoteVisibility: { note: meta({ visibility }), ...noProblems } }
      },
    })
    await page.goto(`/notes/${NOTE_ID}`)
    await page.getByRole('button', { name: 'Share', exact: true }).click()
    const dialog = page.getByRole('dialog', { name: 'Share this note' })
    await expect(dialog.getByRole('radio', { name: /Public/ })).toBeEnabled()
    await expect(dialog.getByRole('button', { name: 'Copy link' })).toBeDisabled()
    for (const width of WIDTHS) await shot(page, 'share-dialog', width)

    await page.setViewportSize({ width: 1440, height: 900 })
    await dialog.getByRole('radio', { name: /Unlisted link/ }).check()
    await expect.poll(() => calls.find((c) => c.op === 'ChangeNoteVisibility')?.variables).toEqual({ noteId: NOTE_ID, visibility: 'UNLISTED' })
    await expect(dialog.getByRole('button', { name: 'Copy link' })).toBeEnabled()
    await dialog.getByRole('radio', { name: /Public/ }).check()
    await expect.poll(() => calls.filter((c) => c.op === 'ChangeNoteVisibility').at(-1)?.variables).toEqual({ noteId: NOTE_ID, visibility: 'PUBLIC' })
  })

  test('a voice note keeps the recording, shows a caption fallback, then transcribes', async ({ page }) => {
    await mockStorage(page)
    const calls = await mockApi(page, {
      NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
      CreateNoteUpload: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: '01920000-0000-7000-8000-00000000f0a1', uploadUrl: 'http://storage.test/put/voice', uploadHeaders: [] }, ...noProblems } }),
      CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...noProblems } }),
      VoiceCapture: () => ({ voiceCapture: noProblems }),
      TranscribeCaptionClip: () => ({ transcribeCaptionClip: { transcript: 'live line', ...noProblems } }),
      TranscribeAudio: () => ({ transcribeAudio: { transcript: 'Binary search halves the range.', ...noProblems } }),
      MakeNotesFromTranscript: () => ({ makeNotesFromTranscript: { markdown: '## Binary search\nHalve the range.', note: { id: NOTE_ID }, ...noProblems } }),
    })
    await page.goto(`/notes/${NOTE_ID}`)
    await page.getByRole('button', { name: 'Add a card', exact: true }).click()
    await page.getByRole('button', { name: /^Record a voice note/ }).click()
    const dialog = page.getByRole('dialog', { name: 'Record a voice note' })
    await dialog.getByRole('button', { name: 'Start recording' }).click()
    await expect(dialog.getByText(/Live captions need the browser’s speech recognition|Listening/)).toBeVisible()
    await expect(dialog.getByRole('status')).toHaveText(/0:0[1-9]/, { timeout: 5_000 })
    for (const width of WIDTHS) await shot(page, 'voice-note', width)
    await page.setViewportSize({ width: 1440, height: 900 })
    await dialog.getByRole('button', { name: 'Stop' }).click()
    await expect(dialog.getByLabel('Your recording')).toBeVisible()
    await dialog.getByRole('button', { name: 'Transcribe' }).click()
    await expect(dialog.getByText('Binary search halves the range.')).toBeVisible()
    await dialog.getByRole('button', { name: 'Make notes from this' }).click()
    await expect(dialog.getByText('Halve the range.')).toBeVisible()
    expect(calls.find((c) => c.op === 'CreateNoteUpload')?.variables).toMatchObject({ input: { purpose: 'VOICE_NOTE', parentId: NOTE_ID } })
    expect(calls.find((c) => c.op === 'VoiceCapture')).toBeTruthy()
    expect(calls.find((c) => c.op === 'TranscribeAudio')?.variables).toMatchObject({ noteId: NOTE_ID })
    expect(calls.find((c) => c.op === 'MakeNotesFromTranscript')?.variables).toMatchObject({ noteId: NOTE_ID, transcript: 'Binary search halves the range.' })
    await dialog.getByRole('button', { name: 'Add to the note' }).click()
    await expect(dialog).toBeHidden()
  })

  test('quick notes, flashcards, projects and upload each have their own page', async ({ page }) => {
    await mockApi(page, {})
    const pages: [path: string, heading: string, file: string][] = [
      ['/quick-notes', 'Quick notes', 'quick-notes'],
      ['/flashcards', 'Flashcards', 'flashcards'],
      ['/projects', 'Projects', 'projects'],
      ['/upload', 'Upload', 'upload'],
    ]
    for (const [path, heading, file] of pages) {
      await page.goto(path)
      await expect(page.getByRole('heading', { level: 1, name: heading })).toBeVisible()
      await expect(page.getByRole('button', { name: 'AI tasks' })).toBeVisible()
      await expect(page.getByRole('region', { name: 'Your results' })).toBeVisible()
      for (const width of WIDTHS) await shot(page, file, width)
    }
    await page.goto('/quick-notes')
    await expect(page.getByRole('paragraph').filter({ hasText: 'Scratchpad' })).toBeVisible()
    await page.goto('/flashcards')
    await page.getByRole('button', { name: 'Flip' }).click()
    await expect(page.getByText('Recall the answer before you turn it over.')).toBeVisible()
    await page.goto('/projects')
    await expect(page.getByRole('region', { name: 'Brief' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Open as a note' })).toBeVisible()
    await page.goto('/upload')
    await expect(page.getByText('Drop a PDF here')).toBeVisible()
  })

  test('the owner shares a quiz and someone takes it', async ({ page }) => {
    await mockApi(page, {
      NoteToEdit: () => ({ note: { ...meta(), cards: page1([...cards, quizCard]) } }),
      ShareQuiz: () => ({ shareQuiz: { quiz: { id: 'q', token: 'quiz-token', path: '/q/quiz-token', title: 'Searching' }, ...noProblems } }),
      SharedQuiz: () => ({ sharedQuiz: { id: 'q', token: 'quiz-token', path: '/q/quiz-token', title: 'Searching', aggregate: { attempts: 2, averageScore: 1, total: 2 }, attempts: [] } }),
      SharedQuizByLink: () => ({ sharedQuizByLink: { title: 'Searching', ownerName: 'Asha Rao', questions: [{ id: 'q1', prompt: 'Its running time?', choices: [{ id: 'a', text: 'O(n)' }, { id: 'b', text: 'O(log n)' }] }] } }),
      SubmitSharedQuizAttempt: () => ({ submitSharedQuizAttempt: { score: 1, total: 1, ...noProblems } }),
    })
    await page.goto(`/notes/${NOTE_ID}?tab=quiz`)
    await page.getByRole('tab', { name: 'Quiz' }).click()
    const share = page.getByRole('region', { name: 'Share this quiz' })
    await share.getByRole('button', { name: 'Share quiz' }).click()
    await expect(share.getByLabel('Quiz link')).toHaveValue(/\/q\/quiz-token$/)
    await expect(share.getByTestId('quiz-stats')).toHaveText('2 attempts · average 1 of 2')

    await page.goto('/q/quiz-token')
    await expect(page.getByRole('heading', { name: 'Searching' })).toBeVisible()
    await page.getByRole('radio', { name: 'O(log n)' }).check()
    await page.getByRole('button', { name: 'Submit' }).click()
    await expect(page.getByRole('status')).toHaveText('1 of 1')
  })

  test('fork stays hidden when the author opted out', async ({ page }) => {
    const friend = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar', handle: 'ravi' }
    await mockApi(page, {
      NoteToEdit: () => ({
        note: {
          ...meta({
            viewerAccess: 'READER',
            owner: friend,
            visibility: 'PUBLIC',
            allowForks: false,
            forkCount: 0,
            viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true },
            publishedAt: new Date().toISOString(),
          }),
          cards: page1(cards),
        },
      }),
    })
    await page.goto(`/notes/${NOTE_ID}`)
    await expect(page.getByRole('button', { name: 'Fork' })).toHaveCount(0)
    await expect(page.getByText('Forks are off. The author opted out of copies.')).toBeVisible()
  })

  test('subjects are in the main nav and can be searched', async ({ page }) => {
    await mockApi(page, {
      Rhythm: () => ({ rhythm: { __typename: 'Rhythm', timeZone: 'UTC', plannedDays: [1], target: 4, countedDays: 0, met: false, week: [], today: { __typename: 'RhythmToday', day: '2026-10-15', learningSeconds: 0, reviews: 0, counted: false, comeback: false, cameBack: false, items: [] }, weeksThisTerm: 1, weeksAllTime: 1, countedDaysAllTime: 0, pauses: [], pauseDaysLeft: 14, suggestion: null, shareRhythm: false } }),
      Exams: () => ({ exams: [] }),
      Recommendations: () => ({ recommendations: [] }),
    }, { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } })
    await page.goto('/home')
    const nav = page.getByRole('navigation', { name: 'Main' })
    await expect(nav.getByRole('link', { name: 'Subjects', exact: true })).toHaveAttribute('href', '/subjects')
    await expect(page.getByRole('heading', { name: 'Subjects' })).toBeVisible()
    await page.getByRole('link', { name: 'All subjects' }).click()
    await expect(page).toHaveURL(/\/subjects$/)
    await expect(page.getByRole('link', { name: /Operating Systems/ })).toHaveAttribute('href', '/subjects/os')
    await page.getByRole('textbox', { name: 'Search subjects' }).fill('paging')
    await expect(page.getByRole('link', { name: /Operating Systems/ })).toBeVisible()
    await expect(page.getByRole('link', { name: /Data Structures/ })).toHaveCount(0)
    await page.getByRole('combobox', { name: 'Filter by topic' }).selectOption({ label: 'Graphs' })
    await expect(page.getByText('No subject matches that search.')).toBeVisible()
  })
})
