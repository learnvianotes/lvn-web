import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/** Notification settings and email unsubscribe (lvn-backend ADR-0050) against a mocked API. */

const categories = (over: Record<string, { push?: boolean; email?: boolean | null }> = {}) =>
  ['SHARE', 'COMMENT', 'FOLLOW', 'CLASSROOM_POST'].map((category) => ({ __typename: 'CategoryPreference', category, push: over[category]?.push ?? true, email: over[category]?.email !== undefined ? over[category]!.email : category === 'CLASSROOM_POST' ? true : null }))
const settings = (over: Record<string, unknown> = {}) => ({ __typename: 'NotificationSettings', quietStart: '22:00', quietEnd: '07:00', timeZone: 'Asia/Kolkata', weeklyDigest: true, pushAvailable: false, devices: 1, categories: categories(), ...over })

test('the settings page saves each choice as it is made', async ({ page }) => {
  let current = settings()
  const calls = await mockApi(page, {
    NotificationSettings: () => ({ notificationSettings: current }),
    UpdateNotificationSettings: (v) => {
      const input = v.input as { categories?: { category: string; push?: boolean; email?: boolean }[]; weeklyDigest?: boolean; timeZone?: string; quietStart?: string }
      current = settings({ ...(input.weeklyDigest !== undefined ? { weeklyDigest: input.weeklyDigest } : {}), ...(input.timeZone ? { timeZone: input.timeZone } : {}), categories: categories(Object.fromEntries((input.categories ?? []).map((c) => [c.category, c]))) })
      return { updateNotificationSettings: { __typename: 'NotificationSettingsPayload', settings: current, userErrors: [] } }
    },
  })
  await page.goto('/profile/notifications')
  await expect(page.getByRole('heading', { name: 'Notification settings' })).toBeVisible()
  await expect(page.getByText("Phone notifications aren't switched on for LearnViaNotes yet.", { exact: false })).toBeVisible()
  await expect(page.getByText('1 phone gets notifications.')).toBeVisible()
  // Comments send no email: there is nothing to tick.
  await expect(page.getByLabel('Emails for Comments and replies')).toHaveCount(0)
  await page.getByLabel('Phone notifications for New followers').uncheck()
  await expect(page.getByRole('status')).toHaveText('Saved.')
  await page.getByLabel('Emails for Class announcements').uncheck()
  await page.getByLabel('A Monday email counting what you haven\'t read yet').uncheck()
  await page.getByLabel('Time zone').selectOption('Europe/London')
  const inputs = () => calls.filter((c) => c.op === 'UpdateNotificationSettings').map((c) => c.variables.input)
  await expect.poll(inputs).toEqual([{ categories: [{ category: 'FOLLOW', push: false }] }, { categories: [{ category: 'CLASSROOM_POST', email: false }] }, { weeklyDigest: false }, { timeZone: 'Europe/London' }])
})

test('the unsubscribe page asks for one click; mail clients POST to the one-click address', async ({ page, request }) => {
  const calls = await mockApi(page, { UnsubscribeEmail: (v) => ({ unsubscribeEmail: { __typename: 'UnsubscribePayload', kind: v.token === 'good' ? 'DIGEST' : null, userErrors: [] } }) })
  await page.goto('/unsubscribe?t=good')
  // Opening the link changes nothing until the click.
  expect(calls.filter((c) => c.op === 'UnsubscribeEmail')).toEqual([])
  await page.getByRole('button', { name: 'Stop these emails' }).click()
  await expect(page.getByRole('status')).toHaveText("Done. You won't get the weekly email.")
  // RFC 8058: the server route calls the API (here its stand-in) and answers the mail client.
  expect((await request.post('/unsubscribe/one-click?t=good', { form: { 'List-Unsubscribe': 'One-Click' } })).status()).toBe(200)
  expect((await request.post('/unsubscribe/one-click?t=bad', { form: { 'List-Unsubscribe': 'One-Click' } })).status()).toBe(400)
  const opened = await request.get('/unsubscribe/one-click?t=good', { maxRedirects: 0 })
  expect(opened.status()).toBe(303)
  expect(opened.headers()['location']).toMatch(/\/unsubscribe\?t=good$/)
})
