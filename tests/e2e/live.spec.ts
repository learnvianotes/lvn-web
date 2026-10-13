import { execFileSync } from 'node:child_process'
import { randomUUID } from 'node:crypto'
import { expect, test, type Page } from '@playwright/test'
import { PDF_TEXT, samplePdf } from './support/sample-pdf'

/**
 * The deployed stack with nothing mocked: web, API, database, Redis and mail of an environment — the local environment
 * on its VM (lvn-backend ADR-0036) or the sandbox. Skipped unless E2E_LIVE is set:
 *
 *   E2E_LIVE=1 E2E_BASE_URL=http://127.0.0.1:8080 pnpm test:e2e tests/e2e/live.spec.ts
 *
 * Against the development servers, where the API has its own origin, also set E2E_API_URL (…:4000/graphql).
 *
 * Each run makes one account per browser, live-<time>-<project>@example.com, and leaves it in place.
 *
 * Tests that need a teacher also need E2E_VM, the local environment's vm.sh: roles are set in its database, as
 * lvn-backend's lifecycle check does, since no API gives them.
 */
test.skip(!process.env.E2E_LIVE || !process.env.E2E_BASE_URL, 'needs a deployed environment: E2E_LIVE=1 E2E_BASE_URL=<public url>')

/** Opens a sidebar entry: the sidebar from 1024 px, the menu below (lvn-backend ADR-0076). */
async function fromSidebar(page: Page, name: string) {
  const menu = page.getByRole('button', { name: 'Menu' })
  if (await menu.isVisible()) await menu.click()
  await page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name, exact: true }).click()
}

test('a new learner signs up with email, keeps the session across a reload, signs out and signs in again', async ({ page }, info) => {
  const email = `live-${Date.now()}-${info.project.name}@example.com`
  const password = `live passphrase ${Date.now()}`

  await page.goto('/')
  const main = page.getByRole('main')
  await expect(main.getByRole('heading', { name: 'Your Learning Community for a Brighter Tomorrow' })).toBeVisible()
  await main.getByRole('link', { name: 'Get Started Free' }).click()
  await expect(page).toHaveURL(/\/sign-up$/)

  await page.getByLabel('Your name').fill('Live Test')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await expect(page.getByRole('heading', { name: 'Live Test' })).toBeVisible()

  // The access token lives only in memory: after a reload the HttpOnly refresh cookie brings the session back.
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Live Test' })).toBeVisible()

  await page.getByRole('button', { name: 'Sign out' }).click()
  await expect(page).toHaveURL(/\/$/)
  await page.goto('/profile')
  await expect(page).toHaveURL(/\/sign-in\?next=%2Fprofile$/)

  await page.getByLabel('Email').fill(email)
  await page.getByLabel('Password').fill(password)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await expect(page.getByRole('heading', { name: 'Live Test' })).toBeVisible()
})

test('offers Google when the environment has it', async ({ page, request }) => {
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ signInOptions { google } }' } })
  const google = ((await res.json()) as { data: { signInOptions: { google: boolean } } }).data.signInOptions.google
  test.skip(!google, 'Google sign-in is off in this environment')
  await page.goto('/sign-in')
  await expect(page.getByRole('button', { name: 'Continue with Google' })).toBeVisible()
})

test('a learner writes a note: cards from the slash menu, autosave, back after a reload, trash and restore', async ({ page }, info) => {
  const email = `live-notes-${Date.now()}-${Math.random().toString(36).slice(2, 8)}-${info.project.name}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Writer')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await fromSidebar(page, 'My Notes')
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  await page.getByLabel('Title').fill('Stacks and queues')
  const editor = page.getByRole('textbox', { name: 'Note content' })
  await editor.click()
  await page.keyboard.type('A queue is first in, first out.')
  if (info.project.name === 'phone') {
    // Phones have no shortcut keys (and Chrome on Android hands Enter to the editor as input, not as a key): tap.
    await page.getByRole('button', { name: 'Add a card', exact: true }).click()
    await page.getByRole('button', { name: /^Heading/ }).click()
  } else {
    await page.keyboard.press('Control+Shift+Enter')
    await page.keyboard.type('/heading')
    await page.keyboard.press('Enter')
  }
  await page.keyboard.type('Practice')
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  await page.getByRole('button', { name: /^Flashcard/ }).click()
  await page.getByLabel('Front').fill('LIFO')
  // The save that carries the back of the card, not an earlier one that happened to say Saved.
  const backSaved = page.waitForResponse((r) => r.url().endsWith('/graphql') && /UpdateNoteDraft/.test(r.request().postData() ?? '') && (r.request().postData() ?? '').includes('Last in, first out'), { timeout: 15_000 })
  await page.getByLabel('Back').fill('Last in, first out: a stack')
  await backSaved
  await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 15_000 })

  await page.reload()
  await expect(editor.getByText('A queue is first in, first out.')).toBeVisible()
  await expect(page.getByLabel('Back')).toHaveValue('Last in, first out: a stack')
  // The outline: beside the note on wide screens, in the Contents sheet on phones.
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Contents' }).click()
  await expect(page.getByRole(info.project.name === 'phone' ? 'dialog' : 'navigation', { name: info.project.name === 'phone' ? 'Contents' : 'Outline' }).getByRole('button', { name: 'Practice' })).toBeVisible()
  if (info.project.name === 'phone') await page.keyboard.press('Escape')

  page.once('dialog', (d) => void d.accept())
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'More' }).click()
  await page.getByRole('button', { name: 'Move to trash' }).click()
  await expect(page).toHaveURL(/\/notes$/)
  await expect(page.getByText('Stacks and queues')).toHaveCount(0)
  await page.getByRole('link', { name: 'Trash' }).click()
  await page.getByRole('button', { name: 'Restore' }).click()
  await page.getByRole('link', { name: 'All notes' }).click()
  await expect(page.getByRole('link', { name: /^Stacks and queues edited/ })).toBeVisible()
})

test('a learner adds a picture to a note: it goes to storage, and is there after a reload', async ({ page }, info) => {
  const png = Buffer.from('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360f8cfc0f01f0005000201a1d0f3a50000000049454e44ae426082', 'hex')
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Picture')
  await page.getByLabel('Email', { exact: true }).fill(`live-media-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await page.goto('/notes')
  await page.getByRole('button', { name: 'New note' }).first().click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  await page.getByLabel('Title').fill('With a picture')
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  const chooser = page.waitForEvent('filechooser')
  await page.getByRole('button', { name: /^Image/ }).click()
  await (await chooser).setFiles({ name: 'dot.png', mimeType: 'image/png', buffer: png })
  await page.getByLabel('Describe the picture for people who cannot see it').fill('A dot')
  await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 15_000 })

  // After a reload the picture comes from storage through a pre-signed read URL, and loads.
  await page.reload()
  const picture = page.getByRole('img', { name: 'A dot' })
  await expect(picture).toHaveAttribute('src', /^https?:\/\/.+X-Amz-Signature=/)
  await expect.poll(() => picture.evaluate((img) => (img as HTMLImageElement).naturalWidth)).toBe(1)
})

test('a learner reads a PDF beside a new note: a highlight and a passage in the note stay after a reload', async ({ page }, info) => {
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Reader')
  await page.getByLabel('Email', { exact: true }).fill(`live-pdf-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await page.goto('/notes')
  await page.getByTestId('read-pdf-input').setInputFiles({ name: 'Biology_chapter_3.pdf', mimeType: 'application/pdf', buffer: samplePdf() })
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}\/read\/[0-9a-f-]{36}$/, { timeout: 20_000 })
  const line = (text: string) => page.locator('.textLayer span', { hasText: text })
  await expect(line(PDF_TEXT.page1[1]!)).toBeAttached({ timeout: 20_000 })
  const select = (text: string) =>
    page.evaluate((words) => {
      const span = [...document.querySelectorAll('.textLayer span')].find((s) => s.textContent === words)!
      const range = document.createRange()
      range.selectNodeContents(span)
      document.getSelection()!.removeAllRanges()
      document.getSelection()!.addRange(range)
    }, text)

  await select(PDF_TEXT.page1[1]!)
  await page.getByRole('dialog', { name: 'Selected words' }).getByRole('button', { name: 'Highlight in yellow' }).click()
  await expect(page.locator('.lvn-mark-highlight')).toHaveCount(1)
  await select(PDF_TEXT.page1[2]!)
  await page.getByRole('dialog', { name: 'Selected words' }).getByRole('button', { name: 'Add to notes' }).click()
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Show notes' }).click()
  await expect(page.getByText('Saved', { exact: true })).toBeVisible({ timeout: 15_000 })

  await page.reload()
  await expect(line(PDF_TEXT.page1[1]!)).toBeAttached({ timeout: 20_000 })
  await expect(page.locator('.lvn-mark-highlight[data-color="YELLOW"]')).toHaveCount(1)
  await expect(page.locator('.lvn-mark-anchor')).toHaveCount(1)
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Show notes' }).click()
  await expect(page.getByRole('textbox', { name: 'Note content' }).getByText(PDF_TEXT.page1[2]!)).toBeVisible()
  await expect(page.locator('.lvn-anchor-chip')).toHaveText('↗ p. 1')
})

test('a learner converts a PDF into cards with the real engine, and checks them beside it', async ({ page }, info) => {
  test.setTimeout(240_000)
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Converter')
  await page.getByLabel('Email', { exact: true }).fill(`live-convert-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await page.goto('/notes')
  await page.getByTestId('read-pdf-input').setInputFiles({ name: 'Biology_chapter_3.pdf', mimeType: 'application/pdf', buffer: samplePdf() })
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}\/read\/[0-9a-f-]{36}$/, { timeout: 20_000 })
  const first = page.url()
  await page.getByRole('button', { name: 'Convert to cards' }).click()
  await page.getByRole('dialog', { name: 'Convert this PDF into cards' }).getByRole('button', { name: 'Convert' }).click()
  await expect.poll(() => page.url(), { timeout: 20_000 }).not.toBe(first)
  // The engine counts the pages, reads the PDF (models load on its first job) and the cards arrive.
  await expect(page.getByText(/Made \d+ cards? from 2 pages\./)).toBeVisible({ timeout: 200_000 })
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Show notes' }).click()
  const notes = page.getByRole('textbox', { name: 'Note content' })
  await expect(notes.getByText('Cells release energy from glucose.')).toBeVisible()
  await expect(page.locator('.lvn-anchor-chip').first()).toBeVisible()
  await expect(page.locator('.lvn-mark-anchor').first()).toBeAttached()
})

test('a notification reaches the bell live: the data export the worker builds (lvn-backend ADR-0042)', async ({ page }, info) => {
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Bell')
  await page.getByLabel('Email', { exact: true }).fill(`live-bell-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await expect(page.getByRole('link', { name: 'Notifications', exact: true })).toBeVisible()

  // The worker builds the archive and notifies; the count changes on this page without a reload.
  await page.getByRole('button', { name: 'Prepare my archive' }).click()
  await expect(page.getByRole('link', { name: 'Notifications, 1 unread' })).toBeVisible({ timeout: 60_000 })
  await page.getByRole('link', { name: 'Notifications, 1 unread' }).click()
  await page.getByRole('button', { name: /Your data export is ready to download/ }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await expect(page.getByRole('link', { name: 'Notifications', exact: true })).toBeVisible()
})

test('a new learner opens their own profile from their account, rendered by the server (lvn-backend ADR-0043)', async ({ page }, info) => {
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Profile')
  await page.getByLabel('Email', { exact: true }).fill(`live-profile-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await page.getByRole('link', { name: 'Followers, following and blocked people' }).click()
  await expect(page.getByText('Nobody follows you yet.')).toBeVisible()
  await page.getByRole('link', { name: 'See your profile' }).click()
  await expect(page).toHaveURL(/\/u\/[a-z0-9]+$/)
  await expect(page.getByRole('heading', { level: 1, name: /Live Profile/ })).toBeVisible()
  await expect(page.getByRole('link', { name: '0 followers · 0 following' })).toBeVisible()
  await expect(page.getByText('No public notes yet.')).toBeVisible()
})

test('the documents the web shows are the version the API asks people to accept', async ({ request }) => {
  const { TERMS_VERSION } = await import('../../features/legal/documents')
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ termsVersion }' } })
  expect(((await res.json()) as { data: { termsVersion: string } }).data.termsVersion).toBe(TERMS_VERSION)
})

/** The API as a teacher made for the test would call it; and SQL on the local environment's database (E2E_VM). */
const apiUrl = () => process.env.E2E_API_URL ?? `${process.env.E2E_BASE_URL!.replace(/\/$/, '')}/graphql`
async function api<T>(query: string, variables: Record<string, unknown> = {}, token?: string): Promise<T> {
  const res = await fetch(apiUrl(), { method: 'POST', headers: { 'content-type': 'application/json', ...(token ? { authorization: `Bearer ${token}` } : {}) }, body: JSON.stringify({ query, variables }) })
  const body = (await res.json()) as { data?: T; errors?: { message: string }[] }
  if (body.errors?.length) throw new Error(body.errors[0]!.message)
  return body.data!
}
const sql = (statement: string) => execFileSync(process.env.E2E_VM!, ['ssh', `docker exec lvn-local-postgres psql -U lvn -d lvn -c "${statement.replace(/"/g, '\\"')}"`], { stdio: 'pipe' })

test('a learner joins a class with its code, is let in, and reads the announcement (lvn-backend ADR-0046)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a teacher')
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email: `live-teacher-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Teacher', dateOfBirth: '1990-01-01', acceptedTermsVersion: termsVersion },
  })
  const teacher = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'TEACHER', "globalRole" = 'TEACHER' WHERE id = '${teacher.user.id}'`)
  const made = await api<{ createClassroom: { classroom: { id: string; joinCode: string } } }>('mutation { createClassroom(input: { name: "Live physics" }) { classroom { id joinCode } } }', {}, teacher.accessToken)
  const { id: classroomId, joinCode } = made.createClassroom.classroom

  const email = `live-class-${stamp}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Learner')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  // Asking to join needs a verified account (ADR-0017).
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE email = '${email}'`)

  await page.goto('/classes')
  await page.getByLabel('Class code').fill(joinCode.toLowerCase())
  await page.getByRole('button', { name: 'Find' }).click()
  await expect(page.getByRole('heading', { name: 'Live physics' })).toBeVisible()
  await expect(page.getByText('Teacher: Live Teacher')).toBeVisible()
  await page.getByRole('button', { name: 'Ask to join' }).click()
  await expect(page.getByText('Your request is waiting for your teacher.')).toBeVisible()

  const asked = await api<{ classroom: { joinRequests: { id: string }[] } }>('query ($id: UUID!) { classroom(id: $id) { joinRequests { id } } }', { id: classroomId }, teacher.accessToken)
  await api('mutation ($input: ReviewClassroomJoinRequestInput!) { reviewClassroomJoinRequest(input: $input) { classroom { id } } }', { input: { requestId: asked.classroom.joinRequests[0]!.id, decision: 'APPROVED' } }, teacher.accessToken)
  await api('mutation ($input: CreateClassroomPostInput!) { createClassroomPost(input: $input) { classroom { id } } }', { input: { classroomId, body: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Live test on Friday' }] }] } } }, teacher.accessToken)
  // Both reach the bell live: the answer, then the announcement.
  await expect(page.getByRole('link', { name: 'Notifications, 2 unread' })).toBeVisible({ timeout: 60_000 })
  await page.getByRole('link', { name: 'Notifications, 2 unread' }).click()
  await page.getByRole('button', { name: /Live Teacher posted an announcement in Live physics/ }).click()
  await expect(page).toHaveURL(new RegExp(`/classes/${classroomId}$`))
  await expect(page.getByText('Live test on Friday')).toBeVisible()
  await expect(page.getByTestId('class-code')).toHaveCount(0)
  // A question under the announcement goes to the staff only (ADR-0047).
  await page.getByRole('button', { name: 'Comment', exact: true }).click()
  await page.getByLabel('Write a comment').fill('Which chapters?')
  await page.getByRole('button', { name: 'Comment', exact: true }).last().click()
  await expect(page.getByText('Private thread')).toBeVisible()
  const postId = (await api<{ classroom: { posts: { edges: { node: { id: string } }[] } } }>('query ($id: UUID!) { classroom(id: $id) { posts { edges { node { id } } } } }', { id: classroomId }, teacher.accessToken)).classroom.posts.edges[0]!.node.id
  const seen = await api<{ discussion: { comments: { edges: { node: { private: boolean; author: { displayName: string } } }[] } } }>('query ($target: CommentTargetInput!) { discussion(target: $target) { comments { edges { node { private author { displayName } } } } } }', { target: { type: 'CLASSROOM_POST', id: postId } }, teacher.accessToken)
  expect(seen.discussion.comments.edges.map((e) => e.node)).toEqual([{ private: true, author: { displayName: 'Live Learner' } }])

  // The announcement was also emailed (ADR-0050), with one-click unsubscribe; needs E2E_MAILPIT (Mailpit's web address).
  const mailpit = process.env.E2E_MAILPIT
  if (!mailpit) return
  let message: { ID: string } | undefined
  await expect
    .poll(async () => {
      const found = (await (await fetch(`${mailpit}/api/v1/search?query=${encodeURIComponent(`to:"${email}" subject:"posted in Live physics"`)}`)).json()) as { messages: { ID: string }[] }
      message = found.messages[0]
      return !!message
    }, { timeout: 60_000 })
    .toBe(true)
  const full = (await (await fetch(`${mailpit}/api/v1/message/${message!.ID}`)).json()) as { Text: string }
  expect(full.Text).toContain('Live test on Friday')
  const headers = (await (await fetch(`${mailpit}/api/v1/message/${message!.ID}/headers`)).json()) as Record<string, string[]>
  expect(headers['List-Unsubscribe-Post']).toEqual(['List-Unsubscribe=One-Click'])
  const oneClick = headers['List-Unsubscribe']![0]!.replace(/^<|>$/g, '')
  // The visible link asks for a click; the mail client's POST needs none.
  const visible = /https?:\/\/\S+\/unsubscribe\?t=[\w.-]+/.exec(full.Text)![0]
  await page.goto(visible)
  await page.getByRole('button', { name: 'Stop these emails' }).click()
  await expect(page.getByRole('status')).toHaveText("Done. You won't get emails about class announcements.")
  expect((await page.request.post(oneClick, { form: { 'List-Unsubscribe': 'One-Click' } })).status()).toBe(200)
})

test('a learner starts a project workspace, a teacher mentors it and answers a doubt (lvn-backend ADR-0048)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a teacher')
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email: `live-mentor-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Mentor', dateOfBirth: '1990-01-01', acceptedTermsVersion: termsVersion },
  })
  const mentor = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'TEACHER', "globalRole" = 'TEACHER' WHERE id = '${mentor.user.id}'`)
  const mentorHandle = (await api<{ viewer: { handle: string } }>('{ viewer { handle } }', {}, mentor.accessToken)).viewer.handle

  const email = `live-project-${stamp}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Builder')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE email = '${email}'`)

  await page.goto('/groups')
  await page.getByRole('button', { name: 'New group' }).click()
  const dialog = page.getByRole('dialog', { name: 'New group' })
  await dialog.getByLabel('Name').fill(`Live project ${stamp}`)
  await dialog.getByLabel(/Project workspace/).check()
  await dialog.getByLabel('Private').check()
  await dialog.getByRole('button', { name: 'Create group' }).click()
  await expect(page).toHaveURL(/\/groups\/[0-9a-f-]+$/)
  const groupId = page.url().split('/').pop()!
  await page.getByRole('tab', { name: 'Members' }).click()
  await page.getByLabel("A teacher's handle or email").fill(mentorHandle)
  await page.getByRole('button', { name: 'Invite', exact: true }).click()
  await expect(page.getByText('Invite sent. It lasts 14 days.')).toBeVisible()
  const invites = await api<{ myMentorInvites: { id: string; group: { id: string } }[] }>('{ myMentorInvites { id group { id } } }', {}, mentor.accessToken)
  const invite = invites.myMentorInvites.find((i) => i.group.id === groupId)!
  await api('mutation ($input: AnswerMentorInviteInput!) { answerMentorInvite(input: $input) { group { id } } }', { input: { inviteId: invite.id, accept: true } }, mentor.accessToken)

  await page.getByRole('tab', { name: 'Doubts' }).click()
  await page.getByRole('button', { name: 'Ask a doubt' }).click()
  await page.getByLabel('Your question').fill('Why a min-heap for the scheduler?')
  await page.getByLabel('Details').fill('We pick the next job by deadline.')
  await page.getByRole('button', { name: 'Ask', exact: true }).click()
  await expect(page).toHaveURL(/\/doubts\/[0-9a-f-]+$/)
  const doubtId = page.url().split('/').pop()!
  await api('mutation ($input: AnswerDoubtInput!) { answerDoubt(input: $input) { doubt { id } } }', { input: { doubtId, body: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'The earliest deadline is always on top.' }] }] } } }, mentor.accessToken)
  // The answer reaches the bell live; the doubt shows it, marked as the mentor's.
  await expect(page.getByRole('link', { name: 'Notifications, 1 unread' })).toBeVisible({ timeout: 60_000 })
  await page.reload()
  await expect(page.getByText('The earliest deadline is always on top.')).toBeVisible()
  await expect(page.getByText('Mentor', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Mark resolved' }).click()
  await expect(page.getByText('This doubt is resolved. Reopen it to answer again.')).toBeVisible()
})

test('a group’s owner hides a reported post from the Reports tab, and puts it back after the author’s appeal (lvn-backend ADR-0051)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to verify accounts')
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const account = async (who: string, name: string) => {
    const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
      input: { email: `live-${who}-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: name, dateOfBirth: '2000-01-01', acceptedTermsVersion: termsVersion },
    })
    sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE id = '${up.signUp.session.user.id}'`)
    return up.signUp.session
  }
  const writer = await account('writer', 'Live Writer')
  const reporter = await account('reporter', 'Live Reporter')

  const email = `live-lead-${stamp}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Lead')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE email = '${email}'`)

  await page.goto('/groups')
  await page.getByRole('button', { name: 'New group' }).click()
  const dialog = page.getByRole('dialog', { name: 'New group' })
  await dialog.getByLabel('Name').fill(`Live club ${stamp}`)
  await dialog.getByLabel('Public').check()
  await dialog.getByLabel('Let people join without approval').check()
  await dialog.getByRole('button', { name: 'Create group' }).click()
  await expect(page).toHaveURL(/\/groups\/[0-9a-f-]+$/)
  const groupId = page.url().split('/').pop()!
  for (const who of [writer, reporter]) await api('mutation ($id: UUID!) { joinGroup(input: { groupId: $id }) { group { id } } }', { id: groupId }, who.accessToken)
  const doc = { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'You are all hopeless at heaps.' }] }] }
  const postId = (await api<{ createGroupPost: { post: { id: string } } }>('mutation ($input: CreateGroupPostInput!) { createGroupPost(input: $input) { post { id } } }', { input: { groupId, body: doc } }, writer.accessToken)).createGroupPost.post.id
  await api('mutation ($input: ReportContentInput!) { reportContent(input: $input) { ok } }', { input: { entityType: 'GROUP_POST', entityId: postId, reason: 'HARASSMENT', details: 'Rude to everyone' } }, reporter.accessToken)

  await page.reload()
  await page.getByRole('tab', { name: 'Reports' }).click()
  const card = page.getByRole('article', { name: 'Post' })
  await expect(card.getByText('You are all hopeless at heaps.')).toBeVisible()
  await expect(card.getByText('Rude to everyone')).toBeVisible()
  await card.getByLabel(/^Reason/).fill('Be kind to the others.')
  await card.getByRole('button', { name: 'Hide' }).click()
  await expect(page.getByText('Nothing to review. Thank you!')).toBeVisible()

  type Seen = { group: { posts: { edges: { node: { id: string; moderation: string; moderationReason: string | null } }[] } } }
  const postsOf = async (token: string) => (await api<Seen>('query ($id: UUID!) { group(id: $id) { posts { edges { node { id moderation moderationReason } } } } }', { id: groupId }, token)).group.posts.edges.map((e) => e.node)
  expect(await postsOf(writer.accessToken)).toEqual([{ id: postId, moderation: 'HIDDEN', moderationReason: 'Be kind to the others.' }])
  expect(await postsOf(reporter.accessToken)).toEqual([])
  await expect
    .poll(async () => (await api<{ notifications: { edges: { node: { category: string; data: unknown } }[] } }>('{ notifications(first: 5) { edges { node { category data } } } }', {}, writer.accessToken)).notifications.edges.map((e) => e.node), { timeout: 30_000 })
    .toContainEqual({ category: 'MODERATION', data: { kind: 'HIDDEN', entityType: 'GROUP_POST' } })

  await api('mutation ($input: AppealModerationInput!) { appealModeration(input: $input) { ok } }', { input: { entityType: 'GROUP_POST', entityId: postId, message: 'I take it back, sorry.' } }, writer.accessToken)
  await page.reload()
  await page.getByRole('tab', { name: 'Reports' }).click()
  await expect(card.getByText('I take it back, sorry.')).toBeVisible()
  await card.getByRole('button', { name: 'Put it back' }).click()
  await expect(page.getByText('Nothing to review. Thank you!')).toBeVisible()
  expect(await postsOf(reporter.accessToken)).toEqual([{ id: postId, moderation: 'OK', moderationReason: null }])
})

test('a learner finds a public group, joins it and posts; the owner reads the post (lvn-backend ADR-0045)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to verify accounts')
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email: `live-owner-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Owner', dateOfBirth: '1995-01-01', acceptedTermsVersion: termsVersion },
  })
  const owner = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE id = '${owner.user.id}'`)
  const name = `Live algorithms ${stamp}`
  const groupId = (await api<{ createGroup: { group: { id: string } } }>('mutation ($input: CreateGroupInput!) { createGroup(input: $input) { group { id } } }', { input: { name, privacy: 'PUBLIC', joinPolicy: 'OPEN' } }, owner.accessToken)).createGroup.group.id

  const email = `live-joiner-${stamp}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Joiner')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE email = '${email}'`)

  await page.goto('/groups')
  await page.getByLabel('Search public groups').fill(name)
  await page.getByRole('link', { name: new RegExp(name) }).click()
  await expect(page).toHaveURL(new RegExp(`/groups/${groupId}$`))
  await page.getByRole('button', { name: 'Join', exact: true }).click()
  await page.getByLabel('Write a post').fill('Hello from the web')
  await page.getByRole('button', { name: 'Post', exact: true }).click()
  // The box empties once the API has the post; until then its own words could pass for the post in the list.
  await expect(page.getByLabel('Write a post')).toHaveValue('')
  await expect(page.getByRole('tabpanel').getByText('Hello from the web')).toBeVisible()

  const seen = await api<{ group: { memberCount: number; posts: { edges: { node: { author: { displayName: string }; body: unknown } }[] } } }>('query ($id: UUID!) { group(id: $id) { memberCount posts { edges { node { author { displayName } body } } } } }', { id: groupId }, owner.accessToken)
  expect(seen.group.memberCount).toBe(2)
  expect(seen.group.posts.edges.map((e) => e.node.author.displayName)).toEqual(['Live Joiner'])
})

test('a platform admin suspends a learner, who reads why on their account and is told so when starting a group (lvn-backend ADR-0053)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a platform admin')
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email: `live-admin-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Admin', dateOfBirth: '1990-01-01', acceptedTermsVersion: termsVersion },
  })
  const admin = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL', "globalRole" = 'PLATFORM_ADMIN' WHERE id = '${admin.user.id}'`)

  const email = `live-suspended-${stamp}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Suspended')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE email = '${email}'`)
  const learnerId = execFileSync(process.env.E2E_VM!, ['ssh', `docker exec lvn-local-postgres psql -U lvn -d lvn -tAc "SELECT id FROM users.\\"User\\" WHERE email = '${email}'"`]).toString().trim()

  const decided = await api<{ moderateContent: { ok: boolean; userErrors: { message: string }[] } }>('mutation ($input: ModerateContentInput!) { moderateContent(input: $input) { ok userErrors { message } } }', { input: { entityType: 'USER', entityId: learnerId, action: 'SUSPEND', reason: 'Posting the same link everywhere.', suspendDays: 3 } }, admin.accessToken)
  expect(decided.moderateContent).toEqual({ ok: true, userErrors: [] })

  await page.reload()
  const banner = page.getByRole('alert').filter({ hasText: 'Your account is suspended until' })
  await expect(banner).toBeVisible()
  await expect(banner.getByText('Posting the same link everywhere.')).toBeVisible()
  await page.goto('/groups')
  await page.getByRole('button', { name: 'New group' }).click()
  const dialog = page.getByRole('dialog', { name: 'New group' })
  await dialog.getByLabel('Name').fill(`Not now ${stamp}`)
  await dialog.getByRole('button', { name: 'Create group' }).click()
  await expect(dialog.getByRole('alert')).toContainText('Your account is suspended until')

  // Lifted: the account page has nothing to say, and the group starts.
  await api('mutation ($input: ModerateContentInput!) { moderateContent(input: $input) { ok } }', { input: { entityType: 'USER', entityId: learnerId, action: 'APPROVE' } }, admin.accessToken)
  await dialog.getByRole('button', { name: 'Create group' }).click()
  await expect(page).toHaveURL(/\/groups\/[0-9a-f-]+$/)
})

test('a learner without a college email asks a teacher to vouch, and is verified when the teacher agrees (lvn-backend ADR-0019)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a teacher')
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email: `live-voucher-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: `Vouching Teacher ${stamp}`, dateOfBirth: '1985-01-01', acceptedTermsVersion: termsVersion },
  })
  const teacher = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL', "globalRole" = 'TEACHER' WHERE id = '${teacher.user.id}'`)

  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Learner Without Email')
  await page.getByLabel('Email', { exact: true }).fill(`live-novouch-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2004-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await page.getByRole('button', { name: 'Ask a teacher' }).click()
  await page.getByLabel('Find your teacher').fill(`Vouching Teacher ${stamp}`)
  await page.getByRole('button', { name: new RegExp(`Vouching Teacher ${stamp}`) }).click()
  await page.getByRole('button', { name: 'Send request' }).click()
  await expect(page.getByText(`Waiting for Vouching Teacher ${stamp} to vouch for you.`)).toBeVisible()

  const waiting = await api<{ verificationRequestsToReview: { id: string }[] }>('{ verificationRequestsToReview { id } }', {}, teacher.accessToken)
  expect(waiting.verificationRequestsToReview).toHaveLength(1)
  await api('mutation ($input: ReviewVerificationRequestInput!) { reviewVerificationRequest(input: $input) { request { status } } }', { input: { requestId: waiting.verificationRequestsToReview[0]!.id, approve: true } }, teacher.accessToken)
  await page.reload()
  await expect(page.getByRole('heading', { name: /✓/ })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Ask a teacher' })).toHaveCount(0)
})

test('a learner searches: a typo still finds a public note, the Projects chip narrows, and Ctrl+K opens a group (lvn-backend ADR-0055, ADR-0056)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to verify the author')
  const stamp = `${Date.now()}${info.project.name}`
  const word = `zorbix${Date.now().toString(36)}${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } | null; userErrors: { message: string }[] } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } userErrors { message } } }', {
    input: { email: `live-author-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Author', dateOfBirth: '1995-01-01', acceptedTermsVersion: termsVersion },
  })
  if (!up.signUp.session) throw new Error(`sign-up refused: ${up.signUp.userErrors[0]?.message}`)
  const author = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE id = '${author.user.id}'`)
  const publish = async (title: string, kind: 'NOTE' | 'PROJECT') => {
    const card = { id: crypto.randomUUID(), type: 'text', position: 'a0', content: { doc: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: `Kruskal joins the cheapest edges first. ${word}` }] }] } } }
    const id = (await api<{ createNote: { note: { id: string } } }>('mutation ($input: CreateNoteInput!) { createNote(input: $input) { note { id } } }', { input: { title, kind, cards: [card] } }, author.accessToken)).createNote.note.id
    await api('mutation ($input: NoteIdInput!) { publishNote(input: $input) { note { id } } }', { input: { noteId: id } }, author.accessToken)
    await api('mutation ($input: ChangeNoteVisibilityInput!) { changeNoteVisibility(input: $input) { note { id } } }', { input: { noteId: id, visibility: 'PUBLIC' } }, author.accessToken)
  }
  await publish('Spanning trees', 'NOTE')
  await publish('Spanning tree visualiser', 'PROJECT')
  const group = `Live search circle ${stamp}`
  const groupId = (await api<{ createGroup: { group: { id: string } } }>('mutation ($input: CreateGroupInput!) { createGroup(input: $input) { group { id } } }', { input: { name: group, privacy: 'PUBLIC', joinPolicy: 'OPEN' } }, author.accessToken)).createGroup.group.id
  // The worker indexes within a second or two (the search outbox).
  await expect.poll(async () => (await api<{ search: { notes: unknown[] } }>('query ($q: String!) { search(query: $q, scopes: [NOTES]) { notes { snippet } } }', { q: word })).search.notes.length, { timeout: 20_000 }).toBe(2)

  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Searcher')
  await page.getByLabel('Email', { exact: true }).fill(`live-searcher-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  // "kruskl" is a typo of a word in the notes, not their titles: only Typesense forgives that.
  await page.goto(`/search?q=${encodeURIComponent(`kruskl ${word}`)}`)
  await expect(page.getByRole('link', { name: /Spanning trees/ })).toBeVisible()
  await expect(page.getByRole('link', { name: /Spanning tree visualiser/ })).toBeVisible()
  await expect(page.getByRole('link', { name: /Spanning trees/ }).locator('mark').first()).toHaveText('Kruskal')
  await page.getByRole('button', { name: 'Projects' }).click()
  await expect(page.getByRole('link', { name: /Spanning tree visualiser/ })).toBeVisible()
  await expect(page.getByRole('link', { name: /Spanning trees(?! visualiser)/ })).toHaveCount(0)

  await page.goto('/notes')
  await page.getByRole('button', { name: 'Search' }).click()
  const palette = page.getByRole('dialog', { name: 'Search notes, people, groups and topics' })
  await palette.getByRole('combobox').fill(group)
  await palette.getByRole('option', { name: new RegExp(`${group} · Group`) }).click()
  await expect(page).toHaveURL(new RegExp(`/groups/${groupId}$`))
})

test('a learner asks AI about a note with the real model: a summary, then flashcards kept in the note (lvn-backend ADR-0059)', async ({ page, request }, info) => {
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ aiStatus { available } }' } })
  const available = ((await res.json()) as { data: { aiStatus: { available: boolean } } }).data.aiStatus.available
  test.skip(!available, 'AI is off in this environment')
  // The model answers one task at a time, and loads on its first one.
  test.setTimeout(300_000)
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Asker')
  await page.getByLabel('Email', { exact: true }).fill(`live-ai-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await fromSidebar(page, 'My Notes')
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  await page.getByLabel('Title').fill('Binary heaps')
  const editor = page.getByRole('textbox', { name: 'Note content' })
  await editor.click()
  const saved = page.waitForResponse((r) => r.url().endsWith('/graphql') && (r.request().postData() ?? '').includes('sifts it down'), { timeout: 15_000 })
  await page.keyboard.type('A min-heap keeps the smallest item at the root. Insert adds at the end and sifts it up; extract-min moves the last item to the root and sifts it down. Both take O(log n).')
  await saved

  await page.getByRole('button', { name: 'AI tasks' }).click()
  const panel = page.getByRole('dialog', { name: 'AI tasks' })
  await panel.getByRole('button', { name: /^Summarise/ }).click()
  const summary = panel.getByRole('article', { name: 'Summarise' })
  await expect(summary).toHaveAttribute('data-ai-status', 'READY', { timeout: 150_000 })
  await expect(summary.getByText(/heap/i).first()).toBeVisible()

  await panel.getByRole('button', { name: /^Flashcards/ }).click()
  const flashcards = panel.getByRole('article', { name: 'Flashcards' })
  await expect(flashcards).toHaveAttribute('data-ai-status', 'READY', { timeout: 120_000 })
  const boxes = flashcards.getByRole('checkbox')
  const made = await boxes.count()
  expect(made).toBeGreaterThan(0)
  if (made > 1) await flashcards.getByRole('checkbox', { name: 'Keep card 1' }).uncheck()
  const keeping = made > 1 ? made - 1 : 1
  await flashcards.getByRole('button', { name: `Add ${keeping} card${keeping === 1 ? '' : 's'} to this note` }).click()
  // The panel closes and the note loads again with the cards in its draft.
  await expect(page.getByText('Added to this note.')).toBeVisible({ timeout: 20_000 })
  await expect(page.getByLabel('Front')).toHaveCount(keeping)
})

test('a learner asks the real model about their note and gets an answer citing it (lvn-backend ADR-0060)', async ({ page, request }, info) => {
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ aiStatus { available } }' } })
  test.skip(!((await res.json()) as { data: { aiStatus: { available: boolean } } }).data.aiStatus.available, 'AI is off in this environment')
  test.setTimeout(300_000)
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Questioner')
  await page.getByLabel('Email', { exact: true }).fill(`live-ask-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await fromSidebar(page, 'My Notes')
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  await page.getByLabel('Title').fill('Photosynthesis')
  await page.getByRole('textbox', { name: 'Note content' }).click()
  const saved = page.waitForResponse((r) => r.url().endsWith('/graphql') && (r.request().postData() ?? '').includes('chloroplast'), { timeout: 15_000 })
  await page.keyboard.type('Plants turn light into chemical energy in the chloroplast. Chlorophyll absorbs red and blue light and reflects green.')
  await saved

  await page.getByRole('button', { name: 'AI tasks' }).click()
  const panel = page.getByRole('dialog', { name: 'AI tasks' })
  await panel.getByRole('textbox', { name: 'Ask about this note' }).fill('Which colours of light does chlorophyll absorb?')
  await panel.getByRole('button', { name: 'Ask', exact: true }).click()
  const card = panel.getByRole('article', { name: 'Which colours of light does chlorophyll absorb?' })
  await expect(card).toHaveAttribute('data-answer-status', 'READY', { timeout: 150_000 })
  await expect(card.getByText(/red/i).first()).toBeVisible()
  await expect(card.getByRole('region', { name: 'Sources' }).getByRole('link', { name: /Photosynthesis/ })).toBeVisible()
})

test('a public note gets its study aids from the real model, on its public page too (lvn-backend ADR-0061)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to verify the author')
  const status = (await api<{ aiStatus: { available: boolean } }>('{ aiStatus { available } }')).aiStatus
  test.skip(!status.available, 'AI is off in this environment')
  // Five model calls, one at a time on the GPU, for each browser's note.
  test.setTimeout(420_000)
  const stamp = `${Date.now()}${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } | null; userErrors: { message: string }[] } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } userErrors { message } } }', {
    input: { email: `live-aids-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Aids', dateOfBirth: '1995-01-01', acceptedTermsVersion: termsVersion },
  })
  if (!up.signUp.session) throw new Error(`sign-up refused: ${up.signUp.userErrors[0]?.message}`)
  const author = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE id = '${author.user.id}'`)
  const card = { id: crypto.randomUUID(), type: 'text', position: 'a0', content: { doc: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Photosynthesis turns light into chemical energy in the chloroplast. Chlorophyll absorbs red and blue light; the light reactions split water and release oxygen; the Calvin cycle fixes carbon dioxide into sugar.' }] }] } } }
  const created = await api<{ createNote: { note: { id: string; slug: string } } }>('mutation ($input: CreateNoteInput!) { createNote(input: $input) { note { id slug } } }', { input: { title: 'Photosynthesis', cards: [card] } }, author.accessToken)
  const id = created.createNote.note.id
  await api('mutation ($input: NoteIdInput!) { publishNote(input: $input) { note { id } } }', { input: { noteId: id } }, author.accessToken)
  const made = await api<{ changeNoteVisibility: { note: { slug: string } } }>('mutation ($input: ChangeNoteVisibilityInput!) { changeNoteVisibility(input: $input) { note { slug } } }', { input: { noteId: id, visibility: 'PUBLIC' } }, author.accessToken)
  // The owner follows the worker's progress.
  await expect
    .poll(async () => (await api<{ note: { noteProcessingStatus: { done: boolean } | null } }>('query ($id: UUID!) { note(id: $id) { noteProcessingStatus { done } } }', { id }, author.accessToken)).note.noteProcessingStatus?.done ?? false, { timeout: 400_000, intervals: [5_000] })
    .toBe(true)
  const aids = (await api<{ note: { aiInsights: { task: string; status: string }[] } }>('query ($id: UUID!) { note(id: $id) { aiInsights { task status } } }', { id })).note.aiInsights
  expect(aids.filter((a) => a.status === 'READY').map((a) => a.task)).toEqual(expect.arrayContaining(['SUMMARIZE', 'QUIZ']))

  // A visitor who is not signed in reads them on the public page, regenerated as each was made.
  await page.goto(`/n/${made.changeNoteVisibility.note.slug}-${id}`)
  const region = page.getByRole('region', { name: 'Study aids' })
  await expect(region.getByRole('tab', { name: 'Summarise' })).toBeVisible({ timeout: 20_000 })
  await expect(region.getByText(/chlorophyll|light/i).first()).toBeVisible()
  await region.getByRole('tab', { name: 'Quiz' }).click()
  await expect(region.getByRole('link', { name: 'Save these cards in your notes' })).toBeVisible()
})

test('a learner tidies rough notes into clean ones with the real model (lvn-backend ADR-0062)', async ({ page, request }, info) => {
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ aiStatus { available } }' } })
  test.skip(!((await res.json()) as { data: { aiStatus: { available: boolean } } }).data.aiStatus.available, 'AI is off in this environment')
  test.setTimeout(300_000)
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Tidier')
  await page.getByLabel('Email', { exact: true }).fill(`live-tidy-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await fromSidebar(page, 'My Notes')
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  await page.getByRole('textbox', { name: 'Note content' }).click()
  const saved = page.waitForResponse((r) => r.url().endsWith('/graphql') && (r.request().postData() ?? '').includes('mitochondria'), { timeout: 15_000 })
  await page.keyboard.type('bio lec 4 - mitochondria = powerhouse, ATP made by resp. glycolysis in cytoplasm, krebs in matrix, ETC inner membrane')
  await saved

  await page.getByRole('button', { name: 'AI tasks' }).click()
  const panel = page.getByRole('dialog', { name: 'AI tasks' })
  await panel.getByRole('button', { name: /^Tidy into notes/ }).click()
  const result = panel.getByRole('article', { name: 'Tidy into notes' })
  await expect(result).toHaveAttribute('data-ai-status', 'READY', { timeout: 150_000 })
  await expect(result.getByText(/mitochondri/i).first()).toBeVisible()
  await expect(result.getByRole('button', { name: /^Add \d+ cards? to this note$/ })).toBeVisible()
})

test('a learner cleans up words a conversion broke with the real model, and applies the changes (lvn-backend ADR-0063)', async ({ page, request }, info) => {
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ aiStatus { available } }' } })
  test.skip(!((await res.json()) as { data: { aiStatus: { available: boolean } } }).data.aiStatus.available, 'AI is off in this environment')
  test.setTimeout(300_000)
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Cleaner')
  await page.getByLabel('Email', { exact: true }).fill(`live-clean-${Date.now()}-${info.project.name}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await fromSidebar(page, 'My Notes')
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  await page.getByRole('textbox', { name: 'Note content' }).click()
  // As a scanned page's OCR leaves it: a word split across lines and a misread letter.
  const saved = page.waitForResponse((r) => r.url().endsWith('/graphql') && (r.request().postData() ?? '').includes('glucose'), { timeout: 15_000 })
  await page.keyboard.type('Respiration releases the en- ergy stored in glucose. Cells use tbis energy to grow and repair themselves.')
  await saved

  await page.getByRole('button', { name: 'AI tasks' }).click()
  const panel = page.getByRole('dialog', { name: 'AI tasks' })
  await panel.getByRole('button', { name: /^Clean up the text/ }).click()
  const result = panel.getByRole('article', { name: 'Clean up the text' })
  await expect(result).toHaveAttribute('data-ai-status', 'READY', { timeout: 150_000 })
  await expect(result.getByText(/the energy stored/).first()).toBeVisible()
  await result.getByRole('button', { name: /^Apply \d+ changes?$/ }).click()
  await expect(page.getByText(/^Applied 1 change\./)).toBeVisible()
  await expect(page.getByRole('textbox', { name: 'Note content' }).getByText(/the energy stored in glucose/)).toBeVisible()
  await expect(page.getByRole('textbox', { name: 'Note content' }).getByText(/en- ergy/)).toHaveCount(0)
})

test('a teacher makes a class quiz from a note with the real model and publishes it; a student’s submission is counted (lvn-backend ADR-0064)', async ({ page, request }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a teacher')
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ aiStatus { available } }' } })
  test.skip(!((await res.json()) as { data: { aiStatus: { available: boolean } } }).data.aiStatus.available, 'AI is off in this environment')
  test.setTimeout(300_000)
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const signUp = async (who: string, name: string) =>
    (await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', { input: { email: `live-${who}-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: name, dateOfBirth: '1990-01-01', acceptedTermsVersion: termsVersion } })).signUp.session
  const teacher = await signUp('quiz-teacher', 'Quiz Teacher')
  const student = await signUp('quiz-student', 'Quiz Student')
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'TEACHER', "globalRole" = 'TEACHER' WHERE id = '${teacher.user.id}'`)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE id = '${student.user.id}'`)
  const text = (s: string) => ({ doc: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] } })
  await api('mutation ($input: CreateNoteInput!) { createNote(input: $input) { note { id } } }', { input: { title: 'Cell respiration', cards: [{ id: randomUUID(), type: 'text', position: 'a0', content: text('Cells release energy from glucose by respiration. Most ATP is made in the mitochondria. Glycolysis happens in the cytoplasm and splits glucose into pyruvate. Aerobic respiration needs oxygen and gives carbon dioxide and water.') }] } }, teacher.accessToken)
  const made = await api<{ createClassroom: { classroom: { id: string; joinCode: string } } }>('mutation { createClassroom(input: { name: "Live biology" }) { classroom { id joinCode } } }', {}, teacher.accessToken)
  const { id: classroomId, joinCode } = made.createClassroom.classroom
  await api('mutation ($input: RequestToJoinClassroomInput!) { requestToJoinClassroom(input: $input) { classroom { id } } }', { input: { code: joinCode } }, student.accessToken)
  const asking = await api<{ classroom: { joinRequests: { id: string }[] } }>('query ($id: UUID!) { classroom(id: $id) { joinRequests { id } } }', { id: classroomId }, teacher.accessToken)
  await api('mutation ($input: ReviewClassroomJoinRequestInput!) { reviewClassroomJoinRequest(input: $input) { classroom { id } } }', { input: { requestId: asking.classroom.joinRequests[0]!.id, decision: 'APPROVED' } }, teacher.accessToken)

  await page.goto('/sign-in')
  await page.getByLabel('Email').fill(`live-quiz-teacher-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByRole('button', { name: 'Sign in' }).click()
  await page.waitForURL((u) => !u.pathname.startsWith('/sign-in'))
  await page.goto(`/classes/${classroomId}`)
  await page.getByRole('tab', { name: 'Quizzes' }).click()
  await page.getByRole('button', { name: 'New quiz' }).click()
  const builder = page.getByRole('dialog', { name: 'New quiz' })
  await builder.getByLabel('Make questions from a note').selectOption({ label: 'Cell respiration' })
  await builder.getByRole('button', { name: 'Make questions' }).click()
  await expect(builder.getByLabel('Words of question 1')).not.toHaveValue('', { timeout: 150_000 })
  await expect(builder.getByLabel('Title')).toHaveValue('Cell respiration')
  await builder.getByRole('button', { name: /^Publish \d+ questions?$/ }).click()
  await expect(page.getByText('Quiz published. Everyone in the class has been told.')).toBeVisible()
  await expect(page.getByText('No student has submitted yet')).toBeVisible()

  // The student is told, and submits through the API; the teacher sees the count.
  const told = await api<{ notifications: { edges: { node: { category: string; path: string } }[] } }>('{ notifications(first: 1) { edges { node { category path } } } }', {}, student.accessToken)
  expect(told.notifications.edges[0]?.node.category).toBe('QUIZ_PUBLISHED')
  const quizId = told.notifications.edges[0]!.node.path.split('/').at(-1)!
  const toTake = await api<{ classQuiz: { questions: { id: string; correct: string[] | null; choices: { id: string }[] }[] } }>('query ($id: UUID!) { classQuiz(id: $id) { questions { id correct choices { id } } } }', { id: quizId }, student.accessToken)
  expect(toTake.classQuiz.questions.every((q) => q.correct === null)).toBe(true)
  await api('mutation ($input: SubmitQuizAttemptInput!) { submitQuizAttempt(input: $input) { attempt { score } } }', { input: { quizId, clientOpId: randomUUID(), answers: toTake.classQuiz.questions.map((q) => ({ questionId: q.id, choiceIds: [q.choices[0]!.id] })) } }, student.accessToken)
  await page.reload()
  await page.getByRole('tab', { name: 'Quizzes' }).click()
  await expect(page.getByText('1 student has submitted')).toBeVisible()
})

test('a platform admin adds a custom OpenAI-compatible provider, tests it, and it answers a task for real (lvn-backend ADR-0065)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a platform admin')
  // One admin changes who answers at a time: the phone's run would race the desktop's for the default.
  test.skip(info.project.name !== 'desktop', 'run once')
  const ollamaV1 = process.env.E2E_OPENAI_COMPATIBLE_URL ?? 'http://10.0.2.2:11434/v1'
  test.setTimeout(300_000)
  const stamp = `${Date.now()}-${info.project.name}`
  const email = `live-ai-admin-${stamp}@example.com`
  const password = `live passphrase ${stamp}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email, password, displayName: 'Live AI Admin', dateOfBirth: '1990-01-01', acceptedTermsVersion: termsVersion },
  })
  const admin = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL', "globalRole" = 'PLATFORM_ADMIN' WHERE id = '${admin.user.id}'`)
  const name = `Ollama through its OpenAI API ${stamp}`
  try {
    await page.goto('/sign-in')
    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password').fill(password)
    await page.getByRole('button', { name: 'Sign in' }).click()
    await expect(page).toHaveURL(/\/profile$/)
    await page.getByRole('link', { name: /AI providers/ }).click()
    await expect(page.getByRole('heading', { name: 'AI providers' })).toBeVisible()

    await page.getByRole('button', { name: /^Custom \(OpenAI-compatible/ }).click()
    const dialog = page.getByRole('dialog', { name: /^Add Custom/ })
    await dialog.getByLabel('Name').fill(name)
    await dialog.getByLabel('Address').fill(ollamaV1)
    await dialog.getByLabel('Chat model').fill('gemma4')
    await dialog.getByLabel('Embedding model').fill('embeddinggemma')
    // A model on this machine: private notes may go to it.
    await dialog.getByLabel(/Private notes may go to it/).check()
    await dialog.getByRole('button', { name: 'Save' }).click()
    await expect(dialog).toBeHidden()

    const card = page.getByRole('article', { name })
    await card.getByRole('button', { name: 'Test' }).click()
    await expect(card.getByRole('status')).toContainText('embeddinggemma gave 768 numbers', { timeout: 180_000 })
    await expect(card.getByRole('status')).toContainText(/models? listed: .*gemma4/)

    await page.getByLabel(/Chats, tasks and Ask AI/).selectOption({ label: `${name} · gemma4` })
    await expect(card.getByText('Answers chats')).toBeVisible()

    // A task now goes through the connection: the usage row says who answered.
    const created = await api<{ createNote: { note: { id: string } } }>('mutation ($input: CreateNoteInput!) { createNote(input: $input) { note { id } } }', { input: { title: 'Heaps', cards: [{ id: crypto.randomUUID(), type: 'text', position: 'a0', content: { doc: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'A min-heap keeps the smallest item at the root; insert and extract-min take O(log n).' }] }] } } }] } }, admin.accessToken)
    const run = await api<{ runAiTask: { artifact: { id: string } | null; userErrors: { message: string }[] } }>('mutation ($input: RunAiTaskInput!) { runAiTask(input: $input) { artifact { id } userErrors { message } } }', { input: { noteId: created.createNote.note.id, task: 'SUMMARIZE' } }, admin.accessToken)
    expect(run.runAiTask.userErrors).toEqual([])
    await expect.poll(async () => (await api<{ aiArtifact: { status: string } }>('query ($id: UUID!) { aiArtifact(id: $id) { status } }', { id: run.runAiTask.artifact!.id }, admin.accessToken)).aiArtifact.status, { timeout: 180_000, intervals: [2_000] }).toBe('READY')
    const answered = execFileSync(process.env.E2E_VM!, ['ssh', `docker exec lvn-local-postgres psql -U lvn -d lvn -tAc "SELECT provider || ' ' || (\\"connectionId\\" IS NOT NULL) FROM ai.\\"AiUsage\\" WHERE \\"userId\\" = '${admin.user.id}' AND task = 'SUMMARIZE' ORDER BY \\"createdAt\\" DESC LIMIT 1"`]).toString().trim()
    expect(answered).toBe('OPENAI_COMPATIBLE true')
  } finally {
    // The environment's own model answers again, for every other test and for people.
    sql(`UPDATE ai."AiSettings" SET "chatConnectionId" = NULL, "embedConnectionId" = NULL`)
    sql(`DELETE FROM ai."AiConnection" WHERE label = '${name}'`)
  }
})

test('a learner’s reading reaches the learning events: the note opened and the time read (lvn-backend ADR-0067)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to read the events')
  const stamp = `${Date.now()}-${info.project.name}`
  const email = `live-events-${stamp}@example.com`
  await page.clock.install()
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Reader')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await fromSidebar(page, 'My Notes')
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  const noteId = page.url().split('/').at(-1)!
  // Half a minute with the note open, then the tab goes to the background: the events go out.
  await page.clock.runFor(30_000)
  await page.evaluate(() => {
    Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'hidden' })
    document.dispatchEvent(new Event('visibilitychange'))
  })
  const events = () =>
    execFileSync(process.env.E2E_VM!, ['ssh', `docker exec lvn-local-postgres psql -U lvn -d lvn -tAc "SELECT e.type FROM learning.\\"LearningEvent\\" e JOIN users.\\"User\\" u ON u.id = e.\\"userId\\" WHERE u.email = '${email}' ORDER BY e.\\"clientTs\\", e.type"`]).toString().trim().split('\n').filter(Boolean)
  await expect.poll(events, { timeout: 30_000 }).toEqual(expect.arrayContaining(['NOTE_CREATED', 'NOTE_OPENED', 'TIME_SPENT']))
  const opened = execFileSync(process.env.E2E_VM!, ['ssh', `docker exec lvn-local-postgres psql -U lvn -d lvn -tAc "SELECT e.\\"entityId\\" FROM learning.\\"LearningEvent\\" e JOIN users.\\"User\\" u ON u.id = e.\\"userId\\" WHERE u.email = '${email}' AND e.type = 'NOTE_OPENED'"`]).toString().trim()
  expect(opened).toBe(noteId)
})

test('a learner reviews the flashcard of their note, and the day shows in their history (lvn-backend ADR-0068)', async ({ page }, info) => {
  const stamp = `${Date.now()}-${info.project.name}`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Reviewer')
  await page.getByLabel('Email', { exact: true }).fill(`live-review-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await fromSidebar(page, 'My Notes')
  await page.getByRole('button', { name: 'New note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  await page.getByLabel('Title').fill('Live deck')
  await page.getByRole('button', { name: 'Add a card', exact: true }).click()
  await page.getByRole('button', { name: /^Flashcard/ }).click()
  await page.getByLabel('Front').fill('FIFO')
  const backSaved = page.waitForResponse((r) => r.url().endsWith('/graphql') && /UpdateNoteDraft/.test(r.request().postData() ?? '') && (r.request().postData() ?? '').includes('First in, first out'), { timeout: 15_000 })
  await page.getByLabel('Back').fill('First in, first out: a queue')
  await backSaved

  // An owner's flashcards are in their reviews at once: graded Easy, the session is done.
  await page.goto('/review')
  const session = page.getByRole('region', { name: 'Review session' })
  await expect(session.getByText('FIFO')).toBeVisible()
  await expect(session.getByText('1 of 1')).toBeVisible()
  await session.getByRole('button', { name: 'Show the answer' }).click()
  await expect(session.getByText('First in, first out: a queue')).toBeVisible()
  await session.getByRole('button', { name: 'Easy' }).click()
  await expect(page.getByText('1 card reviewed.')).toBeVisible()
  await expect(page.getByText(/grades? waits? to be sent/)).toHaveCount(0)

  // The server recorded the review on today's learning day.
  await expect(async () => {
    await page.goto('/history')
    await expect(page.getByRole('article').first().getByText(/1 card reviewed/)).toBeVisible({ timeout: 2_000 })
  }).toPass({ timeout: 30_000 })
  await page.goto('/review')
  await expect(page.getByRole('heading', { name: 'Nothing to review' })).toBeVisible()
})

test('a learner sees this week on their Rhythm, plans six days and pauses for exams (lvn-backend ADR-0069)', async ({ page }, info) => {
  const stamp = `${Date.now()}-${info.project.name}`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Rhythm')
  await page.getByLabel('Email', { exact: true }).fill(`live-rhythm-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  await page.getByRole('main').getByRole('link', { name: /^Rhythm/ }).click()
  await expect(page).toHaveURL(/\/rhythm$/)
  const week = page.getByRole('region', { name: 'This week' })
  // A new account's first week aims only for the planned days from today on (lvn-backend ADR-0069).
  await expect(week.getByText(/^0 of \d days this week$/)).toBeVisible()
  await expect(week.getByRole('listitem', { name: /: today/ })).toHaveCount(1)
  await expect(page.getByRole('region', { name: 'Today' }).getByText(/more learning minutes, or 10 more reviews, and today counts\./)).toBeVisible()

  // Six planned days, from today on in a first week.
  const plan = page.getByRole('region', { name: 'Your planned days' })
  await plan.getByRole('button', { name: 'Wednesday' }).click()
  await plan.getByRole('button', { name: 'Friday' }).click()
  await plan.getByRole('button', { name: 'Save days' }).click()
  await expect(plan.getByRole('status')).toHaveText(/^Saved\. This week now aims for \d days\.$/)

  // A pause for exams from today, then cancelled: its days come back.
  const pauses = page.getByRole('region', { name: 'Pauses' })
  await pauses.getByRole('button', { name: 'Pause Rhythm' }).click()
  await pauses.getByRole('button', { name: 'Pause', exact: true }).click()
  await expect(pauses.getByText('Paused now')).toBeVisible()
  await expect(pauses.getByText(/11 of 14 pause days left this term/)).toBeVisible()
  await pauses.getByRole('button', { name: 'Cancel the pause' }).click()
  await expect(pauses.getByText('No pauses.')).toBeVisible()
  await expect(pauses.getByText(/14 of 14 pause days left this term/)).toBeVisible()
})

test('a learner adds an exam on a topic found by name, is recommended its topic, and focuses for a while (lvn-backend ADR-0070, ADR-0071, ADR-0072)', async ({ page }, info) => {
  const stamp = `${Date.now()}-${info.project.name}`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Exams')
  await page.getByLabel('Email', { exact: true }).fill(`live-exams-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  // An exam ten days away on a curated topic.
  await page.getByRole('main').getByRole('link', { name: /^Exams/ }).click()
  await page.getByRole('button', { name: 'Add an exam' }).click()
  const form = page.getByRole('region', { name: 'Add an exam' })
  await form.getByLabel('Exam').fill('Live midterm')
  await form.getByLabel('Date').fill(new Date(Date.now() + 10 * 86_400_000).toISOString().slice(0, 10))
  await form.getByLabel('Find a topic').fill('arrays & hash')
  await form.getByRole('button', { name: 'Add Arrays & Hashing' }).click()
  await form.getByRole('button', { name: 'Add the exam' }).click()
  const card = page.getByRole('article', { name: 'Live midterm' })
  await expect(card.getByText('Readiness 0%')).toBeVisible()
  await card.getByRole('link', { name: 'Live midterm' }).click()
  await expect(page.getByRole('region', { name: 'Revision plan' }).getByRole('listitem').first()).toBeVisible()

  // The exam's topic is recommended, with why; a focus session starts and ends.
  await page.goto('/rhythm')
  await expect(page.getByRole('region', { name: 'Recommended for you' }).getByText(/^On your plan for Live midterm, in (9|10) days$/)).toBeVisible()
  const focus = page.getByRole('region', { name: 'Focus' })
  await focus.getByRole('button', { name: 'Start focusing' }).click()
  await expect(focus.getByRole('timer')).toHaveText(/^2[45]:\d\d$/)
  await focus.getByRole('button', { name: 'End the session' }).click()
  await expect(focus.getByRole('status')).toHaveText(/minutes? counted\.$/)

  // Home brings it together: the greeting, today, and the next exam (P6h).
  await page.goto('/home')
  await expect(page.getByRole('heading', { name: /^Good (morning|afternoon|evening), Live!/ })).toBeVisible()
  await expect(page.getByRole('region', { name: 'Next exam' }).getByText('Live midterm')).toBeVisible()
  await expect(page.getByRole('region', { name: 'Today' })).toBeVisible()
})

test('a new teacher signs up to teach, sets up a class while waiting, and takes students once an admin approves (lvn-backend ADR-0073)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a platform admin')
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email: `live-teach-admin-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Admin', dateOfBirth: '1990-01-01', acceptedTermsVersion: termsVersion },
  })
  const admin = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL', "globalRole" = 'PLATFORM_ADMIN' WHERE id = '${admin.user.id}'`)

  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill(`Live New Teacher ${stamp}`)
  await page.getByLabel('Email', { exact: true }).fill(`live-new-teacher-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('1988-01-01')
  await page.getByText('Teach', { exact: true }).click()
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/teach$/)
  const form = page.getByRole('form', { name: 'Apply to teach' })
  await form.getByLabel('Where you teach').fill('Govt. Junior College, Guntur')
  await form.getByLabel('What you teach (optional)').fill('Physics')
  await form.getByRole('button', { name: 'Apply to teach' }).click()
  await expect(page.getByRole('heading', { name: 'Your application is being reviewed' })).toBeVisible()

  // While waiting: a class, with no way in for students yet.
  await page.getByRole('link', { name: /Set up a class/ }).click()
  await page.getByRole('button', { name: 'New class' }).click()
  const dialog = page.getByRole('dialog', { name: 'New class' })
  await dialog.getByLabel('Name').fill('Live physics 11A')
  await dialog.getByRole('button', { name: 'Create class' }).click()
  await expect(page).toHaveURL(/\/classes\/[0-9a-f-]+$/)
  await expect(page.getByRole('note')).toContainText('Students can join this class once you are verified as a teacher.')
  await expect(page.getByRole('tab', { name: 'Requests' })).toHaveCount(0)

  const queue = await api<{ verificationRequestsToReview: { id: string; purpose: string; institution: string | null; requester: { displayName: string } }[] }>('{ verificationRequestsToReview { id purpose institution requester { displayName } } }', {}, admin.accessToken)
  const mine = queue.verificationRequestsToReview.find((r) => r.requester.displayName === `Live New Teacher ${stamp}`)
  expect(mine).toMatchObject({ purpose: 'TEACHER_ROLE', institution: 'Govt. Junior College, Guntur' })
  await api('mutation ($input: ReviewVerificationRequestInput!) { reviewVerificationRequest(input: $input) { request { status } } }', { input: { requestId: mine!.id, approve: true } }, admin.accessToken)

  // Approved: the class takes students.
  await page.reload()
  await expect(page.getByRole('tab', { name: 'Requests' })).toBeVisible()
  await expect(page.getByRole('note')).toHaveCount(0)
  await page.goto('/teach')
  await expect(page.getByRole('heading', { name: 'You’re a verified teacher' })).toBeVisible()
})

test('a learner adds a book found on Open Library; it waits for moderators, and a guest reads it once approved (lvn-backend ADR-0074)', async ({ page, browser }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a platform admin')
  test.setTimeout(120_000)
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const up = await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
    input: { email: `live-res-admin-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: 'Live Admin', dateOfBirth: '1990-01-01', acceptedTermsVersion: termsVersion },
  })
  const admin = up.signUp.session
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL', "globalRole" = 'PLATFORM_ADMIN' WHERE id = '${admin.user.id}'`)

  const email = `live-res-${stamp}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Reader')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE email = '${email}'`)

  await page.goto('/resources/new')
  const form = page.getByRole('form', { name: 'Add a resource' })
  // Each run's own book: one ISBN is one resource, and earlier runs' books may still be in the catalogue.
  const books = ['9780132350884', '9780262033848', '9780201633610', '9780596007126', '9781491950357', '9780134685991']
  const isbn = books[(Math.floor(Date.now() / 60_000) + (info.project.name === 'phone' ? 3 : 0)) % books.length]!
  await form.getByLabel('ISBN').fill(isbn)
  await form.getByRole('button', { name: 'Look up the book' }).click()
  await expect(form.getByLabel('Title', { exact: true })).not.toHaveValue('', { timeout: 30_000 })
  await expect(form.getByRole('radio', { name: 'Book' })).toBeChecked()
  const exists = await form.getByText('This is already in the catalogue:').isVisible()
  test.skip(exists, 'this book is already in the catalogue from an earlier run')
  await form.getByPlaceholder('Find a topic, e.g. arrays').fill('array')
  await form.getByRole('button', { name: /^Add / }).first().click()
  await form.getByRole('button', { name: 'Send to moderators' }).click()
  await expect(page).toHaveURL(/\/resources\/[0-9a-f-]+$/, { timeout: 30_000 })
  await expect(page.getByRole('note')).toContainText('Waiting for moderators')
  const id = page.url().split('/').pop()!

  const guest = await (await browser.newContext()).newPage()
  await guest.goto(`/resources/${id}`)
  await expect(guest.getByRole('heading', { name: 'This resource is not here.' })).toBeVisible()
  const decided = await api<{ moderateContent: { ok: boolean } }>('mutation ($input: ModerateContentInput!) { moderateContent(input: $input) { ok } }', { input: { entityType: 'RESOURCE', entityId: id, action: 'APPROVE' } }, admin.accessToken)
  expect(decided.moderateContent.ok).toBe(true)
  await guest.reload()
  await expect(guest.locator('#resource-title')).toBeVisible()
  await expect(guest.getByRole('link', { name: /^Open / })).toHaveAttribute('rel', 'ugc nofollow noopener')
  // Clean up, so the book can be added again by a later run.
  await api('mutation ($input: ResourceIdInput!) { deleteResource(input: $input) { ok } }', { input: { id } }, admin.accessToken)
})

test('a learner finds an approved resource in the catalogue, saves it and discusses it (lvn-backend ADR-0075)', async ({ page }, info) => {
  test.skip(!process.env.E2E_VM, 'needs E2E_VM to make a platform admin')
  test.setTimeout(120_000)
  const stamp = `${Date.now()}-${info.project.name}`
  const { termsVersion } = await api<{ termsVersion: string }>('{ termsVersion }')
  const signUp = async (who: string, name: string) =>
    (await api<{ signUp: { session: { accessToken: string; user: { id: string } } } }>('mutation ($input: SignUpInput!) { signUp(input: $input) { session { accessToken user { id } } } }', {
      input: { email: `live-${who}-${stamp}@example.com`, password: `live passphrase ${stamp}`, displayName: name, dateOfBirth: '1995-01-01', acceptedTermsVersion: termsVersion },
    })).signUp.session
  const admin = await signUp('cat-admin', 'Live Admin')
  const author = await signUp('cat-author', 'Live Author')
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL', "globalRole" = 'PLATFORM_ADMIN' WHERE id = '${admin.user.id}'`)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE id = '${author.user.id}'`)
  const topic = (await api<{ resourceTopicOptions: { id: string }[] }>('query { resourceTopicOptions(query: "array") { id } }', {}, author.accessToken)).resourceTopicOptions[0]!
  const title = `Live course ${stamp}`
  const sent = await api<{ submitResource: { resource: { id: string } } }>('mutation ($input: SubmitResourceInput!) { submitResource(input: $input) { resource { id } } }', { input: { type: 'COURSE', title, url: `https://nptel.ac.in/courses/${stamp}`, topicIds: [topic.id] } }, author.accessToken)
  const id = sent.submitResource.resource.id
  await api('mutation ($input: ModerateContentInput!) { moderateContent(input: $input) { ok } }', { input: { entityType: 'RESOURCE', entityId: id, action: 'APPROVE' } }, admin.accessToken)

  const email = `live-cat-${stamp}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Catalogue Reader')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  sql(`UPDATE users."User" SET "verifiedAt" = now(), "verificationMethod" = 'INSTITUTIONAL_EMAIL' WHERE email = '${email}'`)

  await page.goto('/resources')
  await page.getByLabel('Search resources').fill(stamp)
  const card = page.getByRole('article', { name: title })
  await expect(card).toBeVisible({ timeout: 20_000 })
  await card.getByRole('button', { name: 'Save' }).click()
  await expect(card.getByRole('button', { name: 'Saved' })).toBeVisible()
  await expect(card).toContainText('Saved by 1 person')
  await card.getByRole('link').first().click()
  await expect(page).toHaveURL(new RegExp(`/resources/${id}$`))
  await page.getByLabel('Write a comment').fill('Week 2 has the clearest explanation of arrays.')
  await page.getByRole('button', { name: 'Comment', exact: true }).last().click()
  await expect(page.getByText('Week 2 has the clearest explanation of arrays.')).toBeVisible()
  await page.goto('/resources/saved')
  await expect(page.getByRole('article', { name: title })).toBeVisible()
  // Clean up: the submitter deletes it.
  await api('mutation ($input: ResourceIdInput!) { deleteResource(input: $input) { ok } }', { input: { id } }, author.accessToken)
})

test('a new learner opens every sidebar entry: each page answers with its heading, and no query fails (lvn-backend ADR-0076)', async ({ page }, info) => {
  const stamp = `${Date.now()}-${info.project.name}`
  const failures: string[] = []
  page.on('pageerror', (e) => failures.push(`page error: ${e.message}`))
  page.on('response', async (res) => {
    if (!res.url().endsWith('/graphql') || res.request().method() !== 'POST') return
    const sent = res.request().postDataJSON() as { operationName?: string; query?: string } | null
    // A visitor's first page asks to refresh a session there is none of: that answer is expected.
    if (sent?.query?.includes('refreshSession')) return
    const op = sent?.operationName ?? '?'
    const body = (await res.json().catch(() => null)) as { errors?: { message: string }[] } | null
    if (res.status() >= 500 || body?.errors?.length) failures.push(`${op}: ${res.status()} ${body?.errors?.map((e) => e.message).join('; ') ?? ''}`)
  })
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Shell')
  await page.getByLabel('Email', { exact: true }).fill(`live-shell-${stamp}@example.com`)
  await page.getByLabel('Password').fill(`live passphrase ${stamp}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  const entries: [string, RegExp][] = [
    ['Home', /\/home$/], ['My Notes', /\/notes$/], ['Explore', /\/search$/], ['Groups', /\/groups$/], ['Classrooms', /\/classes$/], ['Exams', /\/exams$/],
    ['Rhythm', /\/rhythm$/], ['Resources', /\/resources$/], ['Community', /\/community$/], ['AI Assistant', /\/ask$/], ['Bookmarks', /\/resources\/saved$/], ['Subjects', /\/core$/],
  ]
  for (const [name, url] of entries) {
    if (info.project.name === 'phone') await page.getByRole('button', { name: 'Menu' }).click()
    await page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name, exact: true }).click()
    await expect(page, name).toHaveURL(url)
    await expect(page.getByRole('heading', { level: 1 }).first(), name).toBeVisible()
    await expect(page.getByText('Something went wrong'), name).toHaveCount(0)
  }
  // The top bar: the avatar opens the account, and Create Note makes a note that opens.
  await page.goto('/home')
  await page.getByRole('link', { name: 'Your account' }).click()
  await expect(page).toHaveURL(/\/profile$/)
  if (info.project.name === 'phone') await page.getByRole('button', { name: 'Menu' }).click()
  await page.getByRole('button', { name: 'Create Note' }).click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}$/)
  expect(failures).toEqual([])
})
