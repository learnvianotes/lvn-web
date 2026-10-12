import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'
import { mockApi, mockLive, NOTE_ID, USER } from './support/notes-api'

/**
 * Notifications (lvn-backend ADR-0042) against a mocked API and a mocked live socket: the bell's count, sentences
 * written from ids, marking read, and live events refreshing what is on screen.
 */

const TEACHER = '01920000-0000-7000-8000-00000000bbbb'
const id = (n: number) => `01920000-0000-7000-8000-0000000f000${n}`
const at = (minutesAgo: number) => new Date(Date.now() - minutesAgo * 60_000).toISOString()
const notification = (n: number, over: Record<string, unknown>) => ({ __typename: 'Notification', id: id(n), path: '/profile', data: null, readAt: null, createdAt: at(n * 5), actor: null, note: null, group: null, ...over })
const LIST = [
  notification(1, { category: 'SHARE', path: `/notes/${NOTE_ID}`, actor: { __typename: 'User', id: TEACHER, displayName: 'Meera Iyer' }, note: { __typename: 'Note', id: NOTE_ID, title: 'Binary heaps' } }),
  notification(2, { category: 'SHARE', path: '/notes/01920000-0000-7000-8000-00000000a0ff', actor: { __typename: 'User', id: TEACHER, displayName: 'Meera Iyer' } }),
  notification(3, { category: 'VERIFICATION', data: { kind: 'DECIDED', decision: 'APPROVED' }, actor: { __typename: 'User', id: TEACHER, displayName: 'Meera Iyer' }, readAt: at(1) }),
  notification(4, { category: 'NOTES_IMPORT', data: { created: 3, skipped: 1, failed: 0 }, readAt: at(1) }),
]
const page1 = (unread: number) => ({ notifications: { __typename: 'NotificationConnection', edges: LIST.map((node) => ({ __typename: 'NotificationEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } }, unreadNotificationCount: unread })

test('the bell counts what is unread, and the page says what happened in words', async ({ page }) => {
  let unread = 2
  const calls = await mockApi(page, {
    UnreadNotificationCount: () => ({ unreadNotificationCount: unread }),
    Notifications: () => page1(unread),
    MarkNotificationsRead: () => ((unread = 0), { markNotificationsRead: { __typename: 'MarkNotificationsReadPayload', unreadCount: 0, userErrors: [] } }),
  })
  await page.goto('/notifications')
  const bell = page.getByRole('link', { name: 'Notifications, 2 unread' })
  await expect(bell).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Notifications', level: 1 })).toBeVisible()
  await expect(page.getByText('Meera Iyer shared “Binary heaps” with you')).toBeVisible()
  await expect(page.getByText('Meera Iyer shared a note with you that you can no longer open')).toBeVisible()
  await expect(page.getByText('Meera Iyer verified your account')).toBeVisible()
  await expect(page.getByText('Your import is done: 3 notes added, 1 skipped')).toBeVisible()
  await expect(page.getByText('Unread')).toHaveCount(2)

  const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
  expect(violations.filter((v) => v.impact === 'critical' || v.impact === 'serious').map((v) => v.id)).toEqual([])

  await page.getByRole('button', { name: 'Mark all as read' }).click()
  await expect(page.getByRole('link', { name: 'Notifications', exact: true })).toBeVisible()
  await expect(page.getByText('Unread')).toHaveCount(0)
  expect(calls.find((c) => c.op === 'MarkNotificationsRead')?.variables).toEqual({ input: { all: true } })
})

test('opening a notification marks it read and goes where it points', async ({ page }) => {
  const calls = await mockApi(page, {
    UnreadNotificationCount: () => ({ unreadNotificationCount: 2 }),
    Notifications: () => page1(2),
    MarkNotificationsRead: () => ({ markNotificationsRead: { __typename: 'MarkNotificationsReadPayload', unreadCount: 1, userErrors: [] } }),
  })
  await page.goto('/notifications')
  await page.getByRole('button', { name: /Binary heaps/ }).click()
  await expect(page).toHaveURL(new RegExp(`/notes/${NOTE_ID}$`))
  expect(calls.find((c) => c.op === 'MarkNotificationsRead')?.variables).toEqual({ input: { ids: [id(1)] } })
})

test('a live event refreshes the count, over a socket that sends the access token', async ({ page }) => {
  const live = await mockLive(page)
  let unread = 1
  await mockApi(page, { UnreadNotificationCount: () => ({ unreadNotificationCount: unread }) })
  await page.goto('/notes')
  await expect(page.getByRole('link', { name: 'Notifications, 1 unread' })).toBeVisible()
  await expect.poll(() => live.subscriptions.length).toBeGreaterThan(0)
  expect(live.inits[0]).toEqual({ authorization: 'Bearer h.p.s' })
  unread = 3
  live.send({ kind: 'NOTIFICATION', id: id(9) })
  await expect(page.getByRole('link', { name: 'Notifications, 3 unread' })).toBeVisible()
})

test('the signed-in header fits a phone, 360 pixels wide too, with a full badge', async ({ page }) => {
  await mockApi(page, { UnreadNotificationCount: () => ({ unreadNotificationCount: 150 }) })
  for (const width of [360, 412]) {
    await page.setViewportSize({ width, height: 800 })
    await page.goto('/notifications')
    await expect(page.getByRole('link', { name: 'Notifications, 150 unread' })).toContainText('99+')
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(width)
  }
})

test('nothing for a visitor who is not signed in', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('link', { name: /^Notifications/ })).toHaveCount(0)
  expect(USER).toBeTruthy()
})
