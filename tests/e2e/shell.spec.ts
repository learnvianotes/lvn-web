import { expect, test, type Page } from '@playwright/test'
import { meta, mockApi, NOTE_ID } from './support/notes-api'
import { samplePdf } from './support/sample-pdf'

/**
 * Board A's frame (lvn-backend ADR-0076), checked for dead controls: every sidebar entry leads to a page that exists,
 * Create Note makes a note and opens it, Upload asks for a PDF, the search field opens the palette, the avatar opens
 * the account, and on a phone the menu holds the same entries. The landing's links lead to pages that exist too.
 */
const ENTRIES: [name: string, href: string][] = [
  ['Home', '/home'],
  ['Subjects', '/subjects'],
  ['My Notes', '/notes'],
  ['Quick notes', '/quick-notes'],
  ['Flashcards', '/flashcards'],
  ['Projects', '/projects'],
  ['Upload', '/upload'],
  ['Explore', '/search'],
  ['Groups', '/groups'],
  ['Classrooms', '/classes'],
  ['Exams', '/exams'],
  ['Quizzes', '/quizzes'],
  ['Contests', '/contests'],
  ['Rhythm', '/rhythm'],
  ['Resources', '/resources'],
  ['Community', '/community'],
  ['AI Assistant', '/ask'],
  ['Bookmarks', '/saved'],
  ['Guide', '/guide'],
]
const noProblems = { userErrors: [] }

/** A page the server has (any answer but 404 and 5xx: a signed-in page may send a visitor to sign in). */
async function exists(page: Page, href: string) {
  const res = await page.request.get(href, { maxRedirects: 0 })
  return res.status() < 400
}

test('every sidebar entry leads to a page that exists, and the page it opens is marked', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the sidebar is the menu on a phone (next test)')
  await mockApi(page, {})
  await page.goto('/home')
  const nav = page.getByRole('navigation', { name: 'Main' })
  const links = nav.getByRole('link')
  await expect(links).toHaveText(ENTRIES.map(([name]) => name))
  for (const [name, href] of ENTRIES) {
    await expect(nav.getByRole('link', { name, exact: true })).toHaveAttribute('href', href)
    expect(await exists(page, href), `${name} → ${href}`).toBe(true)
  }
  await expect(nav.getByRole('link', { name: 'Home' })).toHaveAttribute('aria-current', 'page')
  await nav.getByRole('link', { name: 'Exams' }).click()
  await expect(page).toHaveURL(/\/exams$/)
  await expect(nav.getByRole('link', { name: 'Exams' })).toHaveAttribute('aria-current', 'page')
  await expect(nav.getByRole('link', { name: 'Home' })).not.toHaveAttribute('aria-current', 'page')
  // Bookmarks holds saved notes and resources (ADR-0076).
  await nav.getByRole('link', { name: 'Bookmarks' }).click()
  await expect(page).toHaveURL(/\/saved$/)
  await expect(nav.getByRole('link', { name: 'Bookmarks' })).toHaveAttribute('aria-current', 'page')
  await expect(nav.getByRole('link', { name: 'Resources' })).not.toHaveAttribute('aria-current', 'page')
})

test('on a phone the menu holds the same entries; choosing one goes there and closes it', async ({ page }, info) => {
  test.skip(info.project.name !== 'phone', 'a phone has the menu')
  await mockApi(page, {})
  await page.goto('/home')
  await expect(page.getByRole('navigation', { name: 'Main' })).toBeHidden()
  await page.getByRole('button', { name: 'Menu' }).click()
  const menu = page.getByRole('dialog', { name: 'Menu' })
  await expect(menu.getByRole('navigation', { name: 'Main' }).getByRole('link')).toHaveText(ENTRIES.map(([name]) => name))
  await expect(menu.getByRole('button', { name: 'Create Note' })).toBeVisible()
  await expect(menu.getByRole('button', { name: 'Upload a PDF' })).toBeVisible()
  await menu.getByRole('link', { name: 'Rhythm' }).click()
  await expect(page).toHaveURL(/\/rhythm$/)
  await expect(menu).toHaveCount(0)
  await page.getByRole('button', { name: 'Menu' }).click()
  await menu.getByRole('button', { name: 'Close the menu' }).last().click()
  await expect(menu).toHaveCount(0)
})

test('public pages keep a signed-in learner in the app’s frame; a visitor gets the visitor’s header', async ({ page, browser }, info) => {
  await mockApi(page, { Resources: () => ({ resources: { __typename: 'ResourceConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }) })
  await page.goto('/resources')
  if (info.project.name === 'phone') {
    await page.getByRole('button', { name: 'Menu' }).click()
    await expect(page.getByRole('dialog', { name: 'Menu' }).getByRole('link', { name: 'Resources' })).toHaveAttribute('aria-current', 'page')
  } else await expect(page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'Resources' })).toHaveAttribute('aria-current', 'page')
  // The landing page is for visitors. Someone signed in is sent to Home, in the app's frame.
  await page.goto('/')
  await expect(page).toHaveURL(/\/home$/)
  const frame = info.project.name === 'phone' ? page.getByRole('dialog', { name: 'Menu' }) : page
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Menu' }).click()
  await expect(frame.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'Home' })).toHaveAttribute('aria-current', 'page')
  const visitor = await browser.newPage()
  await visitor.goto('/resources')
  await expect(visitor.getByRole('link', { name: 'Sign in' }).first()).toBeVisible()
  await expect(visitor.getByRole('button', { name: 'Create Note' })).toHaveCount(0)
  await visitor.close()
})

test('Create Note makes a note and opens it', async ({ page }, info) => {
  const calls = await mockApi(page, { CreateNote: () => ({ createNote: { note: { __typename: 'Note', id: NOTE_ID }, ...noProblems } }) })
  await page.goto('/home')
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Menu' }).click()
  await page.getByRole('button', { name: 'Create Note' }).click()
  await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}$`))
  expect(calls.filter((c) => c.op === 'CreateNote')).toHaveLength(1)
})

test('Upload a PDF asks for a PDF, and the one chosen opens in the reader inside a new note', async ({ page }, info) => {
  const FILE_ID = '01920000-0000-7000-8000-0000000f0001'
  const CORS = { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT', 'access-control-allow-headers': '*' }
  await page.route('http://storage.test/**', (route) => route.fulfill({ status: route.request().method() === 'OPTIONS' ? 204 : 200, headers: CORS }))
  const calls = await mockApi(page, {
    CreateNote: () => ({ createNote: { note: { __typename: 'Note', id: NOTE_ID }, ...noProblems } }),
    CreateNoteUpload: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: FILE_ID, uploadUrl: 'http://storage.test/put/pdf', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: 'application/pdf' }] }, ...noProblems } }),
    CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...noProblems } }),
    UpdateNoteDraft: () => ({ updateNoteDraft: { __typename: 'UpdateNoteDraftPayload', note: meta(), results: [], conflictVersion: null, ...noProblems } }),
  })
  await page.goto('/home')
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Menu' }).click()
  const chooser = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: 'Upload a PDF' }).click()
  const picked = await chooser
  expect(await picked.element().getAttribute('accept')).toBe('application/pdf')
  await picked.setFiles({ name: 'Graph_theory.pdf', mimeType: 'application/pdf', buffer: samplePdf() })
  await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}/read/${FILE_ID}$`), { timeout: 15_000 })
  expect(calls.find((c) => c.op === 'CreateNote')?.variables).toEqual({ input: { title: 'Graph theory' } })
})

test('the search field opens the palette, and the avatar opens the account', async ({ page }) => {
  await mockApi(page, {})
  await page.goto('/home')
  await expect(page.getByRole('link', { name: 'Your account' })).toHaveText('A')
  await page.getByRole('button', { name: 'Search', exact: true }).click()
  const palette = page.getByRole('dialog', { name: 'Search notes, people, groups and topics' })
  await expect(palette).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(palette).toBeHidden()
  await page.getByRole('link', { name: 'Your account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
})

test('“or ask AI”: the search field takes the words to Ask AI as a question, ready to send', async ({ page }) => {
  const aiState = { aiStatus: { __typename: 'AiStatus', available: true, reason: null }, myAiAllowance: { __typename: 'AiAllowance', usedToday: 0, limitToday: 200_000, resetsAt: new Date(Date.now() + 3_600_000).toISOString() } }
  const calls = await mockApi(page, { AiState: () => aiState, MyAiAnswers: () => ({ myAiAnswers: [] }) })
  await page.goto('/home')
  await page.getByRole('button', { name: 'Search', exact: true }).click()
  await page.getByRole('combobox').fill('why is a heap a tree')
  await page.getByRole('button', { name: 'Ask AI: “why is a heap a tree”' }).click()
  await expect(page).toHaveURL(/\/ask\?q=why%20is%20a%20heap%20a%20tree$/)
  await expect(page.getByLabel('Your question', { exact: true })).toHaveValue('why is a heap a tree')
  // Nothing is asked until the person sends it: AI has a daily allowance.
  expect(calls.filter((c) => c.op === 'AskAi')).toHaveLength(0)
})

test('the landing’s links all lead to pages that exist, and its sections are there', async ({ page }, info) => {
  await page.goto('/')
  const main = page.getByRole('main')
  await expect(main.getByRole('heading', { level: 1, name: 'Your Learning Community for a Brighter Tomorrow' })).toBeVisible()
  const tiles = page.getByRole('region', { name: 'What you can do' }).getByRole('link')
  await expect(tiles).toHaveCount(6)
  const hrefs = [
    ...(await tiles.evaluateAll((as) => as.map((a) => a.getAttribute('href')!))),
    await main.getByRole('link', { name: 'Get Started Free' }).getAttribute('href'),
    await main.getByRole('link', { name: 'Sign in' }).getAttribute('href'),
    await main.getByRole('link', { name: 'Browse subjects' }).getAttribute('href'),
  ]
  expect(hrefs).toEqual(['/notes', '/ask', '/groups', '/exams', '/review', '/community', '/sign-up', '/sign-in', '/subjects'])
  for (const href of hrefs) expect(await exists(page, href!), href!).toBe(true)
  await expect(page.locator('#features')).toHaveCount(1)
  await expect(page.locator('#subjects')).toHaveCount(1)
  // A visitor's header: Features, Subjects and Community from 768 px, Get Started from 640 px.
  const header = page.getByRole('banner')
  if (info.project.name === 'phone') return
  for (const name of ['Features', 'Subjects', 'Community', 'Get Started']) await expect(header.getByRole('link', { name, exact: true })).toBeVisible()
  await header.getByRole('link', { name: 'Features' }).click()
  await expect(page).toHaveURL(/\/#features$/)
  await header.getByRole('link', { name: 'Get Started' }).click()
  await expect(page).toHaveURL(/\/sign-up$/)
})

test('a public page keeps what happened on it when the app’s frame arrives with the session', async ({ page }) => {
  await mockApi(page, { UnsubscribeEmail: () => ({ unsubscribeEmail: { __typename: 'UnsubscribePayload', kind: 'DIGEST', userErrors: [] } }) })
  // The session is restored a moment after the page is used (a slow network, as on the live environment).
  await page.route('**/graphql', async (route) => {
    if ((route.request().postData() ?? '').includes('refreshSession')) await new Promise((r) => setTimeout(r, 1500))
    return route.fallback()
  })
  await page.goto('/unsubscribe?t=good')
  await page.getByRole('button', { name: 'Stop these emails' }).click()
  await expect(page.getByRole('status')).toHaveText("Done. You won't get the weekly email.")
  await expect(page.getByRole('link', { name: 'Your account' })).toBeVisible()
  await expect(page.getByRole('status').filter({ hasText: 'Done.' })).toHaveText("Done. You won't get the weekly email.")
})
