import { expect, test } from '@playwright/test'
import { mockApi, NOTE_ID, USER } from './support/notes-api'

/** Project workspaces (lvn-backend ADR-0048) against a mocked API: starting one, the repository, ideas, doubts, mentors. */

const GROUP = '01920000-0000-7000-8000-0000000a0009'
const OTHER = '01920000-0000-7000-8000-00000000bbbb'
const DOUBT = '01920000-0000-7000-8000-0000000d0001'
const meera = { __typename: 'User', id: OTHER, displayName: 'Meera Iyer', handle: 'meera' }
const asha = { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' }
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const can = (over: Record<string, boolean> = {}) => ({ __typename: 'GroupActions', join: false, requestJoin: false, post: true, moderate: false, manage: false, delete: false, reviewRequests: false, leave: true, askDoubt: true, inviteMentor: false, acceptMentorInvite: false, ...over })
const workspace = (over: Record<string, unknown> = {}) => ({
  __typename: 'Group', id: GROUP, type: 'PROJECT', name: 'Heap visualiser', description: 'Watch a heap grow', privacy: 'PUBLIC', joinPolicy: 'OPEN', memberCount: 4, viewerRole: 'MEMBER', createdAt: '2026-10-01T10:00:00.000Z',
  viewerRequestId: null, viewerMentorInviteId: null, moderationWarning: null, owner: { __typename: 'User', id: OTHER, displayName: 'Meera Iyer' }, viewerCan: can(), ...over,
})
const repo = (over: Record<string, unknown> = {}) => ({ __typename: 'GroupRepository', provider: 'GITHUB', url: 'https://github.com/team/heap-viz', available: true, name: 'team/heap-viz', description: 'Watch a heap grow', language: 'TypeScript', stars: 42, pushedAt: '2026-10-10T09:00:00.000Z', ...over })
const posts = () => ({ group: { __typename: 'Group', id: GROUP, posts: { __typename: 'GroupPostConnection', pinned: [], edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } })
const idea = (id: string, text: string) => ({ __typename: 'GroupPost', id, kind: 'IDEA', moderation: 'OK', moderationReason: null, moderationCanAppeal: false, body: doc(text), pinned: false, createdAt: new Date().toISOString(), editedAt: null, author: meera, viewerCan: { __typename: 'GroupPostActions', edit: false, delete: false, pin: false }, discussion: { __typename: 'Discussion', commentCount: 0 } })
const summary = (status: string) => ({ __typename: 'Doubt', id: DOUBT, title: 'Why does sift-down swap twice?', moderation: 'OK', moderationReason: null, moderationCanAppeal: false, status, repoRef: 'src/heap.ts:42', createdAt: new Date().toISOString(), answerCount: status === 'OPEN' ? 0 : 1, author: asha })

test('a project workspace starts from the new group dialog', async ({ page }) => {
  const calls = await mockApi(page, {
    MyGroups: () => ({ myGroups: [] }),
    MyMentorInvites: () => ({ myMentorInvites: [] }),
    DiscoverGroups: () => ({ discoverGroups: [] }),
    CreateGroup: () => ({ createGroup: { __typename: 'GroupPayload', group: workspace({ viewerRole: 'OWNER' }), userErrors: [] } }),
    Group: () => ({ group: workspace({ viewerRole: 'OWNER', viewerCan: can({ manage: true, delete: true, inviteMentor: true, moderate: true, reviewRequests: true }) }) }),
    GroupPosts: posts,
    Workspace: () => ({ group: { __typename: 'Group', id: GROUP, repository: null, showcase: null } }),
  })
  await page.goto('/groups')
  await page.getByRole('button', { name: 'New group' }).click()
  const dialog = page.getByRole('dialog', { name: 'New group' })
  await dialog.getByLabel('Name').fill('Heap visualiser')
  await dialog.getByLabel(/Project workspace/).check()
  await dialog.getByRole('button', { name: 'Create group' }).click()
  await expect(page).toHaveURL(new RegExp(`/groups/${GROUP}$`))
  expect(calls.find((c) => c.op === 'CreateGroup')?.variables).toMatchObject({ input: { name: 'Heap visualiser', type: 'PROJECT' } })
  await expect(page.getByRole('tab')).toHaveText(['Posts', 'Ideas', 'Doubts', 'Notes', 'Members', 'Requests', 'Reports', 'Settings'])
  await expect(page.getByText('No repository linked yet.')).toBeVisible()
})

test('the repository card shows its public details; admins link one', async ({ page }) => {
  let linked: ReturnType<typeof repo> | null = null
  const calls = await mockApi(page, {
    Group: () => ({ group: workspace({ viewerRole: 'ADMIN', viewerCan: can({ manage: true, inviteMentor: true, moderate: true, reviewRequests: true }) }) }),
    GroupPosts: posts,
    Workspace: () => ({ group: { __typename: 'Group', id: GROUP, repository: linked, showcase: null } }),
    SetGroupRepository: () => ((linked = repo()), { setGroupRepository: { __typename: 'GroupPayload', group: { __typename: 'Group', id: GROUP }, userErrors: [] } }),
  })
  await page.goto(`/groups/${GROUP}`)
  await page.getByRole('button', { name: 'Link a repository' }).click()
  await page.getByLabel('Repository address').fill('https://github.com/team/heap-viz')
  await page.getByRole('button', { name: 'Save', exact: true }).click()
  await expect(page.getByRole('link', { name: /team\/heap-viz/ })).toHaveAttribute('href', 'https://github.com/team/heap-viz')
  await expect(page.getByRole('link', { name: /team\/heap-viz/ })).toHaveAttribute('rel', 'noopener noreferrer nofollow ugc')
  await expect(page.getByText('42 stars')).toBeVisible()
  await expect(page.getByText('TypeScript')).toBeVisible()
  expect(calls.find((c) => c.op === 'SetGroupRepository')?.variables).toEqual({ groupId: GROUP, url: 'https://github.com/team/heap-viz' })
})

test('the ideas board ranks ideas and takes new ones', async ({ page }) => {
  let ideas = [idea('i1', 'Animate sift-down'), idea('i2', 'Dark mode')]
  const calls = await mockApi(page, {
    Group: () => ({ group: workspace() }),
    GroupPosts: posts,
    Workspace: () => ({ group: { __typename: 'Group', id: GROUP, repository: null, showcase: null } }),
    WorkspaceIdeas: () => ({ group: { __typename: 'Group', id: GROUP, ideas } }),
    CreateIdea: () => ((ideas = [...ideas, idea('i3', 'Sound on swap')]), { createGroupPost: { __typename: 'GroupPostPayload', post: { __typename: 'GroupPost', id: 'i3' }, userErrors: [] } }),
  })
  await page.goto(`/groups/${GROUP}`)
  await page.getByRole('tab', { name: 'Ideas' }).click()
  const board = page.getByRole('tabpanel').getByRole('list').first()
  await expect(board.getByRole('listitem').first()).toContainText('Animate sift-down')
  await expect(board.getByLabel('Rank 1')).toBeVisible()
  await page.getByLabel('Share an idea').fill('Sound on swap')
  await page.getByRole('button', { name: 'Share idea' }).click()
  await expect(board.getByRole('listitem')).toHaveCount(3)
  expect(calls.find((c) => c.op === 'CreateIdea')?.variables).toEqual({ groupId: GROUP, body: doc('Sound on swap') })
})

test('a member asks a doubt and lands on it; the mentor’s answer is marked; the asker resolves it', async ({ page }) => {
  let status = 'OPEN'
  const detail = () => ({
    ...summary(status), body: doc('See the loop'), resolvedAt: null,
    viewerCan: { __typename: 'DoubtActions', answer: status !== 'RESOLVED', resolve: status !== 'RESOLVED', reopen: status === 'RESOLVED', delete: true },
    answers: status === 'OPEN' ? [] : [{ __typename: 'DoubtAnswer', id: 'a1', body: doc('It swaps the larger child'), byMentor: true, createdAt: new Date().toISOString(), author: meera }],
  })
  const calls = await mockApi(page, {
    Group: () => ({ group: workspace() }),
    GroupPosts: posts,
    Workspace: () => ({ group: { __typename: 'Group', id: GROUP, repository: null, showcase: null } }),
    WorkspaceDoubts: () => ({ group: { __typename: 'Group', id: GROUP, doubts: { __typename: 'DoubtConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
    AskDoubt: () => ({ askDoubt: { __typename: 'DoubtPayload', doubt: { __typename: 'Doubt', id: DOUBT }, userErrors: [] } }),
    Doubt: () => ((status = status === 'OPEN' && calls.some((c) => c.op === 'Doubt') ? 'ANSWERED' : status), { doubt: detail() }),
    ResolveDoubt: () => ((status = 'RESOLVED'), { resolveDoubt: { __typename: 'DoubtPayload', doubt: detail(), userErrors: [] } }),
  })
  await page.goto(`/groups/${GROUP}`)
  await page.getByRole('tab', { name: 'Doubts' }).click()
  await expect(page.getByText('No doubts here.')).toBeVisible()
  await page.getByRole('button', { name: 'Ask a doubt' }).click()
  await page.getByLabel('Your question').fill('Why does sift-down swap twice?')
  await page.getByLabel('Details').fill('See the loop')
  await page.getByLabel('Where in the repository (optional)').fill('src/heap.ts:42')
  await page.getByRole('button', { name: 'Ask', exact: true }).click()
  await expect(page).toHaveURL(new RegExp(`/groups/${GROUP}/doubts/${DOUBT}$`))
  expect(calls.find((c) => c.op === 'AskDoubt')?.variables).toEqual({ input: { groupId: GROUP, title: 'Why does sift-down swap twice?', body: doc('See the loop'), repoRef: 'src/heap.ts:42' } })
  await expect(page.getByRole('heading', { name: 'Why does sift-down swap twice?' })).toBeVisible()
  await page.reload()
  await expect(page.getByText('It swaps the larger child')).toBeVisible()
  await expect(page.getByText('Mentor', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Mark resolved' }).click()
  await expect(page.getByText('This doubt is resolved. Reopen it to answer again.')).toBeVisible()
})

test('a teacher answers an invite to mentor from the groups page', async ({ page }) => {
  let invited = true
  const calls = await mockApi(
    page,
    {
      MyGroups: () => ({ myGroups: [] }),
      DiscoverGroups: () => ({ discoverGroups: [] }),
      MyMentorInvites: () => ({ myMentorInvites: invited ? [{ __typename: 'MentorInviteItem', id: 'mi1', expiresAt: '2026-10-27T10:00:00.000Z', group: { __typename: 'Group', id: GROUP, name: 'Heap visualiser' }, invitedBy: meera }] : [] }),
      AnswerMentorInvite: () => ((invited = false), { answerMentorInvite: { __typename: 'GroupPayload', group: workspace({ viewerRole: 'MENTOR' }), userErrors: [] } }),
    },
    { globalRole: 'TEACHER' },
  )
  await page.goto('/groups')
  await expect(page.getByText('Meera Iyer asked you to mentor this project')).toBeVisible()
  await page.getByRole('button', { name: 'Accept' }).click()
  await expect(page.getByText('Invites to mentor')).toHaveCount(0)
  expect(calls.find((c) => c.op === 'AnswerMentorInvite')?.variables).toEqual({ inviteId: 'mi1', accept: true })
})

test('a showcase note credits the team and its mentor', async ({ page }) => {
  await mockApi(page, {
    NoteToEdit: () => ({
      note: {
        __typename: 'Note', id: NOTE_ID, title: 'Heap visualiser', slug: 'heap-visualiser', kind: 'PROJECT', visibility: 'PUBLIC', viewerAccess: 'READER',
        viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true },
        owner: asha, folder: null, tags: [], topics: [], draftRevision: null, draftUpdatedAt: new Date().toISOString(), publishedAt: new Date().toISOString(), publishedVersion: null, forkingEnabled: true, moderation: null, forkedFrom: null, cardCount: 0, deletedAt: null,
        cards: { edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } },
      },
    }),
    NoteContributors: () => ({ note: { __typename: 'Note', id: NOTE_ID, contributors: [{ __typename: 'NoteContributor', role: 'CONTRIBUTOR', user: asha }, { __typename: 'NoteContributor', role: 'MENTOR', user: meera }] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  await expect(page.getByText(/Built by/)).toContainText('Built by Asha Rao · mentored by Meera Iyer')
  await expect(page.getByRole('link', { name: 'Meera Iyer' })).toHaveAttribute('href', '/u/meera')
})
