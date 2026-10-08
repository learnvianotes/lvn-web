import { expect, test } from '@playwright/test'

/**
 * The deployed stack with nothing mocked: web, API, database, Redis and mail of an environment — the local environment
 * on its VM (lvn-backend ADR-0036) or the sandbox. Skipped unless E2E_LIVE is set:
 *
 *   E2E_LIVE=1 E2E_BASE_URL=http://127.0.0.1:8080 pnpm test:e2e tests/e2e/live.spec.ts
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
  const res = await request.post('/graphql', { data: { query: '{ signInOptions { google } }' } })
  const google = ((await res.json()) as { data: { signInOptions: { google: boolean } } }).data.signInOptions.google
  test.skip(!google, 'Google sign-in is off in this environment')
  await page.goto('/sign-in')
  await expect(page.getByRole('button', { name: 'Continue with Google' })).toBeVisible()
})
