import { expect, test } from '@playwright/test'

/**
 * The deployed stack with nothing mocked: web, API, database, Redis and mail of an environment — the local environment
 * on its VM (lvn-backend ADR-0036) or the sandbox. Skipped unless E2E_LIVE is set:
 *
 *   E2E_LIVE=1 E2E_BASE_URL=http://127.0.0.1:8080 pnpm test:e2e tests/e2e/live.spec.ts
 *
 * Against the development servers, where the API has its own origin, also set E2E_API_URL (…:4000/graphql).
 *
 * Each run makes one account per browser, live-<time>-<project>@example.com, and leaves it in place.
 */
test.skip(!process.env.E2E_LIVE || !process.env.E2E_BASE_URL, 'needs a deployed environment: E2E_LIVE=1 E2E_BASE_URL=<public url>')

test('a new learner signs up with email, keeps the session across a reload, signs out and signs in again', async ({ page }, info) => {
  const email = `live-${Date.now()}-${info.project.name}@example.com`
  const password = `live passphrase ${Date.now()}`

  await page.goto('/')
  const main = page.getByRole('main')
  await expect(main.getByRole('heading', { name: 'Start learning in seconds' })).toBeVisible()
  await main.getByRole('link', { name: 'Sign up with email' }).click()
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
  const email = `live-notes-${Date.now()}-${info.project.name}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Live Writer')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`live passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  await page.getByRole('link', { name: 'My notes' }).click()
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
  await page.getByLabel('Back').fill('Last in, first out: a stack')
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

test('the documents the web shows are the version the API asks people to accept', async ({ request }) => {
  const { TERMS_VERSION } = await import('../../features/legal/documents')
  const res = await request.post(process.env.E2E_API_URL ?? '/graphql', { data: { query: '{ termsVersion }' } })
  expect(((await res.json()) as { data: { termsVersion: string } }).data.termsVersion).toBe(TERMS_VERSION)
})
