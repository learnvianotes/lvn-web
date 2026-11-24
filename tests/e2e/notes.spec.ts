import { expect, test, type Page } from '@playwright/test'
import { CARD_A, CARD_B, NOTE_ID, USER, cards, meta, mockApi, p, page1 } from './support/notes-api'

/**
 * The notes app (lvn-backend §4, §12.2) against a mocked GraphQL API: what the editor sends when you type, how it
 * behaves offline, the reader, publishing and history. The real API runs in tests/e2e/live.spec.ts.
 */

const quiz = {
  __typename: 'Card',
  id: '01920000-0000-7000-8000-00000000c003',
  type: 'quiz',
  position: 'a2',
  revision: 1,
  content: { question: { type: 'doc', content: [p('Its running time?')] }, choices: [{ id: 'a', content: [{ type: 'text', text: 'O(n)' }] }, { id: 'b', content: [{ type: 'text', text: 'O(log n)' }] }], correct: ['b'], multiple: false },
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
  await expect(page.getByText('Correct')).toBeVisible()
})

test('an unverified owner is told how to publish', async ({ page }) => {
  await mockApi(
    page,
    {
      NoteToEdit: () => ({ note: { ...meta({ viewerCan: { __typename: 'NotePermissions', edit: true, publish: false, changeVisibility: false, delete: true, share: false, fork: true } }), cards: page1(cards) } }),
      UnverifiedGatedActions: () => ({ unverifiedGatedActions: ['note.publish'] }),
    },
    { emailVerified: false, verified: false },
  )
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByRole('button', { name: 'Publish' })).toBeDisabled()
  await expect(page.getByRole('link', { name: 'Verify your email' })).toHaveAttribute('href', '/profile#verify-email')
})

test('sharing can be held while visibility stays open, and Public follows the setting', async ({ page }) => {
  const published = { publishedAt: new Date().toISOString(), publishedVersion: { __typename: 'NoteVersion', id: NOTE_ID, number: 1, createdAt: new Date().toISOString() } }
  await mockApi(
    page,
    {
      NoteToEdit: () => ({ note: { ...meta(published), cards: page1(cards) } }),
      NoteShares: () => ({ note: { __typename: 'Note', id: NOTE_ID, visibility: 'PRIVATE', shares: [] } }),
      UnverifiedGatedActions: () => ({ unverifiedGatedActions: ['note.share'] }),
      PublicNotesRequireVerification: () => ({ publicNotesRequireVerification: true }),
    },
    { emailVerified: false, verified: false },
  )
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Share', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Share this note' })
  await expect(dialog.getByRole('radio', { name: /Private/ })).toBeEnabled()
  await expect(dialog.getByRole('radio', { name: /Shared/ })).toBeEnabled()
  await expect(dialog.getByRole('radio', { name: /Public/ })).toBeDisabled()
  await expect(dialog.getByRole('group', { name: 'Who can read it' }).getByRole('link', { name: 'Verify your email' })).toBeVisible()
  await expect(dialog.getByRole('region', { name: 'People' }).getByRole('link', { name: 'Verify your email' })).toBeVisible()
  await expect(dialog.getByLabel('Handle or email')).toBeDisabled()
})

test('publishing stays closed without a verify prompt when the email is already confirmed', async ({ page }) => {
  await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ viewerCan: { __typename: 'NotePermissions', edit: true, publish: false, changeVisibility: false, delete: true, share: false, fork: true } }), cards: page1(cards) } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByRole('button', { name: 'Publish' })).toBeDisabled()
  await expect(page.getByRole('link', { name: 'Verify your email' })).toHaveCount(0)
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
  await expect.poll(() => calls.filter((c) => c.op === 'NoteToEdit').length).toBeGreaterThanOrEqual(2)
})

const FRIEND = '01920000-0000-7000-8000-00000000bbbb'
const friend = { __typename: 'User', id: FRIEND, displayName: 'Ravi Kumar', handle: 'ravi' }
const noProblems = { userErrors: [] }

test('the owner shares with a person, changes their role and removes them', async ({ page }) => {
  let shares: { __typename: string; role: string; createdAt: string; user: typeof friend }[] = []
  let visibility = 'PRIVATE'
  const sharesAnswer = () => ({ note: { __typename: 'Note', id: NOTE_ID, visibility, shares } })
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    NoteShares: sharesAnswer,
    ShareNote: (v) => {
      visibility = 'SHARED'
      shares = [{ __typename: 'NoteShare', role: v.role as string, createdAt: new Date().toISOString(), user: friend }]
      return { shareNote: { note: { ...meta({ visibility }), shares }, ...noProblems } }
    },
    UnshareNote: () => {
      shares = []
      return { unshareNote: { note: { __typename: 'Note', id: NOTE_ID, shares }, ...noProblems } }
    },
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Share', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Share this note' })
  await expect(dialog.getByRole('radio', { name: /Private/ })).toBeChecked()
  // Public can be chosen before the note is published; readers see it once a version exists.
  await expect(dialog.getByRole('radio', { name: /Public/ })).toBeEnabled()
  await expect(dialog.getByText('Not shared with anyone yet.')).toBeVisible()

  await dialog.getByLabel('Handle or email').fill('@ravi')
  await dialog.getByLabel('What they can do').selectOption('EDITOR')
  await dialog.getByRole('button', { name: 'Add' }).click()
  await expect(dialog.getByText('Ravi Kumar', { exact: true })).toBeVisible()
  await expect(dialog.getByRole('radio', { name: /Shared/ })).toBeChecked()
  expect(calls.find((c) => c.op === 'ShareNote')?.variables).toEqual({ noteId: NOTE_ID, person: '@ravi', role: 'EDITOR' })

  await dialog.getByLabel('What Ravi Kumar can do').selectOption('VIEWER')
  await expect.poll(() => calls.filter((c) => c.op === 'ShareNote').at(-1)?.variables).toEqual({ noteId: NOTE_ID, person: '@ravi', role: 'VIEWER' })
  await dialog.getByRole('button', { name: 'Remove Ravi Kumar' }).click()
  await expect(dialog.getByText('Not shared with anyone yet.')).toBeVisible()
  expect(calls.find((c) => c.op === 'UnshareNote')?.variables).toEqual({ noteId: NOTE_ID, userId: FRIEND })
  await dialog.getByRole('button', { name: 'Done' }).click()
  await expect(page.getByTitle('Share this note')).toContainText('Shared')
})

test('a refusal from the server is shown in its own words', async ({ page }) => {
  await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ publishedAt: new Date().toISOString(), publishedVersion: { __typename: 'NoteVersion', id: NOTE_ID, number: 1, createdAt: new Date().toISOString() } }), cards: page1(cards) } }),
    NoteShares: () => ({ note: { __typename: 'Note', id: NOTE_ID, visibility: 'PRIVATE', shares: [] } }),
  })
  await page.route('**/graphql', async (route) => {
    const op = (route.request().postDataJSON() as { operationName?: string }).operationName
    if (op !== 'ChangeNoteVisibility') return route.fallback()
    return route.fulfill({ json: { data: null, errors: [{ message: 'Your account cannot make notes public.', extensions: { code: 'FORBIDDEN' } }] } })
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Share', exact: true }).click()
  const dialog = page.getByRole('dialog', { name: 'Share this note' })
  await dialog.getByText('Public', { exact: true }).click()
  await expect(dialog.getByRole('alert')).toHaveText('Your account cannot make notes public.')
  await expect(dialog.getByRole('radio', { name: /Private/ })).toBeChecked()
})

test('a reader makes a copy, which opens with a credit to the author', async ({ page }) => {
  const COPY = '01920000-0000-7000-8000-00000000a002'
  const calls = await mockApi(page, {
    NoteToEdit: (v) =>
      v.id === COPY
        ? { note: { ...meta({ id: COPY, forkedFrom: { __typename: 'ForkCredit', title: 'Searching', author: friend, note: { __typename: 'Note', id: NOTE_ID } } }), cards: page1([]) } }
        : { note: { ...meta({ viewerAccess: 'READER', owner: friend, visibility: 'PUBLIC' }), cards: page1(cards) } },
    ForkNote: () => ({ forkNote: { note: { __typename: 'Note', id: COPY }, ...noProblems } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('By Ravi Kumar')).toBeVisible()
  await page.getByRole('button', { name: 'Fork' }).click()
  await expect(page).toHaveURL(new RegExp(`/notes/${COPY}$`))
  await expect(page.getByText('Copied from Searching by Ravi Kumar')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Searching' })).toHaveAttribute('href', `/notes/${NOTE_ID}`)
  expect(calls.find((c) => c.op === 'ForkNote')?.variables).toEqual({ noteId: NOTE_ID })
})

test('Shared with me lists notes from other people with what you can do', async ({ page }) => {
  await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    SharedWithMe: () => ({
      sharedWithMe: {
        edges: [
          {
            __typename: 'NoteEdge',
            node: { __typename: 'Note', id: NOTE_ID, title: 'Graphs, explained', excerpt: 'Vertices and edges.', kind: 'NOTE', visibility: 'SHARED', draftUpdatedAt: null, publishedAt: new Date().toISOString(), deletedAt: null, cardCount: 4, folder: null, tags: [], viewerAccess: 'EDITOR', owner: { __typename: 'User', id: FRIEND, displayName: 'Ravi Kumar' } },
          },
        ],
        pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null },
      },
    }),
  })
  await page.goto('/notes?view=shared')
  await expect(page.getByRole('heading', { name: 'Shared with me', level: 1 })).toBeVisible()
  const tile = page.getByRole('link', { name: /Graphs, explained/ })
  await expect(tile).toContainText('From Ravi Kumar')
  await expect(tile).toContainText('Can edit')
  await expect(page.getByText('Start from')).toHaveCount(0)
})

const FILE_ID = '01920000-0000-7000-8000-00000000f001'
const PNG = Buffer.from('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360f8cfc0f01f0005000201a1d0f3a50000000049454e44ae426082', 'hex')
const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT, GET', 'access-control-allow-headers': '*' }

/** Pre-signed storage URLs: PUTs are recorded, GETs serve a tiny PNG. */
async function mockStorage(page: Page) {
  const puts: { url: string; type: string | undefined; size: number }[] = []
  await page.route('http://storage.test/**', async (route) => {
    const req = route.request()
    if (req.method() === 'OPTIONS') return route.fulfill({ status: 204, headers: CORS })
    if (req.method() === 'PUT') {
      puts.push({ url: req.url(), type: req.headers()['content-type'], size: req.postDataBuffer()?.length ?? 0 })
      return route.fulfill({ status: 200, headers: CORS })
    }
    return route.fulfill({ status: 200, headers: { ...CORS, 'content-type': 'image/png' }, body: PNG })
  })
  return puts
}

test('a picture chosen from Add a card uploads, shows at once and saves as an image card', async ({ page }) => {
  const puts = await mockStorage(page)
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    CreateNoteUpload: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: FILE_ID, uploadUrl: 'http://storage.test/put/original', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: 'image/png' }] }, ...noProblems } }),
    CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...noProblems } }),
    UpdateNoteDraft: (v) => saveAnswer(((v.input as { ops: { id: string }[] }).ops ?? []).map((o) => ({ __typename: 'CardOpResult', id: o.id, status: 'APPLIED', revision: 1, message: null }))),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('Halve the range each step.')).toBeVisible()
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  const chooser = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: /^Image/ }).click()
  await (await chooser).setFiles({ name: 'graph.png', mimeType: 'image/png', buffer: PNG })

  await expect(page.locator('img[src^="blob:"]')).toBeVisible()
  await page.getByLabel('Describe the picture for people who cannot see it').fill('A one-pixel graph')
  await expect.poll(() => calls.filter((c) => c.op === 'UpdateNoteDraft').flatMap((c) => (c.variables.input as { ops: { type: string; content: unknown }[] }).ops).filter((o) => o.type === 'image').at(-1)?.content, { timeout: 10_000 }).toEqual({ fileId: FILE_ID, alt: 'A one-pixel graph' })
  expect(calls.find((c) => c.op === 'CreateNoteUpload')?.variables).toEqual({ input: { fileName: 'graph.png', mimeType: 'image/png', sizeBytes: PNG.length, purpose: 'ATTACHMENT', parentId: NOTE_ID } })
  expect(puts).toEqual([{ url: 'http://storage.test/put/original', type: 'image/png', size: PNG.length }])
  expect(calls.find((c) => c.op === 'CompleteNoteUpload')?.variables).toEqual({ fileId: FILE_ID })
})

test('an upload the API refuses says why, in its words', async ({ page }) => {
  await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta(), cards: page1(cards) } }),
    CreateNoteUpload: () => ({ createUploadIntent: { intent: null, userErrors: [{ __typename: 'UserError', field: ['input', 'sizeBytes'], message: 'Files like this can be at most 20 MB.', code: 'VALIDATION' }] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  const chooser = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: /^Image/ }).click()
  await (await chooser).setFiles({ name: 'huge.png', mimeType: 'image/png', buffer: PNG })
  await expect(page.getByText('Files like this can be at most 20 MB.')).toBeVisible()
  await expect(page.getByRole('button', { name: /Choose a picture/ })).toBeVisible()
})

test('a reader sees the pictures and files of a note', async ({ page }) => {
  await mockStorage(page)
  const media = (id: string, fileName: string, mimeType: string) => ({ __typename: 'MediaFile', id, url: `http://storage.test/get/${fileName}`, expiresAt: new Date(Date.now() + 900_000).toISOString(), mimeType, fileName, sizeBytes: 2_400_000, width: null, height: null, durationMs: null, pageCount: null, thumbUrl: null, mediumUrl: null, largeUrl: null, posterUrl: null, playbackUrl: null })
  const PDF_ID = FILE_ID.replace('f001', 'f002')
  const withMedia = [
    ...cards.map((c) => ({ ...c, media: null })),
    { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c010', type: 'image', position: 'a2', revision: 1, content: { fileId: FILE_ID, alt: 'A search tree', caption: [{ type: 'text', text: 'Each step halves the range' }] }, media: media(FILE_ID, 'tree.png', 'image/png') },
    { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c011', type: 'file', position: 'a3', revision: 1, content: { fileId: PDF_ID }, media: media(PDF_ID, 'lecture-4.pdf', 'application/pdf') },
  ]
  await mockApi(page, { NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER', owner: friend }), cards: page1(withMedia) } }) })
  await page.goto(`/notes/${NOTE_ID}`)
  const picture = page.getByRole('img', { name: 'A search tree' })
  await expect(picture).toBeVisible()
  await expect(picture).toHaveAttribute('src', 'http://storage.test/get/tree.png')
  await expect(page.getByText('Each step halves the range')).toBeVisible()
  const file = page.getByRole('link', { name: /lecture-4\.pdf/ })
  await expect(file).toHaveAttribute('href', 'http://storage.test/get/lecture-4.pdf')
  await expect(file).toContainText('2.3 MB')
})

test('a reader sees the sizes, posters and transcodes the server made (ADR-0041)', async ({ page }) => {
  await mockStorage(page)
  const base = (id: string, fileName: string, mimeType: string) => ({ __typename: 'MediaFile', id, url: `http://storage.test/get/${fileName}`, expiresAt: new Date(Date.now() + 900_000).toISOString(), mimeType, fileName, sizeBytes: 2_400_000, width: null, height: null, durationMs: null, pageCount: null, thumbUrl: null, mediumUrl: null, largeUrl: null, posterUrl: null, playbackUrl: null })
  const variant = (fileName: string, name: string) => `http://storage.test/get/${fileName}/${name}`
  const VIDEO_ID = FILE_ID.replace('f001', 'f003')
  const PDF_ID = FILE_ID.replace('f001', 'f004')
  const withMedia = [
    ...cards.map((c) => ({ ...c, media: null })),
    { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c010', type: 'image', position: 'a2', revision: 1, content: { fileId: FILE_ID, alt: 'A search tree' }, media: { ...base(FILE_ID, 'tree.jpg', 'image/jpeg'), width: 2400, height: 1600, thumbUrl: variant('tree.jpg', 'thumb'), mediumUrl: variant('tree.jpg', 'medium'), largeUrl: variant('tree.jpg', 'large') } },
    { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c011', type: 'video', position: 'a3', revision: 1, content: { fileId: VIDEO_ID }, media: { ...base(VIDEO_ID, 'lecture.mov', 'video/quicktime'), durationMs: 60_000, posterUrl: variant('lecture.mov', 'poster'), playbackUrl: variant('lecture.mov', 'video720') } },
    { __typename: 'Card', id: '01920000-0000-7000-8000-00000000c012', type: 'file', position: 'a4', revision: 1, content: { fileId: PDF_ID }, media: { ...base(PDF_ID, 'chapter-2.pdf', 'application/pdf'), pageCount: 12 } },
  ]
  await mockApi(page, { NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER', owner: friend }), cards: page1(withMedia) } }) })
  await page.goto(`/notes/${NOTE_ID}`)
  const picture = page.getByRole('img', { name: 'A search tree' })
  await expect(picture).toHaveAttribute('src', variant('tree.jpg', 'medium'))
  await expect(picture).toHaveAttribute('srcset', `${variant('tree.jpg', 'thumb')} 320w, ${variant('tree.jpg', 'medium')} 960w, ${variant('tree.jpg', 'large')} 1920w`)
  await expect(picture).toHaveAttribute('width', '2400')
  const video = page.locator('video')
  await expect(video).toHaveAttribute('src', variant('lecture.mov', 'video720'))
  await expect(video).toHaveAttribute('poster', variant('lecture.mov', 'poster'))
  await expect(page.getByRole('link', { name: /chapter-2\.pdf/ })).toContainText('2.3 MB · 12 pages')
})
