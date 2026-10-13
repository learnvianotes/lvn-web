import { expect, test } from '@playwright/test'
import { mockApi, USER } from './support/notes-api'

/**
 * Finding resources (lvn-backend ADR-0075): the catalogue with filters, saves with counts, recommending to a person or
 * a group with a reason, the group's Resources tab, resources in search and the resource discussion.
 */
const ID = '01920000-0000-7000-8000-0000000e0011'
const GROUP = '01920000-0000-7000-8000-0000000a0011'
const ravi = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Ravi Kumar', handle: 'ravi' }
const resource = (over: Record<string, unknown> = {}) => ({
  __typename: 'Resource',
  id: ID,
  type: 'COURSE',
  title: 'Data Structures, NPTEL',
  description: 'Twelve weeks on arrays, trees and graphs.',
  url: 'https://nptel.ac.in/courses/106102064',
  host: 'nptel.ac.in',
  isbn: null,
  author: 'IIT Delhi',
  coverUrl: null,
  topics: [{ __typename: 'Topic', id: '01920000-0000-7000-8000-0000000f0011', title: 'Arrays' }],
  submittedBy: ravi,
  status: 'APPROVED',
  reason: null,
  decidedAt: null,
  createdAt: new Date().toISOString(),
  viewerCan: { __typename: 'ResourceActions', edit: false, delete: false, report: true },
  saveCount: 2,
  viewerSaved: false,
  ...over,
})
const page1 = (nodes: unknown[]) => ({ __typename: 'ResourceConnection', edges: nodes.map((node) => ({ __typename: 'ResourceEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } })

test('browses the catalogue: type and words filter it, sort changes, and a resource is saved', async ({ page }) => {
  let saved = false
  const calls = await mockApi(page, {
    Resources: () => ({ resources: page1([resource({ viewerSaved: saved, saveCount: saved ? 3 : 2 })]) }),
    SaveResource: () => ((saved = true), { saveResource: { __typename: 'ResourcePayload', resource: { __typename: 'Resource', id: ID, saveCount: 3, viewerSaved: true }, userErrors: [] } }),
  })
  await page.goto('/resources')
  const card = page.getByRole('article', { name: 'Data Structures, NPTEL' })
  await expect(card).toContainText('nptel.ac.in')
  await expect(card).toContainText('Saved by 2 people')
  await page.getByRole('radio', { name: 'Course' }).click()
  await page.getByLabel('Search resources').fill('graphs')
  await page.getByLabel('Sort').selectOption('NEWEST')
  await expect.poll(() => calls.filter((c) => c.op === 'Resources').at(-1)?.variables).toEqual({ filter: { type: 'COURSE', query: 'graphs' }, sort: 'NEWEST', first: 24 })
  await card.getByRole('button', { name: 'Save' }).click()
  await expect(card.getByRole('button', { name: 'Saved' })).toHaveAttribute('aria-pressed', 'true')
  await expect(card).toContainText('Saved by 3 people')
})

test('recommends a resource to a group with a reason; the group’s Resources tab shows it with who and why', async ({ page }) => {
  let recommended: Record<string, unknown> | null = null
  await mockApi(page, {
    Resource: () => ({ resource: resource() }),
    Discussion: () => ({ discussion: null }),
    MyGroups: () => ({ myGroups: [{ __typename: 'Group', id: GROUP, type: 'COMMUNITY', name: 'CSE 3rd Year', description: null, privacy: 'PRIVATE', joinPolicy: 'APPROVAL', memberCount: 124, viewerRole: 'MEMBER' }] }),
    RecommendResource: (v) => ((recommended = v.input as Record<string, unknown>), { recommendResource: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await page.goto(`/resources/${ID}`)
  await expect(page.getByRole('heading', { name: 'Data Structures, NPTEL' })).toBeVisible()
  await page.getByRole('button', { name: 'Recommend' }).click()
  const dialog = page.getByRole('dialog', { name: 'Recommend this resource' })
  await dialog.getByRole('tab', { name: 'A group' }).click()
  await dialog.getByRole('radio', { name: 'CSE 3rd Year' }).click()
  await dialog.getByLabel('Why (optional)').fill('Weeks 3 and 4 are exactly our syllabus')
  await dialog.getByRole('button', { name: 'Recommend' }).click()
  await expect(dialog.getByRole('status')).toHaveText('Recommended to CSE 3rd Year.')
  expect(recommended).toEqual({ resourceId: ID, to: { groupId: GROUP }, reason: 'Weeks 3 and 4 are exactly our syllabus' })
})

test('a person the API refuses is told why', async ({ page }) => {
  await mockApi(page, {
    Resource: () => ({ resource: resource() }),
    Discussion: () => ({ discussion: null }),
    Search: () => ({ search: { __typename: 'SearchResults', notes: [], notesCursor: null, topics: [], groups: [], classrooms: [], resources: [], people: [{ __typename: 'User', id: '01920000-0000-7000-8000-00000000cccc', handle: 'kiran', displayName: 'Kiran Rao', globalRole: 'STUDENT' }] } }),
    RecommendResource: () => ({ recommendResource: { __typename: 'OkPayload', ok: false, userErrors: [{ __typename: 'UserError', field: null, message: 'Recommend to people you follow, are connected to, or share a group or class with.', code: 'FORBIDDEN' }] } }),
  })
  await page.goto(`/resources/${ID}`)
  await page.getByRole('button', { name: 'Recommend' }).click()
  const dialog = page.getByRole('dialog', { name: 'Recommend this resource' })
  await dialog.getByLabel('Find a person by name or @handle').fill('kiran')
  await dialog.getByRole('radio', { name: 'Kiran Rao (@kiran)' }).click()
  await dialog.getByRole('button', { name: 'Recommend' }).click()
  await expect(dialog.getByRole('alert')).toHaveText('Recommend to people you follow, are connected to, or share a group or class with.')
})

test('a group’s Resources tab lists what members recommended, with who and why', async ({ page }) => {
  await mockApi(page, {
    Group: () => ({ group: { __typename: 'Group', id: GROUP, type: 'COMMUNITY', name: 'CSE 3rd Year', description: null, privacy: 'PRIVATE', joinPolicy: 'APPROVAL', memberCount: 124, viewerRole: 'MEMBER', createdAt: new Date().toISOString(), moderationWarning: null, pendingRequestId: null, mentorInviteId: null, owner: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' }, repository: null, mentor: null, viewerCan: { __typename: 'GroupActions', join: false, requestJoin: false, post: true, moderate: false, manage: false, delete: false, reviewRequests: false, leave: true, askDoubt: false, inviteMentor: false, acceptMentorInvite: false } } }),
    GroupPosts: () => ({ group: { __typename: 'Group', id: GROUP, pinned: [], posts: { __typename: 'GroupPostConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
    ResourceRecommendations: () => ({ resourceRecommendations: { __typename: 'ResourceRecommendationConnection', edges: [{ __typename: 'ResourceRecommendationEdge', node: { __typename: 'ResourceRecommendation', id: 'rr1', reason: 'Weeks 3 and 4 are our syllabus', createdAt: new Date().toISOString(), viewerCanRemove: false, from: ravi, resource: resource() } }], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
  })
  await page.goto(`/groups/${GROUP}`)
  await page.getByRole('tab', { name: 'Resources' }).click()
  const card = page.getByRole('article', { name: 'Data Structures, NPTEL' })
  await expect(card).toContainText('Ravi Kumar: Weeks 3 and 4 are our syllabus')
  await expect(page.getByRole('button', { name: 'Remove' })).toHaveCount(0)
})

test('⌘K finds resources beside notes and people', async ({ page }) => {
  await mockApi(page, {
    Search: () => ({ search: { __typename: 'SearchResults', notes: [], notesCursor: null, people: [], topics: [], groups: [], classrooms: [], resources: [{ __typename: 'Resource', id: ID, type: 'COURSE', title: 'Data Structures, NPTEL', host: 'nptel.ac.in', author: 'IIT Delhi', saveCount: 2 }] } }),
    Resource: () => ({ resource: resource() }),
    Discussion: () => ({ discussion: null }),
    SavedResources: () => ({ savedResources: page1([]) }),
  })
  await page.goto('/resources/saved')
  await expect(page.getByRole('heading', { name: 'Your saved resources' })).toBeVisible()
  await page.keyboard.press('Control+k')
  const palette = page.getByRole('dialog', { name: 'Search notes, people, groups and topics' })
  await palette.getByRole('combobox').fill('data structures')
  await palette.getByRole('option', { name: /Data Structures, NPTEL/ }).click()
  await expect(page).toHaveURL(new RegExp(`/resources/${ID}$`))
})
