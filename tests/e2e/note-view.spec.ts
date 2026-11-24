import { expect, test } from '@playwright/test'
import { CARD_B, NOTE_ID, cards, meta, mockApi, p, page1, type Handler } from './support/notes-api'

/**
 * The note view as board A draws it (lvn-backend ADR-0076), checked for dead controls: the breadcrumb leads to the
 * topic's notes; the tabs offered each have something or a way to make it (AI, or a card added to the note); Fork and
 * Share do what they say; the card rail moves between sections; and Ask Nova is docked beside the note from 1280 px, each
 * suggestion one AI task.
 */
const TOPIC = { __typename: 'Topic', id: '01920000-0000-7000-8000-0000000070a1', title: 'Searching', subject: { __typename: 'Subject', id: '01920000-0000-7000-8000-00000000500a', title: 'Algorithms' } }
const FRIEND = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar', handle: 'ravi' }
const FORKED = '01920000-0000-7000-8000-00000000a0ff'
const ART = '01920000-0000-7000-8000-0000000a1001'
const heading = (id: string, text: string, position: string) => ({ __typename: 'Card', id, type: 'heading', position, revision: 1, content: { level: 2, content: [{ type: 'text', text }] } })
const twoSections = [...cards, heading('01920000-0000-7000-8000-00000000c0d1', 'Practice', 'a2'), { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c0d2', type: 'text', position: 'a3', revision: 1, content: { doc: { type: 'doc', content: [p('Try it on a sorted list.')] } } }]
const aiState = (available: boolean) => ({ aiStatus: { __typename: 'AiStatus', available, reason: available ? null : 'NOT_CONFIGURED' }, myAiAllowance: { __typename: 'AiAllowance', usedToday: 0, limitToday: 200_000, resetsAt: new Date(Date.now() + 3_600_000).toISOString() } })
const noArtifacts = { note: { __typename: 'Note', id: NOTE_ID, cards: { __typename: 'CardConnection', edges: [] }, aiArtifacts: [] } }
const noInsights = { note: { __typename: 'Note', id: NOTE_ID, noteProcessingStatus: null, aiInsights: [] } }
const artifact = (task: string, over: Record<string, unknown> = {}) => ({ __typename: 'AiArtifact', id: ART, task, status: 'READY', language: 'ENGLISH', markdown: 'Binary search **halves** the range.', title: null, cards: null, changes: null, error: null, fromPublishedVersion: false, truncated: false, keptAt: null, createdAt: new Date().toISOString(), ...over })
const ok = { userErrors: [] }

const owner = (extra: Record<string, Handler> = {}, ai = false, list = cards) => ({
  NoteToEdit: () => ({ note: { ...meta({ topics: [TOPIC] }), cards: page1(list) } }),
  AiState: () => aiState(ai),
  NoteAiArtifacts: () => noArtifacts,
  NoteInsights: () => noInsights,
  ...extra,
})
const reader = (extra: Record<string, Handler> = {}) => ({
  NoteToEdit: () => ({
    note: {
      ...meta({ viewerAccess: 'READER', owner: FRIEND, visibility: 'PUBLIC', publishedAt: new Date().toISOString(), viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true } }),
      cards: page1(twoSections),
    },
  }),
  AiState: () => aiState(false),
  NoteAiArtifacts: () => noArtifacts,
  NoteInsights: () => noInsights,
  Discussion: () => ({
    discussion: {
      __typename: 'Discussion',
      commentCount: 0,
      viewerCanComment: true,
      whyNot: null,
      reactions: { __typename: 'Reactions', viewerReaction: null, counts: ['LIKE', 'HELPFUL', 'CELEBRATE'].map((kind) => ({ __typename: 'ReactionCount', kind, count: 0, atLeast: false })) },
      comments: { __typename: 'CommentConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } },
    },
  }),
  ...extra,
})

test('the breadcrumb leads to the topic’s notes; the owner’s tabs offer a way to add flashcards and quiz cards', async ({ page }) => {
  const calls = await mockApi(page, owner({ UpdateNoteDraft: () => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: [], conflictVersion: null, ...ok } }) }))
  await page.goto(`/notes/${NOTE_ID}`)
  const crumbs = page.getByRole('navigation', { name: 'Breadcrumb' })
  await expect(crumbs.getByRole('link', { name: 'Searching' })).toHaveAttribute('href', `/search?topic=${TOPIC.id}&topicTitle=Searching`)
  const tabs = page.getByRole('tablist', { name: 'Note sections' })
  // AI is off and the note is unpublished: no summary or discussion to offer, but its editor can add cards.
  await expect(tabs.getByRole('tab')).toHaveText(['Content', 'Flashcards', 'Quiz'])
  await tabs.getByRole('tab', { name: 'Flashcards' }).click()
  await expect(page).toHaveURL(/\?tab=flashcards$/)
  await expect(page.getByText('No flashcards in this note yet.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Make flashcards with Nova' })).toHaveCount(0)
  await page.getByRole('button', { name: 'Add a flashcard' }).click()
  await expect(tabs.getByRole('tab', { name: 'Content' })).toHaveAttribute('aria-selected', 'true')
  await expect.poll(() => calls.filter((c) => c.op === 'UpdateNoteDraft').flatMap((c) => ((c.variables.input as { ops: { type?: string }[] }).ops ?? []).map((o) => o.type)), { timeout: 10_000 }).toContain('flashcard')
})

test('arrow keys move along the tabs, and the tab chosen survives a reload', async ({ page }) => {
  await mockApi(page, owner())
  await page.goto(`/notes/${NOTE_ID}`)
  const tabs = page.getByRole('tablist', { name: 'Note sections' })
  await tabs.getByRole('tab', { name: 'Content' }).focus()
  await page.keyboard.press('ArrowRight')
  await expect(tabs.getByRole('tab', { name: 'Flashcards' })).toBeFocused()
  await expect(tabs.getByRole('tab', { name: 'Flashcards' })).toHaveAttribute('aria-selected', 'true')
  await page.keyboard.press('ArrowRight')
  await expect(tabs.getByRole('tab', { name: 'Quiz' })).toHaveAttribute('aria-selected', 'true')
  await page.reload()
  await expect(page.getByRole('tablist', { name: 'Note sections' }).getByRole('tab', { name: 'Quiz' })).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByText('No quiz in this note yet.')).toBeVisible()
})

test('with AI on, Summarise makes a summary that shows in the tab; each docked suggestion runs its task', async ({ page }, info) => {
  const tasks: string[] = []
  await mockApi(page, owner({ RunAiTask: (v) => (tasks.push((v.input as { task: string }).task), { runAiTask: { __typename: 'RunAiTaskPayload', artifact: artifact((v.input as { task: string }).task), ...ok } }) }, true))
  await page.goto(`/notes/${NOTE_ID}`)
  const tabs = page.getByRole('tablist', { name: 'Note sections' })
  await expect(tabs.getByRole('tab')).toHaveText(['Content', 'Summary', 'Flashcards', 'Quiz'])
  await tabs.getByRole('tab', { name: 'Summary' }).click()
  await page.getByRole('button', { name: 'Summarise with Nova' }).click()
  await expect(page.getByRole('region', { name: 'Made for you with Nova' }).locator('strong')).toHaveText('halves')
  expect(tasks).toEqual(['SUMMARIZE'])

  const dock = page.getByRole('complementary', { name: 'Ask Nova about this note' })
  if (info.project.name === 'phone') return void (await expect(dock).toHaveCount(0))
  const chips: [string, string][] = [
    ['Explain this in simple words', 'EXPLAIN_SIMPLY'],
    ['Generate practice questions', 'PRACTICE_QUESTIONS'],
    ['Generate flashcards', 'FLASHCARDS'],
    ['Find common mistakes', 'FIND_MISTAKES'],
    ['Summarize this note', 'SUMMARIZE'],
    ['Generate quiz', 'QUIZ'],
    ['Create quick notes', 'QUICK_NOTE'],
  ]
  await expect(dock.getByRole('listitem')).toHaveCount(chips.length)
  for (const [name, task] of chips) {
    await dock.getByRole('button', { name }).click()
    await expect.poll(() => tasks.at(-1)).toBe(task)
  }
  await expect(dock.getByLabel('Ask about this note', { exact: true })).toBeVisible()
  // The Nova tasks sheet has every task; while it is open the dock steps aside.
  await page.getByRole('button', { name: 'Nova tasks' }).click()
  await expect(dock).toHaveCount(0)
})

test('below 1280 px there is no dock; the Nova tasks sheet is the way', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'a phone never has the dock (previous test)')
  await page.setViewportSize({ width: 1279, height: 900 })
  await mockApi(page, owner({}, true))
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByRole('tablist', { name: 'Note sections' })).toBeVisible()
  await expect(page.getByRole('complementary', { name: 'Ask Nova about this note' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Nova tasks' })).toBeVisible()
})

test('a reader forks the note, copies its link, moves between its sections and opens its discussion', async ({ page, context }, info) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']).catch(() => undefined)
  const calls = await mockApi(page, reader({ ForkNote: () => ({ forkNote: { __typename: 'ForkNotePayload', note: { __typename: 'Note', id: FORKED }, ...ok } }) }))
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByRole('navigation', { name: 'Breadcrumb' }).getByRole('link', { name: 'Ravi Kumar' })).toHaveAttribute('href', '/u/ravi')
  const tabs = page.getByRole('tablist', { name: 'Note sections' })
  await expect(tabs.getByRole('tab')).toHaveText(['Content', 'Discussions'])
  await page.getByRole('button', { name: 'Share' }).click()
  await expect(page.getByRole('status').filter({ hasText: 'Link copied' })).toBeVisible()

  if (info.project.name !== 'phone') {
    const rail = page.getByRole('navigation', { name: 'Outline' })
    await expect(rail.getByRole('button', { name: /Binary search/ })).toBeVisible()
    await expect(rail.getByText('Section 1 of 2')).toBeVisible()
    await rail.getByRole('button', { name: 'Next section' }).click()
    await expect(rail.getByText('Section 2 of 2')).toBeVisible()
    await expect(rail.getByRole('button', { name: /Practice/ })).toHaveAttribute('aria-current', 'step')
    await expect(rail.getByRole('button', { name: 'Next section' })).toBeDisabled()
    await rail.getByRole('button', { name: 'Previous section' }).click()
    await expect(rail.getByText('Section 1 of 2')).toBeVisible()
  }

  await tabs.getByRole('tab', { name: 'Discussions' }).click()
  await expect(page.getByRole('region', { name: 'Discussion' })).toBeVisible()
  await page.getByRole('button', { name: 'Fork' }).click()
  await expect(page).toHaveURL(new RegExp(`/notes/${FORKED}$`))
  expect(calls.find((c) => c.op === 'ForkNote')?.variables).toEqual({ noteId: NOTE_ID })
})

test('an edit made before switching tabs is kept, and saved once', async ({ page }) => {
  const calls = await mockApi(page, owner({ UpdateNoteDraft: () => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: [], conflictVersion: null, ...ok } }) }))
  await page.goto(`/notes/${NOTE_ID}`)
  const editor = page.getByRole('textbox', { name: 'Note content' })
  await editor.getByText('Halve the range each step.').click()
  await page.keyboard.press('End')
  await page.keyboard.type(' Always.')
  const tabs = page.getByRole('tablist', { name: 'Note sections' })
  await tabs.getByRole('tab', { name: 'Quiz' }).click()
  await tabs.getByRole('tab', { name: 'Content' }).click()
  await expect(editor.getByText('Halve the range each step. Always.')).toBeVisible()
  await expect.poll(() => calls.filter((c) => c.op === 'UpdateNoteDraft').length, { timeout: 10_000 }).toBe(1)
  expect(JSON.stringify(calls.find((c) => c.op === 'UpdateNoteDraft')?.variables)).toContain(CARD_B)
})

test('a flashcard’s front and back typed one after the other are both saved (no edit undoes the one before)', async ({ page }) => {
  const calls = await mockApi(page, owner({ UpdateNoteDraft: () => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: [], conflictVersion: null, ...ok } }) }, true))
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  await page.getByRole('button', { name: /^Flashcard/ }).click()
  await page.getByLabel('Front').fill('LIFO')
  await page.getByLabel('Back').fill('Last in, first out: a stack')
  const last = () =>
    calls
      .filter((c) => c.op === 'UpdateNoteDraft')
      .flatMap((c) => (c.variables.input as { ops: { type?: string; content?: unknown }[] }).ops)
      .filter((o) => o.type === 'flashcard')
      .at(-1)?.content
  await expect.poll(() => JSON.stringify(last() ?? null), { timeout: 10_000 }).toContain('Last in, first out')
  expect(JSON.stringify(last())).toContain('LIFO')
  await expect(page.getByLabel('Front')).toHaveValue('LIFO')
})
