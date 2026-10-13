import { expect, test } from '@playwright/test'
import { cards, meta, mockApi, mockLive, NOTE_ID, page1, USER } from './support/notes-api'

/**
 * Ask AI (lvn-backend ADR-0060) against a mocked API: the Ask AI page and its scopes, an answer that grows while the
 * model writes (the live channel says when), its citations and sources, Ask AI on one note and on a workspace doubt,
 * and the refusals. The real model answers in lvn-backend's tests and tests/e2e/live.spec.ts.
 */

const ANSWER = '01920000-0000-7000-8000-0000000a5001'
const GRAPHS = '01920000-0000-7000-8000-00000000a0a1'
const GROUP = '01920000-0000-7000-8000-0000000a0009'
const DOUBT = '01920000-0000-7000-8000-0000000d0001'
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })

const answer = (over: Record<string, unknown> = {}) => ({
  __typename: 'AiAnswer',
  id: ANSWER,
  question: 'How do I find shortest paths?',
  scope: 'PUBLIC',
  status: 'READY',
  text: '',
  sources: [],
  error: null,
  noteId: null,
  doubtId: null,
  createdAt: new Date().toISOString(),
  ...over,
})
const source = (n: number, over: Record<string, unknown> = {}) => ({ __typename: 'AiSource', n, noteId: GRAPHS, title: 'Graphs', versionId: '01920000-0000-7000-8000-0000000e0001', cardIds: ['01920000-0000-7000-8000-00000000c0a1'], snippet: 'Dijkstra finds shortest paths with a priority queue.', ...over })
const aiState = (available = true, reason: string | null = null) => ({
  aiStatus: { __typename: 'AiStatus', available, reason },
  myAiAllowance: { __typename: 'AiAllowance', usedToday: 0, limitToday: 200_000, resetsAt: new Date(Date.now() + 3_600_000).toISOString() },
})
const asked = (a: unknown) => ({ askAi: { __typename: 'AskAiPayload', answer: a, userErrors: [] } })

test('asks public notes from the Ask AI page; the answer grows as the live channel says, then cites its sources', async ({ page }) => {
  const live = await mockLive(page)
  let stage: 'none' | 'writing' | 'done' = 'none'
  const current = () =>
    stage === 'writing'
      ? answer({ status: 'RUNNING', text: 'Use Dijkstra' })
      : answer({ text: 'Use **Dijkstra** with a priority queue [1].', sources: [source(1)] })
  const calls = await mockApi(page, {
    AiState: () => aiState(),
    MyAiAnswers: () => ({ myAiAnswers: stage === 'none' ? [] : [current()] }),
    AskAi: () => ((stage = 'writing'), asked(answer({ status: 'QUEUED' }))),
    AiAnswer: () => ({ aiAnswer: current() }),
  })
  await page.goto('/ask')
  await expect(page.getByRole('heading', { level: 1, name: 'Ask AI' })).toBeVisible()
  await expect(page.getByText('No questions yet.')).toBeVisible()
  await page.getByRole('radio', { name: 'Public notes' }).click()
  await expect(page.getByText('Notes anyone can read on LearnViaNotes.')).toBeVisible()
  await page.getByLabel('Your question', { exact: true }).fill('How do I find shortest paths?')
  await page.getByRole('button', { name: 'Ask', exact: true }).click()
  const card = page.getByRole('article', { name: 'How do I find shortest paths?' })
  await expect(card.getByRole('status')).toHaveText('Writing…')
  await expect(card.getByText('Use Dijkstra')).toBeVisible()
  expect(calls.find((c) => c.op === 'AskAi')?.variables).toEqual({ input: { question: 'How do I find shortest paths?', scope: 'PUBLIC' } })

  // The model finished: the live channel says so, and the answer is asked for at once.
  stage = 'done'
  const before = calls.filter((c) => c.op === 'AiAnswer').length
  await expect.poll(() => live.subscriptions.length).toBeGreaterThan(0)
  live.send({ kind: 'AI_ANSWER', id: ANSWER })
  await expect.poll(() => calls.filter((c) => c.op === 'AiAnswer').length, { timeout: 1500 }).toBeGreaterThan(before)
  await expect(card.locator('strong')).toHaveText('Dijkstra')
  await expect(card.getByRole('status')).toHaveCount(0)
  await expect(card.getByRole('link', { name: 'Source 1' })).toHaveAttribute('href', `#source-${ANSWER}-1`)
  const sources = card.getByRole('region', { name: 'Sources' })
  await expect(sources.getByRole('link', { name: /Graphs/ })).toHaveAttribute('href', `/notes/${GRAPHS}`)
  await expect(sources.getByText('Dijkstra finds shortest paths with a priority queue.')).toBeVisible()
})

test('asks about one note from its AI panel: the draft is the source', async ({ page }) => {
  let answers: unknown[] = []
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    AiState: () => aiState(),
    NoteAiArtifacts: () => ({ note: { __typename: 'Note', id: NOTE_ID, cards: { __typename: 'CardConnection', edges: [] }, aiArtifacts: [] } }),
    MyAiAnswers: (v) => ({ myAiAnswers: v.noteId === NOTE_ID ? answers : [] }),
    AskAi: (v) => {
      const input = v.input as { question: string }
      answers = [answer({ question: input.question, scope: 'THIS_NOTE', noteId: NOTE_ID, text: 'Halve the range each step [1].', sources: [source(1, { noteId: NOTE_ID, title: 'Searching', versionId: null, snippet: 'Halve the range each step.' })] })]
      return asked(answers[0])
    },
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'AI tasks' }).click()
  const panel = page.getByRole('dialog', { name: 'AI tasks' })
  await panel.getByRole('textbox', { name: 'Ask about this note' }).fill('How does binary search work?')
  await panel.getByRole('textbox', { name: 'Ask about this note' }).press('Enter')
  const card = panel.getByRole('article', { name: 'How does binary search work?' })
  await expect(card.getByText('Halve the range each step', { exact: false }).first()).toBeVisible()
  await expect(card.getByRole('region', { name: 'Sources' }).getByText('draft')).toBeVisible()
  expect(calls.find((c) => c.op === 'AskAi')?.variables).toEqual({ input: { question: 'How does binary search work?', scope: 'THIS_NOTE', noteId: NOTE_ID } })
})

test('asks AI about a workspace doubt, over the workspace’s notes', async ({ page }) => {
  let answers: unknown[] = []
  const calls = await mockApi(page, {
    AiState: () => aiState(),
    Doubt: () => ({
      doubt: {
        __typename: 'Doubt', id: DOUBT, title: 'Why does sift-down swap twice?', moderation: 'OK', moderationReason: null, moderationCanAppeal: false, status: 'OPEN', repoRef: null, createdAt: new Date().toISOString(), answerCount: 0,
        author: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' }, body: doc('See the loop'), resolvedAt: null, answers: [],
        viewerCan: { __typename: 'DoubtActions', answer: true, resolve: true, reopen: false, delete: true },
      },
    }),
    MyAiAnswers: (v) => ({ myAiAnswers: v.doubtId === DOUBT ? answers : [] }),
    AskAiAboutDoubt: () => {
      answers = [answer({ question: 'Why does sift-down swap twice?', scope: 'WORKSPACE', doubtId: DOUBT, text: 'It swaps with the smaller child [1].', sources: [source(1, { title: 'Team notes', snippet: 'Sift-down swaps the parent with its smaller child.' })] })]
      return { askAiAboutDoubt: { __typename: 'AskAiPayload', answer: answers[0], userErrors: [] } }
    },
  })
  await page.goto(`/groups/${GROUP}/doubts/${DOUBT}`)
  const section = page.getByRole('region', { name: 'Ask AI' })
  await section.getByRole('button', { name: 'Ask AI about this doubt' }).click()
  await expect(section.getByText('It swaps with the smaller child', { exact: false })).toBeVisible()
  await expect(section.getByRole('link', { name: /Team notes/ })).toBeVisible()
  expect(calls.find((c) => c.op === 'AskAiAboutDoubt')?.variables).toEqual({ doubtId: DOUBT })
})

test('says why AI cannot answer: off, or the day’s allowance used up; a failed answer and deleting one', async ({ page }) => {
  let state = aiState(false, 'PROVIDER_DOWN')
  let answers: unknown[] = [answer({ status: 'FAILED', error: 'AI is not answering right now. Try again in a minute.' })]
  const calls = await mockApi(page, {
    AiState: () => state,
    MyAiAnswers: () => ({ myAiAnswers: answers }),
    AskAi: () => ({ askAi: { __typename: 'AskAiPayload', answer: null, userErrors: [{ __typename: 'UserError', field: null, message: 'You have used today’s AI allowance. It renews at midnight UTC.', code: 'RATE_LIMITED' }] } }),
    DeleteAiAnswer: () => ((answers = []), { deleteAiAnswer: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await page.goto('/ask')
  await expect(page.getByText('The AI model isn\'t answering right now. Try again in a minute.')).toBeVisible()
  await expect(page.getByLabel('Your question', { exact: true })).toBeDisabled()
  const failed = page.getByRole('article', { name: 'How do I find shortest paths?' })
  await expect(failed.getByRole('alert')).toHaveText('AI is not answering right now. Try again in a minute.')

  state = aiState()
  await page.reload()
  await page.getByLabel('Your question', { exact: true }).fill('What is a heap?')
  await page.getByRole('button', { name: 'Ask', exact: true }).click()
  await expect(page.getByRole('alert').filter({ hasText: 'allowance' })).toHaveText('You have used today’s AI allowance. It renews at midnight UTC.')

  await failed.getByRole('button', { name: 'Delete this answer' }).click()
  await expect(failed).toHaveCount(0)
  expect(calls.find((c) => c.op === 'DeleteAiAnswer')?.variables).toEqual({ id: ANSWER })
})

test('the sidebar takes a signed-in learner to the AI Assistant; phones find it in the menu and with their notes', async ({ page }, info) => {
  await mockApi(page, {
    AiState: () => aiState(),
    MyAiAnswers: () => ({ myAiAnswers: [] }),
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
  })
  await page.goto('/ask')
  const sidebar = page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'AI Assistant' })
  if (info.project.name !== 'phone') return void (await expect(sidebar).toHaveAttribute('href', '/ask'))
  // A phone has the sidebar as a menu (lvn-backend ADR-0076), and Ask AI leads the views row of the notes.
  await expect(sidebar).toBeHidden()
  await page.getByRole('button', { name: 'Menu' }).click()
  await expect(page.getByRole('dialog', { name: 'Menu' }).getByRole('link', { name: 'AI Assistant' })).toHaveAttribute('href', '/ask')
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog', { name: 'Menu' })).toHaveCount(0)
  await page.goto('/notes')
  await page.getByRole('link', { name: 'Ask AI' }).click()
  await expect(page).toHaveURL(/\/ask$/)
})
