import { expect, test } from '@playwright/test'
import { mockApi, NOTE_ID, USER } from './support/notes-api'

/** Groups (lvn-backend ADR-0045) against a mocked API: finding and starting one, asking to join, posts, notes, members. */

const GROUP = '01920000-0000-7000-8000-0000000a0001'
const OTHER = '01920000-0000-7000-8000-00000000bbbb'
const can = (over: Record<string, boolean> = {}) => ({ __typename: 'GroupActions', join: false, requestJoin: false, post: false, moderate: false, manage: false, delete: false, reviewRequests: false, leave: false, askDoubt: false, inviteMentor: false, acceptMentorInvite: false, ...over })
const group = (over: Record<string, unknown> = {}) => ({
  __typename: 'Group', id: GROUP, type: 'COMMUNITY', name: 'Algorithms study', description: 'Weekly problems and solutions', privacy: 'PUBLIC', joinPolicy: 'APPROVAL', memberCount: 12, viewerRole: null, createdAt: '2026-10-01T10:00:00.000Z', viewerRequestId: null, viewerMentorInviteId: null,
  owner: { __typename: 'User', id: OTHER, displayName: 'Meera Iyer' }, viewerCan: can(), ...over,
})
const card = (id: string, name: string, viewerRole: string | null = null) => ({ __typename: 'Group', id, type: 'COMMUNITY', name, description: null, privacy: 'PUBLIC', joinPolicy: 'OPEN', memberCount: 3, viewerRole })
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const post = (id: string, text: string, over: Record<string, unknown> = {}) => ({ __typename: 'GroupPost', id, kind: 'POST', body: doc(text), pinned: false, createdAt: new Date().toISOString(), editedAt: null, author: { __typename: 'User', id: OTHER, displayName: 'Meera Iyer', handle: 'meera' }, viewerCan: { __typename: 'GroupPostActions', edit: false, delete: false, pin: false }, discussion: { __typename: 'Discussion', commentCount: 0 }, ...over })
const page = (pinned: unknown[], nodes: unknown[]) => ({ group: { __typename: 'Group', id: GROUP, posts: { __typename: 'GroupPostConnection', pinned, edges: nodes.map((node) => ({ __typename: 'GroupPostEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } })

test('your groups, public groups to find, and starting a new one', async ({ page: p }) => {
  const calls = await mockApi(p, {
    MyGroups: () => ({ myGroups: [card('01920000-0000-7000-8000-0000000a0002', 'Compilers club', 'OWNER')] }),
    MyMentorInvites: () => ({ myMentorInvites: [] }),
    DiscoverGroups: (v) => ({ discoverGroups: v.query ? [card(GROUP, 'Algorithms study')] : [card(GROUP, 'Algorithms study'), card('01920000-0000-7000-8000-0000000a0002', 'Compilers club', 'OWNER')] }),
    CreateGroup: () => ({ createGroup: { __typename: 'GroupPayload', group: group({ viewerRole: 'OWNER' }), userErrors: [] } }),
    Group: () => ({ group: group({ viewerRole: 'OWNER', viewerCan: can({ post: true, moderate: true, manage: true, delete: true, reviewRequests: true }) }) }),
    GroupPosts: () => page([], []),
  })
  await p.goto('/groups')
  await expect(p.getByRole('link', { name: /Compilers club/ })).toHaveAttribute('href', '/groups/01920000-0000-7000-8000-0000000a0002')
  // Groups one is in are not offered again under "Find a group".
  await expect(p.getByRole('link', { name: /Algorithms study/ })).toHaveCount(1)
  await p.getByRole('button', { name: 'New group' }).click()
  const dialog = p.getByRole('dialog', { name: 'New group' })
  await dialog.getByLabel('Name').fill('Algorithms study')
  await dialog.getByLabel('Private').check()
  await expect(dialog.getByLabel('Let people join without approval')).toHaveCount(0)
  await dialog.getByLabel('Public').check()
  await dialog.getByLabel('Let people join without approval').check()
  await dialog.getByRole('button', { name: 'Create group' }).click()
  await expect(p).toHaveURL(new RegExp(`/groups/${GROUP}$`))
  expect(calls.find((c) => c.op === 'CreateGroup')?.variables).toEqual({ input: { name: 'Algorithms study', description: null, privacy: 'PUBLIC', joinPolicy: 'OPEN', type: 'COMMUNITY' } })
})

test('someone outside asks to join with a note for the admins; inside stays closed', async ({ page: p }) => {
  let waiting = false
  const calls = await mockApi(p, {
    Group: () => ({ group: group(waiting ? { viewerRequestId: 'r1' } : { viewerCan: can({ requestJoin: true }) }) }),
    RequestToJoinGroup: () => ((waiting = true), { requestToJoinGroup: { __typename: 'GroupPayload', group: group({ viewerRequestId: 'r1' }), userErrors: [] } }),
  })
  await p.goto(`/groups/${GROUP}`)
  await expect(p.getByRole('heading', { name: 'Algorithms study' })).toBeVisible()
  await expect(p.getByText('Posts, notes and members are for members. Join to see them.')).toBeVisible()
  await p.getByRole('button', { name: 'Ask to join' }).click()
  await p.getByLabel('A note for the admins (optional)').fill('I study graphs')
  await p.getByRole('button', { name: 'Send request' }).click()
  await expect(p.getByText('Your request is waiting for an answer.')).toBeVisible()
  expect(calls.find((c) => c.op === 'RequestToJoinGroup')?.variables).toEqual({ groupId: GROUP, message: 'I study graphs' })
})

test('members post, pinned posts come first, and moderators can pin and delete', async ({ page: p }) => {
  let posts = [post('p2', 'Week 2 is up')]
  const calls = await mockApi(p, {
    Group: () => ({ group: group({ viewerRole: 'MODERATOR', viewerCan: can({ post: true, moderate: true, leave: true }) }) }),
    GroupPosts: () => page([post('p1', 'Read the rules', { pinned: true, viewerCan: { __typename: 'GroupPostActions', edit: false, delete: true, pin: true } })], posts),
    CreateGroupPost: (v) => {
      const created = post('p3', 'Hello all', { author: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' } })
      posts = [created, ...posts]
      return { createGroupPost: { __typename: 'GroupPostPayload', post: created, userErrors: [], _v: v } }
    },
  })
  await p.goto(`/groups/${GROUP}`)
  const items = p.getByRole('tabpanel').getByRole('listitem')
  await expect(items).toHaveCount(2)
  await expect(items.first()).toContainText('Read the rules')
  await expect(items.first()).toContainText('Pinned')
  await expect(items.first().getByRole('button', { name: 'Unpin' })).toBeVisible()
  await p.getByLabel('Write a post').fill('Hello all\nSee you Friday')
  await p.getByRole('button', { name: 'Post', exact: true }).click()
  await expect(items).toHaveCount(3)
  expect(calls.find((c) => c.op === 'CreateGroupPost')?.variables).toEqual({ groupId: GROUP, body: { type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: 'Hello all' }] }, { type: 'paragraph', content: [{ type: 'text', text: 'See you Friday' }] }] } })
})

test('a member shares one of their notes with the group', async ({ page: p }) => {
  let shared = false
  const calls = await mockApi(p, {
    Group: () => ({ group: group({ viewerRole: 'MEMBER', viewerCan: can({ post: true, leave: true }) }) }),
    GroupPosts: () => page([], []),
    GroupNotes: () => ({ group: { __typename: 'Group', id: GROUP, sharedNotes: { __typename: 'NoteConnection', edges: shared ? [{ __typename: 'NoteEdge', node: { __typename: 'Note', id: NOTE_ID, title: 'Binary heaps', kind: 'NOTE', visibility: 'SHARED', publishedAt: null, owner: { __typename: 'User', id: USER, displayName: 'Asha Rao' } } }] : [] } } }),
    MyNotes: () => ({ myNotes: { __typename: 'NoteConnection', edges: [{ __typename: 'NoteEdge', node: { __typename: 'Note', id: NOTE_ID, title: 'Binary heaps' } }], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    ShareNoteToGroup: () => ((shared = true), { shareNoteToGroup: { __typename: 'NotePayload', note: { __typename: 'Note', id: NOTE_ID, visibility: 'SHARED' }, userErrors: [] } }),
  })
  await p.goto(`/groups/${GROUP}`)
  await p.getByRole('tab', { name: 'Notes' }).click()
  await p.getByLabel('Share one of your notes').selectOption({ label: 'Binary heaps' })
  await p.getByRole('button', { name: 'Share', exact: true }).click()
  await expect(p.getByRole('link', { name: /Binary heaps/ })).toHaveAttribute('href', `/notes/${NOTE_ID}`)
  expect(calls.find((c) => c.op === 'ShareNoteToGroup')?.variables).toEqual({ noteId: NOTE_ID, groupId: GROUP })
})

test('admins answer requests to join', async ({ page: p }) => {
  let pending = true
  const admin = () => group({ viewerRole: 'ADMIN', viewerCan: can({ post: true, moderate: true, manage: true, reviewRequests: true, leave: true }) })
  const calls = await mockApi(p, {
    Group: () => ({ group: admin() }),
    GroupPosts: () => page([], []),
    GroupMembers: () => ({
      group: {
        __typename: 'Group', id: GROUP, viewerRole: 'ADMIN',
        members: [{ __typename: 'GroupMember', role: 'OWNER', joinedAt: '2026-10-01T10:00:00.000Z', mutedUntil: null, user: { __typename: 'User', id: OTHER, displayName: 'Meera Iyer', handle: 'meera' } }],
        joinRequests: pending ? [{ __typename: 'GroupJoinRequest', id: 'jr1', message: 'I study graphs', createdAt: '2026-10-12T10:00:00.000Z', user: { __typename: 'User', id: '01920000-0000-7000-8000-00000000cccc', displayName: 'Ravi Kumar', handle: 'ravi' } }] : [],
      },
    }),
    ReviewGroupJoinRequest: () => ((pending = false), { reviewGroupJoinRequest: { __typename: 'GroupPayload', group: { ...admin(), memberCount: 13 }, userErrors: [] } }),
  })
  await p.goto(`/groups/${GROUP}`)
  await p.getByRole('tab', { name: 'Requests' }).click()
  await expect(p.getByText('“I study graphs”')).toBeVisible()
  await p.getByRole('button', { name: 'Approve' }).click()
  await expect(p.getByText('No requests waiting.')).toBeVisible()
  expect(calls.find((c) => c.op === 'ReviewGroupJoinRequest')?.variables).toEqual({ requestId: 'jr1', decision: 'APPROVED' })
  // Admins cannot act on the owner, who ranks above them.
  await p.getByRole('tab', { name: 'Members' }).click()
  await expect(p.getByText('Meera Iyer')).toBeVisible()
  await expect(p.getByRole('button', { name: 'Remove' })).toHaveCount(0)
})

test('older posts are added below the newer ones, not swapped for them', async ({ page: p }) => {
  const second = (nodes: unknown[], hasNextPage: boolean) => ({ group: { __typename: 'Group', id: GROUP, posts: { __typename: 'GroupPostConnection', pinned: [], edges: nodes.map((node) => ({ __typename: 'GroupPostEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage, endCursor: hasNextPage ? 'c1' : null } } } })
  await mockApi(p, {
    Group: () => ({ group: group({ viewerRole: 'MEMBER', viewerCan: can({ post: true, leave: true }) }) }),
    GroupPosts: (v) => (v.after ? second([post('p2', 'Last week')], false) : second([post('p1', 'This week')], true)),
  })
  await p.goto(`/groups/${GROUP}`)
  await expect(p.getByText('This week')).toBeVisible()
  await p.getByRole('button', { name: 'Show older' }).click()
  await expect(p.getByText('Last week')).toBeVisible()
  await expect(p.getByText('This week')).toBeVisible()
  await expect(p.getByRole('button', { name: 'Show older' })).toHaveCount(0)
})
