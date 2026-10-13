import { expect, test } from '@playwright/test'
import { mockApi, USER } from './support/notes-api'

/**
 * Resources (lvn-backend ADR-0074): a link or an ISBN fills the form; topics come from the curated list; it goes to
 * moderators and waits; a rejected one says why and is sent again; links are marked as user content; moderators
 * approve or reject in the queue.
 */
const ID = '01920000-0000-7000-8000-0000000e0001'
const TOPIC = { __typename: 'Topic', id: '01920000-0000-7000-8000-0000000f0001', title: 'Arrays' }
const me = { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' }
const resource = (over: Record<string, unknown> = {}) => ({
  __typename: 'Resource',
  id: ID,
  type: 'BOOK',
  title: 'Clean Code',
  description: 'Even bad code can function.',
  url: 'https://books.example.com/clean-code',
  host: 'books.example.com',
  isbn: '9780132350884',
  author: 'Robert C. Martin',
  coverUrl: null,
  topics: [TOPIC],
  submittedBy: me,
  status: 'PENDING',
  reason: null,
  decidedAt: null,
  createdAt: new Date().toISOString(),
  viewerCan: { __typename: 'ResourceActions', edit: true, delete: true, report: false },
  saveCount: 0,
  viewerSaved: false,
  ...over,
})
const preview = {
  __typename: 'ResourcePreview',
  url: 'https://books.example.com/clean-code',
  title: 'Clean Code',
  description: 'Even bad code can function.',
  author: 'Robert C. Martin',
  isbn: '9780132350884',
  type: 'BOOK',
  siteName: 'Example Books',
  imageUrl: null,
  found: true,
  existing: null,
}

test('adds a resource: the link fills the form, topics come from the list, and it waits for moderators', async ({ page }) => {
  let sent: Record<string, unknown> | null = null
  const calls = await mockApi(page, {
    ResourcePreview: () => ({ resourcePreview: preview }),
    ResourceTopicOptions: () => ({ resourceTopicOptions: [{ __typename: 'ExamTopicOption', id: TOPIC.id, title: 'Arrays', subjectTitle: 'Data Structures' }] }),
    SubmitResource: (v) => ((sent = v.input as Record<string, unknown>), { submitResource: { __typename: 'ResourcePayload', resource: resource(), userErrors: [] } }),
    MyResources: () => ({ myResources: [resource()] }),
    Resource: () => ({ resource: resource() }),
  })
  await page.goto('/resources/new')
  const form = page.getByRole('form', { name: 'Add a resource' })
  await form.getByLabel('Link').fill('https://books.example.com/clean-code?utm_source=x')
  await form.getByRole('button', { name: 'Fill in from the page' }).click()
  await expect(form.getByLabel('Title', { exact: true })).toHaveValue('Clean Code')
  await expect(form.getByRole('radio', { name: 'Book' })).toBeChecked()
  await expect(form.getByLabel('By (author or maker, optional)')).toHaveValue('Robert C. Martin')
  await expect(form.getByRole('button', { name: 'Send to moderators' })).toBeDisabled()
  await form.getByPlaceholder('Find a topic, e.g. arrays').fill('arr')
  await form.getByRole('button', { name: 'Add Arrays' }).click()
  await form.getByRole('button', { name: 'Send to moderators' }).click()
  await expect(page).toHaveURL(new RegExp(`/resources/${ID}$`))
  expect(sent).toEqual({ type: 'BOOK', title: 'Clean Code', url: 'https://books.example.com/clean-code', isbn: '9780132350884', author: 'Robert C. Martin', description: 'Even bad code can function.', topicIds: [TOPIC.id], coverFileId: null, imageUrl: null })
  expect(calls.find((c) => c.op === 'ResourcePreview')?.variables).toEqual({ input: { url: 'https://books.example.com/clean-code?utm_source=x' } })
  await expect(page.getByRole('note')).toContainText('Waiting for moderators: only you can see it until they approve it.')
})

test('a page that cannot be read leaves the form to the person; one already in the catalogue is named', async ({ page }) => {
  let answer: Record<string, unknown> = { ...preview, title: null, description: null, author: null, isbn: null, type: null, found: false }
  await mockApi(page, { ResourcePreview: () => ({ resourcePreview: answer }) })
  await page.goto('/resources/new')
  const form = page.getByRole('form', { name: 'Add a resource' })
  await form.getByLabel('Link').fill('https://example.com/course')
  await form.getByRole('button', { name: 'Fill in from the page' }).click()
  await expect(form.getByText('We could not read that page. Fill in the details yourself.')).toBeVisible()
  answer = { ...preview, existing: { __typename: 'Resource', id: ID, title: 'Clean Code' } }
  await form.getByRole('button', { name: 'Fill in from the page' }).click()
  await expect(form.getByRole('status')).toContainText('This is already in the catalogue:')
  await expect(form.getByRole('link', { name: 'Clean Code' })).toHaveAttribute('href', `/resources/${ID}`)
})

test('a rejected resource says why, and is edited and sent again', async ({ page }) => {
  let status = 'REJECTED'
  let updated: Record<string, unknown> | null = null
  await mockApi(page, {
    Resource: () => ({ resource: resource({ status, reason: status === 'REJECTED' ? 'This page sells the book; link to its publisher instead.' : null }) }),
    ResourceTopicOptions: () => ({ resourceTopicOptions: [] }),
    UpdateResource: (v) => ((updated = v.input as Record<string, unknown>), (status = 'PENDING'), { updateResource: { __typename: 'ResourcePayload', resource: resource(), userErrors: [] } }),
    MyResources: () => ({ myResources: [resource()] }),
  })
  await page.goto(`/resources/${ID}`)
  await expect(page.getByRole('note')).toContainText('Not approved')
  await expect(page.getByRole('note')).toContainText('This page sells the book; link to its publisher instead.')
  await page.getByRole('link', { name: 'Edit and send again' }).click()
  const form = page.getByRole('form', { name: 'Edit your resource' })
  await form.getByLabel('Link').fill('https://publisher.example.com/clean-code')
  await form.getByRole('button', { name: 'Save and send again' }).click()
  await expect(page).toHaveURL(new RegExp(`/resources/${ID}$`))
  expect(updated).toMatchObject({ id: ID, url: 'https://publisher.example.com/clean-code', topicIds: [TOPIC.id], removeCover: false })
})

test('an approved resource: its link is marked as user content, the page stays out of search engines, and others can report it', async ({ page }) => {
  await mockApi(page, { Resource: () => ({ resource: resource({ status: 'APPROVED', submittedBy: { __typename: 'User', id: 'someone-else', displayName: 'Ravi Kumar', handle: 'ravi' }, viewerCan: { __typename: 'ResourceActions', edit: false, delete: false, report: true } }) }) })
  await page.goto(`/resources/${ID}`)
  await expect(page.getByRole('heading', { name: 'Clean Code' })).toBeVisible()
  const link = page.getByRole('link', { name: 'Open books.example.com' })
  await expect(link).toHaveAttribute('rel', 'ugc nofollow noopener')
  await expect(link).toHaveAttribute('href', 'https://books.example.com/clean-code')
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute('content', /noindex/)
  await expect(page.getByRole('note')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Report' })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Edit' })).toHaveCount(0)
})

test('one’s resources, each with its state, from the account page', async ({ page }) => {
  await mockApi(page, {
    MyDataExports: () => ({ myDataExports: [] }),
    NoteImports: () => ({ noteImports: [] }),
    MyVerificationRequests: () => ({ myVerificationRequests: [] }),
    MyResources: () => ({ myResources: [resource({ status: 'APPROVED', viewerCan: { __typename: 'ResourceActions', edit: false, delete: true, report: false } }), resource({ id: `${ID.slice(0, -1)}2`, title: 'A sales page', status: 'REJECTED', reason: 'A shop, not a resource.' })] }),
  }, { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } })
  await page.goto('/profile')
  await page.getByRole('link', { name: 'Your resources' }).click()
  await expect(page).toHaveURL(/\/resources\/mine$/)
  const items = page.getByRole('listitem')
  await expect(items).toHaveCount(2)
  await expect(items.nth(0)).toContainText('In the catalogue')
  await expect(items.nth(1)).toContainText('Not approved')
  await expect(items.nth(1)).toContainText('A shop, not a resource.')
  await expect(page.getByRole('link', { name: 'Add a resource' })).toHaveAttribute('href', '/resources/new')
})

test('moderators approve a new resource, and reject another with a reason', async ({ page }) => {
  const at = new Date(Date.now() - 3_600_000).toISOString()
  const kase = (id: string, title: string) => ({
    __typename: 'ModerationCase', resource: resource({ id, title }), suspendedUntil: null, removedGroup: null, entityType: 'RESOURCE', entityId: id, scope: 'PLATFORM', scopeId: null, openedAt: at, note: null, user: null, content: null, group: null, appeal: null,
    reports: [{ __typename: 'ModerationReport', reason: 'OTHER', details: 'New resource, waiting for approval.', createdAt: at, reporter: null }],
  })
  let open = [kase(ID, 'Clean Code'), kase(`${ID.slice(0, -1)}2`, 'Buy cheap textbooks')]
  const calls = await mockApi(page, {
    ModerationQueue: () => ({ moderationQueue: { edges: open.map((node) => ({ __typename: 'ModerationCaseEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    ModerateContent: (v) => {
      const input = v.input as { entityId: string }
      open = open.filter((c) => c.entityId !== input.entityId)
      return { moderateContent: { __typename: 'OkPayload', ok: true, userErrors: [] } }
    },
  }, { globalRole: 'PLATFORM_ADMIN' })
  await page.goto('/admin/moderation')
  const good = page.getByRole('article', { name: 'Clean Code' })
  await expect(good.getByText('Resource', { exact: true })).toBeVisible()
  await expect(good.getByRole('link', { name: 'https://books.example.com/clean-code' })).toHaveAttribute('rel', 'ugc nofollow noopener')
  await good.getByRole('button', { name: 'Approve' }).click()
  await expect(good).toHaveCount(0)
  const bad = page.getByRole('article', { name: 'Buy cheap textbooks' })
  await bad.getByRole('button', { name: 'Reject' }).click()
  await expect(bad.getByRole('alert')).toHaveText('Write a reason first: the author is told.')
  await bad.getByLabel(/^Reason/).fill('A shop, not a resource.')
  await bad.getByRole('button', { name: 'Reject' }).click()
  await expect(bad).toHaveCount(0)
  expect(calls.filter((c) => c.op === 'ModerateContent').map((c) => c.variables.input)).toEqual([
    { entityType: 'RESOURCE', entityId: ID, action: 'APPROVE', reason: null },
    { entityType: 'RESOURCE', entityId: `${ID.slice(0, -1)}2`, action: 'REMOVE', reason: 'A shop, not a resource.' },
  ])
})
