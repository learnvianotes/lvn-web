import { expect, test, type Page, type Route } from '@playwright/test'

/**
 * The notes app (lvn-backend §4, §12.2) against a mocked GraphQL API: what the editor sends when you type, how it
 * behaves offline, the reader, publishing and history. The real API runs in tests/e2e/live.spec.ts.
 */

const NOTE_ID = '01920000-0000-7000-8000-00000000a001'
const CARD_A = '01920000-0000-7000-8000-00000000c001'
const CARD_B = '01920000-0000-7000-8000-00000000c002'
const USER = '01920000-0000-7000-8000-00000000aaaa'

const p = (text: string) => ({ type: 'paragraph', content: [{ type: 'text', text }] })
const cards = [
  { __typename: 'Card', id: CARD_A, type: 'heading', position: 'a0', revision: 3, content: { level: 1, content: [{ type: 'text', text: 'Binary search' }] } },
  { __typename: 'Card', id: CARD_B, type: 'text', position: 'a1', revision: 5, content: { doc: { type: 'doc', content: [p('Halve the range each step.')] } } },
]
const quiz = {
  __typename: 'Card',
  id: '01920000-0000-7000-8000-00000000c003',
  type: 'quiz',
  position: 'a2',
  revision: 1,
  content: { question: { type: 'doc', content: [p('Its running time?')] }, choices: [{ id: 'a', content: [{ type: 'text', text: 'O(n)' }] }, { id: 'b', content: [{ type: 'text', text: 'O(log n)' }] }], correct: ['b'], multiple: false },
}

const meta = (over: Record<string, unknown> = {}) => ({
  __typename: 'Note',
  id: NOTE_ID,
  title: 'Searching',
  slug: 'searching',
  kind: 'NOTE',
  visibility: 'PRIVATE',
  viewerAccess: 'OWNER',
  viewerCan: { __typename: 'NotePermissions', edit: true, publish: true, changeVisibility: true, delete: true, share: true, fork: true },
  owner: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' },
  folder: null,
  tags: [],
  topics: [],
  draftRevision: 8,
  draftUpdatedAt: new Date().toISOString(),
  publishedAt: null,
  publishedVersion: null,
  forkingEnabled: true,
  cardCount: 2,
  deletedAt: null,
  ...over,
})
const page1 = (list: unknown[]) => ({ edges: list.map((node) => ({ __typename: 'CardEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } })

type Handler = (variables: Record<string, unknown>) => unknown

/** A signed-in session (refresh answered) and GraphQL by operation name; calls are recorded. */
async function mockApi(page: Page, handlers: Record<string, Handler>) {
  const calls: { op: string; variables: Record<string, unknown> }[] = []
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { query: string; operationName?: string; variables?: Record<string, unknown> }
    const op = body.operationName ?? (body.query.includes('refreshSession') ? 'Refresh' : 'unknown')
    calls.push({ op, variables: body.variables ?? {} })
    if (op === 'Refresh') {
      return route.fulfill({ json: { data: { refreshSession: { session: { accessToken: 'h.p.s', accessTokenExpiresAt: new Date(Date.now() + 900_000).toISOString() } } } } })
    }
    if (op === 'Viewer') return route.fulfill({ json: { data: { viewer: { __typename: 'User', id: USER, handle: 'asharao', displayName: 'Asha Rao', email: 'asha@example.com', emailVerified: true, registrationComplete: true, verified: true, verificationMethod: 'INSTITUTIONAL_EMAIL', globalRole: 'STUDENT', restrictedMinor: false, institutionalEmail: null, institutionalEmailStatus: 'NONE', institution: null } } } })
    const handler = handlers[op]
    if (!handler) return route.fulfill({ status: 500, json: { errors: [{ message: `unmocked ${op}` }] } })
    return route.fulfill({ json: { data: handler(body.variables ?? {}) } })
  })
  return calls
}

const saveAnswer = (results: unknown[]) => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results, conflictVersion: null, userErrors: [] } })

test('an empty notes page invites the first note, and New note opens it', async ({ page }) => {
  await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({ myNotes: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    CreateNote: () => ({ createNote: { note: { __typename: 'Note', id: NOTE_ID }, userErrors: [] } }),
    NoteToEdit: () => ({ note: { ...meta({ title: '', cardCount: 0 }), cards: page1([]) } }),
  })
  await page.goto('/notes')
  await expect(page.getByText('Start your first note')).toBeVisible()
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}$`))
  await expect(page.getByRole('textbox', { name: 'Note content' })).toBeVisible()
})

test('typing saves after a pause: the edited card with the revision the editor saw, and the title', async ({ page }) => {
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    UpdateNoteDraft: (v) => saveAnswer(((v.input as { ops: { id: string }[] }).ops ?? []).map((o) => ({ __typename: 'CardOpResult', id: o.id, status: 'APPLIED', revision: 6, message: null }))),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('Halve the range each step.')).toBeVisible()
  await page.getByText('Halve the range each step.').click()
  await page.keyboard.press('End')
  await page.keyboard.type(' Stop when it is empty.')
  await page.getByLabel('Title').fill('Searching, revised')
  await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 10_000 })
  const saves = calls.filter((c) => c.op === 'UpdateNoteDraft').map((c) => c.variables.input as { title?: string; ops: { kind: string; id: string; baseRevision?: number; content?: unknown }[] })
  const ops = saves.flatMap((s) => s.ops)
  expect(saves.some((s) => s.title === 'Searching, revised')).toBe(true)
  expect(ops.every((o) => o.id === CARD_B && o.kind === 'UPSERT')).toBe(true)
  expect(ops[0]).toMatchObject({ baseRevision: 5, content: { doc: { type: 'doc', content: [p('Halve the range each step. Stop when it is empty.')] } } })
  // The heading was not touched, so it was not sent.
  expect(ops.some((o) => o.id === CARD_A)).toBe(false)
})

test('offline, changes stay on this device and go out when the connection is back', async ({ page }) => {
  // A mocked API answers even when the browser is offline, so the outage is made here: saves fail until it ends.
  let offline = false
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    UpdateNoteDraft: (v) => saveAnswer(((v.input as { ops: { id: string }[] }).ops ?? []).map((o) => ({ __typename: 'CardOpResult', id: o.id, status: 'APPLIED', revision: 6, message: null }))),
  })
  await page.route('**/graphql', async (route) => {
    const op = (route.request().postDataJSON() as { operationName?: string }).operationName
    if (offline && op === 'UpdateNoteDraft') return route.abort('internetdisconnected')
    return route.fallback()
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('Halve the range each step.')).toBeVisible()
  offline = true
  await page.getByLabel('Title').fill('Written on the train')
  await expect(page.getByText(/Offline — kept on this device/)).toBeVisible({ timeout: 10_000 })
  // The draft is in IndexedDB while it waits.
  const mirrored = await page.evaluate(() => new Promise<number>((resolve) => {
    const req = indexedDB.open('lvn-notes')
    req.onsuccess = () => {
      const count = req.result.transaction('drafts').objectStore('drafts').count()
      count.onsuccess = () => resolve(count.result)
    }
  }))
  expect(mirrored).toBe(1)
  offline = false
  await page.evaluate(() => window.dispatchEvent(new Event('online')))
  await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 15_000 })
  expect(calls.some((c) => c.op === 'UpdateNoteDraft' && (c.variables.input as { title?: string }).title === 'Written on the train')).toBe(true)
})

test('a reader sees the published version, read-only, and can try the quiz', async ({ page }) => {
  await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER', viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true }, draftRevision: null, publishedAt: new Date().toISOString() }), cards: page1([...cards, quiz]) } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByRole('heading', { level: 1, name: 'Searching' })).toBeVisible()
  await expect(page.getByText('By Asha Rao')).toBeVisible()
  await expect(page.getByRole('textbox', { name: 'Note content' })).toHaveCount(0)
  await page.getByRole('radio', { name: 'O(log n)' }).click()
  await page.getByRole('button', { name: 'Check' }).click()
  await expect(page.getByText('Correct!')).toBeVisible()
})

test('an unverified owner is told how to publish', async ({ page }) => {
  await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ viewerCan: { __typename: 'NotePermissions', edit: true, publish: false, changeVisibility: false, delete: true, share: false, fork: true } }), cards: page1(cards) } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByRole('button', { name: 'Publish' })).toBeDisabled()
  await expect(page.getByRole('link', { name: 'Verify now' })).toHaveAttribute('href', '/profile')
})

test('publishing names the version, and history previews and restores one', async ({ page }, info) => {
  const version = { __typename: 'NoteVersion', id: '01920000-0000-7000-8000-00000000e001', number: 1, kind: 'PUBLISHED', title: 'Searching (v1)', createdAt: new Date().toISOString(), createdBy: { __typename: 'User', id: USER, displayName: 'Asha Rao' } }
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    PublishNote: () => ({ publishNote: { note: meta({ publishedAt: new Date().toISOString(), publishedVersion: { __typename: 'NoteVersion', id: version.id, number: 1, createdAt: version.createdAt } }), userErrors: [] } }),
    NoteVersions: () => ({ note: { __typename: 'Note', id: NOTE_ID, versions: { edges: [{ __typename: 'NoteVersionEdge', node: version }], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
    NoteVersionPreview: () => ({ note: { __typename: 'Note', id: NOTE_ID, version: { ...version, cards: page1([cards[1]]) } } }),
    RestoreNoteVersion: () => ({ restoreNoteVersion: { note: { __typename: 'Note', id: NOTE_ID }, userErrors: [] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Publish' }).click()
  await expect(page.getByText('Published as version 1.')).toBeVisible()
  // Phones keep History in the More menu.
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'More' }).click()
  await page.getByRole('button', { name: 'History' }).click()
  const history = page.getByRole('dialog', { name: 'Version history' })
  await history.getByRole('button', { name: /Version 1 · published/ }).click()
  await expect(history.getByRole('heading', { name: 'Searching (v1)' })).toBeVisible()
  await history.getByRole('button', { name: 'Restore this version' }).click()
  await expect(history).toBeHidden()
  expect(calls.find((c) => c.op === 'RestoreNoteVersion')!.variables).toEqual({ noteId: NOTE_ID, versionId: version.id })
  // The page reloads the note after a restore.
  expect(calls.filter((c) => c.op === 'NoteToEdit').length).toBeGreaterThanOrEqual(2)
})
