import { expect, test } from '@playwright/test'
import { NOTE_ID, USER, cards, meta, mockApi, page1 } from './support/notes-api'

/** Moderation on the web (lvn-backend §15.1, ADR-0037, ADR-0051): reporting, what the owner is told, and the platform queue. */

const ok = (name: string) => ({ [name]: { ok: true, userErrors: [] } })
const ravi = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar', handle: 'ravi' }

test('a reader reports a note with a reason and a few words', async ({ page }) => {
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ viewerAccess: 'READER', owner: ravi, visibility: 'PUBLIC' }), cards: page1(cards) } }),
    ReportContent: () => ok('reportContent'),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await page.getByRole('button', { name: 'Report' }).click()
  const dialog = page.getByRole('dialog', { name: 'Report this note' })
  await expect(dialog.getByRole('button', { name: 'Send report' })).toBeDisabled()
  await dialog.getByText('Copied without permission').click()
  await dialog.getByLabel('Anything moderators should know (optional)').fill('Chapter 3 of my textbook')
  await dialog.getByRole('button', { name: 'Send report' }).click()
  await expect(dialog.getByText('Thank you for telling us')).toBeVisible()
  expect(calls.find((c) => c.op === 'ReportContent')?.variables).toEqual({ input: { entityType: 'NOTE', entityId: NOTE_ID, reason: 'COPYRIGHT', details: 'Chapter 3 of my textbook' } })
})

test('the owner of a hidden note sees why, cannot make it public, and appeals once', async ({ page }) => {
  const moderation = { __typename: 'NoteModeration', state: 'HIDDEN', reason: 'Copied from a book without permission.', canAppeal: true }
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ visibility: 'SHARED', moderation, publishedAt: new Date().toISOString(), publishedVersion: { __typename: 'NoteVersion', id: NOTE_ID, number: 1, createdAt: new Date().toISOString() } }), cards: page1(cards) } }),
    NoteShares: () => ({ note: { __typename: 'Note', id: NOTE_ID, visibility: 'SHARED', shares: [] } }),
    AppealModeration: () => ok('appealModeration'),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText('Hidden by moderators')).toBeVisible()
  await expect(page.getByText('Copied from a book without permission.')).toBeVisible()

  await page.getByRole('button', { name: 'Share', exact: true }).click()
  const share = page.getByRole('dialog', { name: 'Share this note' })
  await expect(share.getByRole('radio', { name: /Public/ })).toBeDisabled()
  await expect(share.getByText('Moderators took this note off the public pages. You can appeal from the note.')).toBeVisible()
  await share.getByRole('button', { name: 'Done' }).click()

  await page.getByRole('button', { name: 'Appeal' }).click()
  const appeal = page.getByRole('dialog', { name: 'Appeal this decision' })
  await appeal.getByLabel('Your message').fill('I wrote every word myself.')
  await appeal.getByRole('button', { name: 'Send appeal' }).click()
  await expect(page.getByText('Your appeal is with the moderators.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Appeal' })).toHaveCount(0)
  expect(calls.find((c) => c.op === 'AppealModeration')?.variables).toEqual({ input: { entityType: 'NOTE', entityId: NOTE_ID, message: 'I wrote every word myself.' } })
})

test('a platform admin works through the queue: reasons first, then the decision', async ({ page }) => {
  let open = true
  const item = {
    __typename: 'ModerationCase',
    entityType: 'NOTE',
    entityId: NOTE_ID,
    scope: 'PLATFORM',
    scopeId: null,
    content: null,
    group: null,
    openedAt: new Date(Date.now() - 3_600_000).toISOString(),
    note: { __typename: 'ModeratedNote', id: NOTE_ID, title: 'Free stuff', excerpt: 'Buy followers here, cheap.', visibility: 'PUBLIC', moderation: 'PENDING_REVIEW', moderationReason: 'Held', deleted: false, owner: ravi },
    user: null,
    reports: [
      { __typename: 'ModerationReport', reason: 'SPAM', details: 'Held on the way to the public: it contains words linked to spam.', createdAt: new Date().toISOString(), reporter: null },
      { __typename: 'ModerationReport', reason: 'SPAM', details: 'Ads', createdAt: new Date().toISOString(), reporter: { __typename: 'User', id: USER, displayName: 'Asha Rao' } },
    ],
    appeal: null,
  }
  const calls = await mockApi(
    page,
    {
      ModerationQueue: () => ({ moderationQueue: { edges: open ? [{ __typename: 'ModerationCaseEdge', node: item }] : [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
      ModerateContent: () => {
        open = false
        return ok('moderateContent')
      },
    },
    { globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/moderation')
  const card = page.getByRole('article', { name: 'Free stuff' })
  await expect(card.getByText('by Ravi Kumar (@ravi)')).toBeVisible()
  await expect(card.getByText('held automatically')).toBeVisible()
  await expect(card.getByText('Asha Rao')).toBeVisible()

  await card.getByRole('button', { name: 'Remove' }).click()
  await expect(card.getByRole('alert')).toHaveText('Write a reason first: the author is told.')
  expect(calls.some((c) => c.op === 'ModerateContent')).toBe(false)
  await card.getByLabel(/^Reason/).fill('Spam.')
  await card.getByRole('button', { name: 'Remove' }).click()
  await expect(page.getByText('Nothing to review. Thank you!')).toBeVisible()
  expect(calls.find((c) => c.op === 'ModerateContent')?.variables).toEqual({ input: { entityType: 'NOTE', entityId: NOTE_ID, action: 'REMOVE', reason: 'Spam.' } })
})

test('the queue is for platform admins only', async ({ page }) => {
  await mockApi(page, {})
  await page.goto('/admin/moderation')
  await expect(page.getByRole('heading', { name: 'Only moderators can see this page' })).toBeVisible()
})

test('platform admins see every scope: a group’s appealed post to put back or keep hidden, and a reported group (ADR-0051)', async ({ page }) => {
  const GROUP = '01920000-0000-7000-8000-0000000a0001'
  const at = new Date(Date.now() - 7_200_000).toISOString()
  const appealed = {
    __typename: 'ModerationCase', entityType: 'GROUP_POST', entityId: 'p2', scope: 'GROUP', scopeId: GROUP, openedAt: at, note: null, user: null, group: null, reports: [],
    content: { __typename: 'ModeratedContent', entityType: 'GROUP_POST', id: 'p2', excerpt: 'Idea: dark mode', moderation: 'HIDDEN', moderationReason: 'Off topic.', deleted: false, path: `/groups/${GROUP}`, author: ravi },
    appeal: { __typename: 'ModerationAppeal', message: 'It is on topic: the app needs it.', createdAt: at },
  }
  const reported = {
    __typename: 'ModerationCase', entityType: 'GROUP', entityId: GROUP, scope: 'PLATFORM', scopeId: null, openedAt: at, note: null, user: null, content: null, appeal: null,
    group: { __typename: 'Group', id: GROUP, name: 'Heaps club' },
    reports: [{ __typename: 'ModerationReport', reason: 'HATE', details: 'The group name', createdAt: at, reporter: { __typename: 'User', id: USER, displayName: 'Asha Rao' } }],
  }
  const calls = await mockApi(
    page,
    {
      ModerationQueue: () => ({ moderationQueue: { edges: [appealed, reported].map((node) => ({ __typename: 'ModerationCaseEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
      ModerateContent: () => ok('moderateContent'),
    },
    { globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/moderation')
  const post = page.getByRole('article', { name: 'Post' })
  await expect(post.getByText('In a group')).toBeVisible()
  expect(calls.find((c) => c.op === 'ModerationQueue')?.variables).not.toHaveProperty('scope')
  await expect(post.getByText('It is on topic: the app needs it.')).toBeVisible()
  await expect(post.getByRole('button', { name: 'Put it back' })).toBeVisible()
  await expect(post.getByRole('button', { name: 'Keep the decision' })).toBeVisible()
  await post.getByRole('button', { name: 'Put it back' }).click()
  expect(calls.find((c) => c.op === 'ModerateContent')?.variables).toEqual({ input: { entityType: 'GROUP_POST', entityId: 'p2', action: 'APPROVE', reason: null } })

  const group = page.getByRole('article', { name: 'Heaps club' })
  await expect(group.getByRole('link', { name: 'Heaps club' })).toHaveAttribute('href', `/groups/${GROUP}`)
  await expect(group.getByRole('button')).toHaveText(['Dismiss reports', 'Warn', 'Remove'])
})
