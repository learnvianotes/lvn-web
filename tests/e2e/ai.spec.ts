import { expect, test, type Page } from '@playwright/test'
import { NOTE_ID, cards, meta, mockApi, mockLive, p, page1, type Handler } from './support/notes-api'

/**
 * AI tasks on a note (lvn-backend ADR-0059) against a mocked API: running a task and waiting for it, Markdown results,
 * keeping cards into the note or a new note of one's own, failures, AI being off and the day's allowance. The real
 * model answers in lvn-backend's live tests; the deployed API in tests/e2e/live.spec.ts.
 */

const ART = '01920000-0000-7000-8000-0000000a1001'
const NEW_NOTE = '01920000-0000-7000-8000-00000000a0ff'
const FRIEND = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar', handle: 'ravi' }
const readerCan = (fork: boolean) => ({ __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork })

const artifact = (over: Record<string, unknown> = {}) => ({
  __typename: 'AiArtifact',
  id: ART,
  task: 'SUMMARIZE',
  status: 'READY',
  language: 'ENGLISH',
  markdown: null,
  title: null,
  cards: null,
  error: null,
  fromPublishedVersion: false,
  truncated: false,
  keptAt: null,
  createdAt: new Date().toISOString(),
  ...over,
})
const aiCard = (type: string, content: unknown) => ({ __typename: 'AiCard', type, content })
const flashcard = (front: string, back: string) => aiCard('flashcard', { front: { type: 'doc', content: [p(front)] }, back: { type: 'doc', content: [p(back)] } })

const aiState = (over: { available?: boolean; reason?: string | null; usedToday?: number; limitToday?: number | null } = {}) => ({
  aiStatus: { __typename: 'AiStatus', available: over.available ?? true, reason: over.reason ?? null },
  myAiAllowance: { __typename: 'AiAllowance', usedToday: over.usedToday ?? 20_000, limitToday: over.limitToday === undefined ? 200_000 : over.limitToday, resetsAt: new Date(Date.now() + 3_600_000).toISOString() },
})
const noRecordings = { __typename: 'CardConnection', edges: [] as unknown[] }
const artifacts = (list: unknown[], recordings: string[] = []) => ({ note: { __typename: 'Note', id: NOTE_ID, cards: { ...noRecordings, edges: recordings.map((id) => ({ __typename: 'CardEdge', node: { __typename: 'Card', id, type: 'audio' } })) }, aiArtifacts: list } })
const ran = (a: unknown) => ({ runAiTask: { __typename: 'RunAiTaskPayload', artifact: a, userErrors: [] } })

async function openPanel(page: Page) {
  await page.getByRole('button', { name: 'AI tasks' }).click()
  return page.getByRole('dialog', { name: 'AI tasks' })
}

const owner = (extra: Record<string, Handler>) => ({ NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }), AiState: () => aiState(), ...extra })
const reader = (fork: boolean, extra: Record<string, Handler>) => ({
  NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER', owner: FRIEND, visibility: 'PUBLIC', viewerCan: readerCan(fork), publishedAt: new Date().toISOString() }), cards: page1(cards) } }),
  AiState: () => aiState(),
  ...extra,
})

test('an owner summarises a note: it shows while it runs, then reads as Markdown', async ({ page }) => {
  let polls = 0
  const calls = await mockApi(
    page,
    owner({
      NoteAiArtifacts: () => artifacts([]),
      RunAiTask: () => ran(artifact({ status: 'QUEUED' })),
      AiArtifact: () => ({ aiArtifact: ++polls < 2 ? artifact({ status: 'RUNNING' }) : artifact({ markdown: 'Binary search **halves** the range.\n\n- Needs sorted input\n- Takes O(log n) steps' }) }),
    }),
  )
  await page.goto(`/notes/${NOTE_ID}`)
  const panel = await openPanel(page)
  await expect(panel.getByText('Nothing yet.', { exact: false })).toBeVisible()
  await expect(panel.getByText("Today's AI allowance: 10% used")).toBeVisible()
  await panel.getByRole('button', { name: /^Summarise/ }).click()
  const result = panel.getByRole('article', { name: 'Summarise' })
  await expect(result.getByRole('status')).toBeVisible()
  await expect(result.getByText('halves', { exact: true })).toBeVisible()
  await expect(result.locator('strong')).toHaveText('halves')
  await expect(result.getByRole('listitem')).toHaveText(['Needs sorted input', 'Takes O(log n) steps'])
  await expect(result.getByRole('status')).toHaveCount(0)
  expect(calls.find((c) => c.op === 'RunAiTask')?.variables).toEqual({ input: { noteId: NOTE_ID, task: 'SUMMARIZE', language: 'ENGLISH' } })
  expect(polls).toBeGreaterThanOrEqual(2)
})

test('flashcards are previewed, one is dropped, and the rest go into the note', async ({ page }) => {
  const calls = await mockApi(
    page,
    owner({
      NoteAiArtifacts: () =>
        artifacts([
          artifact({ task: 'FLASHCARDS', title: 'Flashcards — Searching', cards: [flashcard('What does binary search need?', 'Sorted input'), flashcard('Its running time?', 'O(log n)'), flashcard('What is halved?', 'The range')] }),
          artifact({ id: '01920000-0000-7000-8000-0000000a1002', task: 'REVISION_SHEET', title: 'Revision sheet — Searching', cards: [aiCard('markdown', { source: '- Sorted input\n- **Halve** the range' })] }),
        ]),
      KeepAiCards: () => ({ keepAiCards: { __typename: 'KeepAiCardsPayload', noteId: NOTE_ID, userErrors: [] } }),
    }),
  )
  await page.goto(`/notes/${NOTE_ID}`)
  const panel = await openPanel(page)
  // A Markdown card previews as Markdown, not as its source.
  const sheet = panel.getByRole('article', { name: 'Revision sheet' })
  await expect(sheet.locator('[data-card-type="markdown"] li')).toHaveText(['Sorted input', 'Halve the range'])
  const flashcards = panel.getByRole('article', { name: 'Flashcards' })
  await expect(flashcards.getByText('What does binary search need?')).toBeVisible()
  await flashcards.getByRole('checkbox', { name: 'Keep card 2' }).uncheck()
  await flashcards.getByRole('button', { name: 'Add 2 cards to this note' }).click()
  // The panel closes and the note loads again with the cards in its draft.
  await expect(panel).toBeHidden()
  await expect(page.getByText('Added to this note.')).toBeVisible()
  expect(calls.find((c) => c.op === 'KeepAiCards')?.variables).toEqual({ input: { artifactId: ART, cardIndexes: [0, 2], into: 'NOTE' } })
  await expect.poll(() => calls.filter((c) => c.op === 'NoteToEdit').length).toBeGreaterThanOrEqual(2)
})

test("a reader keeps a quiz as a note of their own, and is never offered the author's note", async ({ page }) => {
  const quiz = aiCard('quiz', { question: { type: 'doc', content: [p('Its running time?')] }, choices: [{ id: 'c1', content: [{ type: 'text', text: 'O(n)' }] }, { id: 'c2', content: [{ type: 'text', text: 'O(log n)' }] }], correct: ['c2'], multiple: false })
  const calls = await mockApi(
    page,
    reader(true, {
      NoteAiArtifacts: () => artifacts([artifact({ task: 'QUIZ', title: 'Quiz — Searching', cards: [quiz], fromPublishedVersion: true })]),
      KeepAiCards: () => ({ keepAiCards: { __typename: 'KeepAiCardsPayload', noteId: NEW_NOTE, userErrors: [] } }),
    }),
  )
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('By Ravi Kumar')).toBeVisible()
  const panel = await openPanel(page)
  const result = panel.getByRole('article', { name: 'Quiz' })
  await expect(result.getByText('Made from the published version.')).toBeVisible()
  // The preview is the card itself: it can be tried before it is kept.
  await result.getByRole('radio', { name: 'O(log n)' }).click()
  await result.getByRole('button', { name: 'Check' }).click()
  await expect(result.getByText('Correct!')).toBeVisible()
  await expect(result.getByRole('button', { name: /to this note/ })).toHaveCount(0)
  await result.getByRole('button', { name: 'Save 1 card as my note' }).click()
  await expect(result.getByRole('link', { name: 'Open it' })).toHaveAttribute('href', `/notes/${NEW_NOTE}`)
  await expect(result.getByText('Kept')).toBeVisible()
  expect(calls.find((c) => c.op === 'KeepAiCards')?.variables).toEqual({ input: { artifactId: ART, cardIndexes: [0], into: 'NEW_NOTE' } })
})

test('a reader who may not copy the note is not offered tasks that make a copy, nor code help without code', async ({ page }) => {
  await mockApi(page, reader(false, { NoteAiArtifacts: () => artifacts([]) }))
  await page.goto(`/notes/${NOTE_ID}`)
  const panel = await openPanel(page)
  await expect(panel.getByRole('button', { name: /^Summarise/ })).toBeEnabled()
  await expect(panel.getByRole('button', { name: /^Flashcards/ })).toBeVisible()
  await expect(panel.getByRole('button', { name: /^Make notes/ })).toHaveCount(0)
  await expect(panel.getByRole('button', { name: /^Outline → note/ })).toHaveCount(0)
  await expect(panel.getByRole('button', { name: /^Explain the code/ })).toHaveCount(0)
  // Tidying into notes is for one's own notes (ADR-0062).
  await expect(panel.getByRole('button', { name: /^Tidy into notes/ })).toHaveCount(0)
})

test('a failed result says why and runs again, translating sends the language, and a result can be deleted', async ({ page }) => {
  let list = [artifact({ status: 'FAILED', error: 'The AI model gave an answer that could not be used. Try again.' })]
  const calls = await mockApi(
    page,
    owner({
      NoteAiArtifacts: () => artifacts(list),
      RunAiTask: (v) => {
        const input = v.input as { task: string; language: string }
        return ran(artifact({ id: input.task === 'TRANSLATE' ? '01920000-0000-7000-8000-0000000a1004' : '01920000-0000-7000-8000-0000000a1003', task: input.task, language: input.language, status: 'QUEUED' }))
      },
      AiArtifact: (v) => ({ aiArtifact: artifact({ id: v.id, task: v.id === '01920000-0000-7000-8000-0000000a1004' ? 'TRANSLATE' : 'SUMMARIZE', language: v.id === '01920000-0000-7000-8000-0000000a1004' ? 'TELUGU' : 'ENGLISH', markdown: 'Done.' }) }),
      DeleteAiArtifact: () => {
        list = []
        return { deleteAiArtifact: { __typename: 'OkPayload', ok: true, userErrors: [] } }
      },
    }),
  )
  await page.goto(`/notes/${NOTE_ID}`)
  const panel = await openPanel(page)
  const failed = panel.locator('article[data-ai-status="FAILED"]')
  await expect(failed.getByRole('alert')).toHaveText('The AI model gave an answer that could not be used. Try again.')
  await failed.getByRole('button', { name: 'Try again' }).click()
  await expect(panel.locator('article[data-ai-status="READY"]', { hasText: 'Done.' })).toHaveCount(1)

  await panel.getByLabel('Translate into').selectOption('TELUGU')
  await panel.getByRole('button', { name: 'Translate', exact: true }).click()
  await expect(panel.getByRole('article', { name: 'Translated into Telugu' })).toContainText('Done.')
  const runs = calls.filter((c) => c.op === 'RunAiTask').map((c) => c.variables.input)
  expect(runs).toEqual([
    { noteId: NOTE_ID, task: 'SUMMARIZE', language: 'ENGLISH' },
    { noteId: NOTE_ID, task: 'TRANSLATE', language: 'TELUGU' },
  ])

  await failed.getByRole('button', { name: 'Delete this result' }).click()
  await expect(failed).toHaveCount(0)
  expect(calls.find((c) => c.op === 'DeleteAiArtifact')?.variables).toEqual({ id: ART })
})

test("AI that is off says why, and a spent allowance stops new tasks; the server's refusal is shown in its words", async ({ page }) => {
  let state = aiState({ available: false, reason: 'PROVIDER_DOWN' })
  await mockApi(
    page,
    owner({
      AiState: () => state,
      NoteAiArtifacts: () => artifacts([]),
      RunAiTask: () => ({ runAiTask: { __typename: 'RunAiTaskPayload', artifact: null, userErrors: [{ __typename: 'UserError', field: null, message: "You've used today's AI allowance; it comes back at midnight UTC.", code: 'RATE_LIMITED' }] } }),
    }),
  )
  await page.goto(`/notes/${NOTE_ID}`)
  let panel = await openPanel(page)
  await expect(panel.getByRole('alert')).toHaveText("The AI model isn't answering right now. Try again in a minute.")
  await expect(panel.getByRole('button', { name: /^Summarise/ })).toBeDisabled()
  await panel.getByRole('button', { name: 'Close' }).click()

  state = aiState({ usedToday: 200_000 })
  panel = await openPanel(page)
  await expect(panel.getByText("You've used today's AI allowance.", { exact: false })).toBeVisible()
  await expect(panel.getByRole('button', { name: /^Quiz/ })).toBeDisabled()
  await panel.getByRole('button', { name: 'Close' }).click()

  // The allowance shown can be behind the server's: its refusal is the answer.
  state = aiState({ usedToday: 199_000 })
  panel = await openPanel(page)
  await panel.getByRole('button', { name: /^Quiz/ }).click()
  await expect(panel.getByRole('alert')).toHaveText("You've used today's AI allowance; it comes back at midnight UTC.")
})

test("the account page shows today's AI allowance, or why AI is off", async ({ page }) => {
  let state = aiState({ usedToday: 150_000 })
  await mockApi(page, { AiState: () => state, MyDataExports: () => ({ myDataExports: [] }), NoteImports: () => ({ noteImports: [] }) }, { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } })
  await page.goto('/profile')
  const section = page.getByRole('region', { name: 'AI' })
  await expect(section.getByText("Today's AI allowance: 75% used")).toBeVisible()
  await expect(section.getByRole('meter', { name: "Today's AI allowance" })).toHaveAttribute('aria-valuenow', '150000')

  state = aiState({ available: false, reason: 'BUDGET' })
  await page.reload()
  await expect(page.getByRole('region', { name: 'AI' }).getByText("AI is resting until next month: this month's AI budget is used up.")).toBeVisible()
})

const insight = (task: string, over: Record<string, unknown> = {}) => ({ __typename: 'AiInsight', id: `01920000-0000-7000-8000-0000000a70${task.length.toString().padStart(2, '0')}`, task, status: 'READY', markdown: null, title: null, cards: null, hidden: false, versionId: '01920000-0000-7000-8000-0000000e0001', ...over })
const quizCard = aiCard('quiz', { question: { type: 'doc', content: [p('Its running time?')] }, choices: [{ id: 'c1', content: [{ type: 'text', text: 'O(n)' }] }, { id: 'c2', content: [{ type: 'text', text: 'O(log n)' }] }], correct: ['c2'], multiple: false })

test('a reader of a public note tries its study aids and keeps the quiz as their own note (lvn-backend ADR-0061)', async ({ page }) => {
  const calls = await mockApi(page, {
    ...reader(true, {}),
    NoteInsights: () => ({ note: { __typename: 'Note', id: NOTE_ID, noteProcessingStatus: null, aiInsights: [insight('SUMMARIZE', { markdown: 'Binary search **halves** the range.' }), insight('QUIZ', { title: 'Quiz — Searching', cards: [quizCard] })] } }),
    KeepAiCards: () => ({ keepAiCards: { __typename: 'KeepAiCardsPayload', noteId: NEW_NOTE, userErrors: [] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const aids = page.getByRole('region', { name: 'Study aids' })
  await expect(aids.locator('strong')).toHaveText('halves')
  await expect(aids.getByRole('button', { name: /Hide from readers/ })).toHaveCount(0)
  await aids.getByRole('tab', { name: 'Quiz' }).click()
  await aids.getByRole('radio', { name: 'O(log n)' }).click()
  await aids.getByRole('button', { name: 'Check' }).click()
  await expect(aids.getByText('Correct!')).toBeVisible()
  await aids.getByRole('button', { name: 'Save as my note' }).click()
  await expect(aids.getByRole('link', { name: 'Open it' })).toHaveAttribute('href', `/notes/${NEW_NOTE}`)
  expect(calls.find((c) => c.op === 'KeepAiCards')?.variables).toEqual({ input: { artifactId: insight('QUIZ').id, cardIndexes: [0], into: 'NEW_NOTE' } })
})

test('the owner watches the study aids being made, live, and hides one from readers', async ({ page }) => {
  const live = await mockLive(page)
  let stage: 'making' | 'done' = 'making'
  let hidden = false
  const answer = () => ({
    note: {
      __typename: 'Note',
      id: NOTE_ID,
      noteProcessingStatus: { __typename: 'NoteProcessing', versionId: insight('SUMMARIZE').versionId, done: stage === 'done', steps: [] },
      aiInsights: [insight('SUMMARIZE', { markdown: 'Binary search halves the range.', hidden }), insight('FLASHCARDS', stage === 'done' ? { cards: [aiCard('flashcard', { front: { type: 'doc', content: [p('Halve what?')] }, back: { type: 'doc', content: [p('The range')] } })] } : { status: 'RUNNING' })],
    },
  })
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ publishedAt: new Date().toISOString(), publishedVersion: { __typename: 'NoteVersion', id: insight('SUMMARIZE').versionId, number: 1, createdAt: new Date().toISOString() } }), cards: page1(cards) } }),
    NoteInsights: answer,
    SetAiInsightHidden: (v) => ((hidden = v.hidden as boolean), { setAiInsightHidden: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const aids = page.getByRole('region', { name: 'Study aids' })
  await expect(aids.getByText('Made by AI from your published note for its readers.', { exact: false })).toBeVisible()
  await aids.getByRole('tab', { name: 'Flashcards' }).click()
  await expect(aids.getByRole('status')).toHaveText('Being made…')
  stage = 'done'
  await expect.poll(() => live.subscriptions.length).toBeGreaterThan(0)
  live.send({ kind: 'NOTE_PROCESSING', id: NOTE_ID })
  await expect(aids.getByText('Halve what?')).toBeVisible({ timeout: 2500 })
  await aids.getByRole('tab', { name: 'Summarise' }).click()
  await aids.getByRole('button', { name: 'Hide from readers' }).click()
  await expect(aids.getByText('Hidden from readers', { exact: true })).toBeVisible()
  expect(calls.find((c) => c.op === 'SetAiInsightHidden')?.variables).toEqual({ id: insight('SUMMARIZE').id, hidden: true })
})

test('transcribes a note’s recording and tidies rough notes into clean ones (lvn-backend ADR-0062)', async ({ page }) => {
  const RECORDING = '01920000-0000-7000-8000-00000000c0a9'
  const calls = await mockApi(
    page,
    owner({
      NoteAiArtifacts: () => artifacts([], [RECORDING]),
      RunAiTask: (v) => ran(artifact({ id: '01920000-0000-7000-8000-0000000a1abc', task: (v.input as { task: string }).task, status: 'QUEUED' })),
      AiArtifact: () => ({ aiArtifact: artifact({ id: '01920000-0000-7000-8000-0000000a1abc', task: 'TRANSCRIBE', title: 'Transcript — Searching', cards: [aiCard('text', { doc: { type: 'doc', content: [p('Today we look at binary search.')] } })] }) }),
    }),
  )
  await page.goto(`/notes/${NOTE_ID}`)
  const panel = await openPanel(page)
  await panel.getByRole('button', { name: /^Transcribe the recording/ }).click()
  await expect(panel.getByRole('article', { name: 'Transcribe' }).getByText('Today we look at binary search.')).toBeVisible()
  await expect(panel.getByRole('button', { name: 'Add 1 card to this note' })).toBeVisible()
  await panel.getByRole('button', { name: /^Tidy into notes/ }).click()
  expect(calls.filter((c) => c.op === 'RunAiTask').map((c) => c.variables.input)).toEqual([
    { noteId: NOTE_ID, task: 'TRANSCRIBE', language: 'ENGLISH', cardIds: [RECORDING] },
    { noteId: NOTE_ID, task: 'QUICK_NOTE', language: 'ENGLISH' },
  ])
})
