import { expect, test } from '@playwright/test'
import { mockApi, NOTE_ID, USER } from './support/notes-api'

/** Groups (lvn-backend ADR-0045) against a mocked API: finding and starting one, asking to join, posts, notes, members. */

const GROUP = '01920000-0000-7000-8000-0000000a0001'
const OTHER = '01920000-0000-7000-8000-00000000bbbb'
const can = (over: Record<string, boolean> = {}) => ({ __typename: 'GroupActions', join: false, requestJoin: false, post: false, moderate: false, manage: false, delete: false, reviewRequests: false, leave: false, askDoubt: false, inviteMentor: false, acceptMentorInvite: false, ...over })
const group = (over: Record<string, unknown> = {}) => ({
  __typename: 'Group', id: GROUP, type: 'COMMUNITY', name: 'Algorithms study', description: 'Weekly problems and solutions', privacy: 'PUBLIC', joinPolicy: 'APPROVAL', memberCount: 12, viewerRole: null, createdAt: '2026-10-01T10:00:00.000Z', viewerRequestId: null, viewerMentorInviteId: null, moderationWarning: null,
  owner: { __typename: 'User', id: OTHER, displayName: 'Meera Iyer' }, viewerCan: can(), ...over,
})
const card = (id: string, name: string, viewerRole: string | null = null) => ({ __typename: 'Group', id, type: 'COMMUNITY', name, description: null, privacy: 'PUBLIC', joinPolicy: 'OPEN', memberCount: 3, viewerRole })
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const post = (id: string, text: string, over: Record<string, unknown> = {}) => ({ __typename: 'GroupPost', id, kind: 'POST', moderation: 'OK', moderationReason: null, moderationCanAppeal: false, body: doc(text), pinned: false, createdAt: new Date().toISOString(), editedAt: null, author: { __typename: 'User', id: OTHER, displayName: 'Meera Iyer', handle: 'meera' }, viewerCan: { __typename: 'GroupPostActions', edit: false, delete: false, pin: false }, discussion: { __typename: 'Discussion', commentCount: 0 }, ...over })
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
  await expect(p.getByRole('button', { name: 'New post' })).toHaveCount(0)
  await p.getByRole('button', { name: 'Ask to join' }).click()
  await p.getByLabel('A note for the admins (optional)').fill('I study graphs')
  await p.getByRole('button', { name: 'Send request' }).click()
  await expect(p.getByText('Your request is waiting for an answer.')).toBeVisible()
  expect(calls.find((c) => c.op === 'RequestToJoinGroup')?.variables).toEqual({ groupId: GROUP, message: 'I study graphs' })
})

test('members post from the floating ＋, pinned posts come first, and moderators can pin and delete', async ({ page: p }) => {
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
  // A new post starts from the floating ＋.
  await p.getByRole('button', { name: 'New post' }).click()
  const writing = p.getByRole('dialog', { name: 'New post' })
  await writing.getByLabel('Write a post').fill('Hello all\nSee you Friday')
  await writing.getByRole('button', { name: 'Post', exact: true }).click()
  await expect(writing).toBeHidden()
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

test('the owner hands the group over after confirming; a mentor has no role to change (ADR-0048)', async ({ page: p }) => {
  const member = (id: string, displayName: string, role: string) => ({ __typename: 'GroupMember', role, joinedAt: '2026-10-01T10:00:00.000Z', mutedUntil: null, user: { __typename: 'User', id, displayName, handle: displayName.split(' ')[0]!.toLowerCase() } })
  let roles: Record<string, string> = { [USER]: 'OWNER', u2: 'MEMBER', t1: 'MENTOR' }
  const owner = () => group({ viewerRole: roles[USER], viewerCan: can({ post: true, moderate: true, manage: true, delete: roles[USER] === 'OWNER', reviewRequests: true, leave: roles[USER] !== 'OWNER' }) })
  const calls = await mockApi(p, {
    Group: () => ({ group: owner() }),
    GroupPosts: () => page([], []),
    GroupMembers: () => ({ group: { __typename: 'Group', id: GROUP, viewerRole: roles[USER], members: [member(USER, 'Asha Rao', roles[USER]!), member('u2', 'Ravi Kumar', roles.u2!), member('t1', 'Meera Iyer', roles.t1!)], joinRequests: [] } }),
    SetGroupRole: (v) => {
      if (v.role === 'OWNER') roles = { ...roles, [USER]: 'ADMIN', [String(v.userId)]: 'OWNER' }
      return { setGroupRole: { __typename: 'GroupPayload', group: owner(), userErrors: [] } }
    },
  })
  await p.goto(`/groups/${GROUP}`)
  await p.getByRole('tab', { name: 'Members' }).click()
  await expect(p.getByText('Meera Iyer')).toBeVisible()
  await expect(p.getByRole('combobox', { name: 'Role of Meera Iyer' })).toHaveCount(0)
  await expect(p.getByRole('button', { name: 'Remove' })).toHaveCount(2)
  const ravi = p.getByRole('combobox', { name: 'Role of Ravi Kumar' })
  // Declining the confirmation changes nothing.
  p.once('dialog', (d) => void d.dismiss())
  await ravi.selectOption({ label: 'Hand the group to Ravi Kumar' })
  expect(calls.filter((c) => c.op === 'SetGroupRole')).toHaveLength(0)
  p.once('dialog', (d) => {
    expect(d.message()).toBe("Hand the group to Ravi Kumar? You'll stay on as an admin.")
    void d.accept()
  })
  await ravi.selectOption({ label: 'Hand the group to Ravi Kumar' })
  await expect(p.getByText('Admin', { exact: true }).first()).toBeVisible()
  expect(calls.find((c) => c.op === 'SetGroupRole')?.variables).toEqual({ groupId: GROUP, userId: 'u2', role: 'OWNER' })
  // Now an admin, the hand-over is no longer offered.
  await expect(p.getByRole('option', { name: /Hand the group/ })).toHaveCount(0)
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

test('a member reports someone else’s post, and sees why their own was hidden, with one appeal (ADR-0051)', async ({ page: p }) => {
  let appealed = false
  const mine = post('p9', 'My hot take', { author: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' }, moderation: 'HIDDEN', moderationReason: 'Be kind to the others.', moderationCanAppeal: true })
  const calls = await mockApi(p, {
    Group: () => ({ group: group({ viewerRole: 'MEMBER', viewerCan: can({ post: true, leave: true }) }) }),
    GroupPosts: () => page([], [post('p2', 'You are all hopeless'), appealed ? { ...mine, moderationCanAppeal: false } : mine]),
    ReportContent: () => ({ reportContent: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
    AppealModeration: () => ((appealed = true), { appealModeration: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await p.goto(`/groups/${GROUP}`)
  await expect(p.getByRole('tab', { name: 'Reports' })).toHaveCount(0)
  const items = p.getByRole('tabpanel').getByRole('listitem')
  await expect(items).toHaveCount(2)
  // Only other people's posts can be reported.
  await expect(items.nth(1).getByRole('button', { name: 'Report' })).toHaveCount(0)
  await items.first().getByRole('button', { name: 'Report' }).click()
  const dialog = p.getByRole('dialog', { name: 'Report this post' })
  await dialog.getByText('Bullying or harassment').click()
  await dialog.getByRole('button', { name: 'Send report' }).click()
  await expect(dialog.getByText('Thank you for telling us')).toBeVisible()
  expect(calls.find((c) => c.op === 'ReportContent')?.variables).toEqual({ input: { entityType: 'GROUP_POST', entityId: 'p2', reason: 'HARASSMENT', details: null } })
  await dialog.getByRole('button', { name: 'Done' }).click()

  const own = items.nth(1)
  await expect(own.getByText('Hidden by moderators')).toBeVisible()
  await expect(own.getByText('Be kind to the others.')).toBeVisible()
  await expect(own.getByText('Only you can see it now.')).toBeVisible()
  await own.getByRole('button', { name: 'Appeal' }).click()
  const appeal = p.getByRole('dialog', { name: 'Appeal this decision' })
  await expect(appeal.getByText('Tell the moderators why it should come back. You can appeal once.')).toBeVisible()
  await appeal.getByLabel('Your message').fill('It was a joke among friends.')
  await appeal.getByRole('button', { name: 'Send appeal' }).click()
  await expect(own.getByText('Your appeal is with the moderators.')).toBeVisible()
  await expect(own.getByRole('button', { name: 'Appeal' })).toHaveCount(0)
  expect(calls.find((c) => c.op === 'AppealModeration')?.variables).toEqual({ input: { entityType: 'GROUP_POST', entityId: 'p9', message: 'It was a joke among friends.' } })
})

test('group moderators work through the group’s reports: open it, mute the author, hide with a reason (ADR-0051)', async ({ page: p }) => {
  let open = true
  const item = {
    __typename: 'ModerationCase', resource: null, suspendedUntil: null, removedGroup: null, entityType: 'GROUP_POST', entityId: 'p2', scope: 'GROUP', scopeId: GROUP, openedAt: new Date(Date.now() - 3_600_000).toISOString(), note: null, user: null, group: null, appeal: null,
    content: { __typename: 'ModeratedContent', entityType: 'GROUP_POST', id: 'p2', excerpt: 'You are all hopeless at heaps.', moderation: 'OK', moderationReason: null, deleted: false, path: `/groups/${GROUP}`, author: { __typename: 'User', id: OTHER, displayName: 'Meera Iyer', handle: 'meera' } },
    reports: [{ __typename: 'ModerationReport', reason: 'HARASSMENT', details: 'Rude to everyone', createdAt: new Date().toISOString(), reporter: { __typename: 'User', id: USER, displayName: 'Asha Rao' } }],
  }
  const calls = await mockApi(p, {
    Group: () => ({ group: group({ viewerRole: 'MODERATOR', viewerCan: can({ post: true, moderate: true, leave: true }) }) }),
    GroupPosts: () => page([], []),
    ModerationQueue: () => ({ moderationQueue: { __typename: 'ModerationCaseConnection', edges: open ? [{ __typename: 'ModerationCaseEdge', cursor: 'c1', node: item }] : [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
    MuteGroupMember: () => ({ muteGroupMember: { __typename: 'GroupPayload', group: { __typename: 'Group', id: GROUP }, userErrors: [] } }),
    ModerateContent: () => ((open = false), { moderateContent: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await p.goto(`/groups/${GROUP}`)
  await p.getByRole('tab', { name: 'Reports' }).click()
  await expect(p.getByText(/Only the group’s moderators see them/)).toBeVisible()
  expect(calls.find((c) => c.op === 'ModerationQueue')?.variables).toMatchObject({ scope: { scope: 'GROUP', id: GROUP } })
  const card = p.getByRole('article', { name: 'Post' })
  await expect(card.getByText('by Meera Iyer (@meera)')).toBeVisible()
  await expect(card.getByText('You are all hopeless at heaps.')).toBeVisible()
  await expect(card.getByText('Rude to everyone')).toBeVisible()
  await expect(card.getByRole('link', { name: 'Open where it is' })).toHaveAttribute('href', `/groups/${GROUP}`)
  // Approving a post that is up would change nothing; dismissing does that.
  await expect(card.getByRole('button', { name: 'Approve' })).toHaveCount(0)
  await card.getByRole('button', { name: 'Mute the author for a day' }).click()
  await expect(card.getByRole('button', { name: 'Muted for a day' })).toBeDisabled()
  expect(calls.find((c) => c.op === 'MuteGroupMember')?.variables).toMatchObject({ groupId: GROUP, userId: OTHER })
  await card.getByRole('button', { name: 'Hide' }).click()
  await expect(card.getByRole('alert')).toHaveText('Write a reason first: the author is told.')
  await card.getByLabel(/^Reason/).fill('Be kind to the others.')
  await card.getByRole('button', { name: 'Hide' }).click()
  await expect(p.getByText('Nothing to review. Thank you!')).toBeVisible()
  expect(calls.find((c) => c.op === 'ModerateContent')?.variables).toEqual({ input: { entityType: 'GROUP_POST', entityId: 'p2', action: 'HIDE', reason: 'Be kind to the others.' } })
})

test('the owner reads the platform moderators’ warning on the group; others can report the group (ADR-0051)', async ({ page: p }) => {
  let owner = true
  const calls = await mockApi(p, {
    Group: () => ({ group: owner ? group({ viewerRole: 'OWNER', moderationWarning: 'Rename the group, please.', owner: { __typename: 'User', id: USER, displayName: 'Asha Rao' }, viewerCan: can({ post: true, moderate: true, manage: true, delete: true }) }) : group({ viewerRole: 'MEMBER', viewerCan: can({ post: true, leave: true }) }) }),
    GroupPosts: () => page([], []),
    ReportContent: () => ({ reportContent: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await p.goto(`/groups/${GROUP}`)
  const header = p.getByRole('banner').filter({ hasText: 'Algorithms study' })
  await expect(p.getByText('A warning from the moderators')).toBeVisible()
  await expect(p.getByText('Rename the group, please.')).toBeVisible()
  await expect(header.getByRole('button', { name: 'Report' })).toHaveCount(0)

  owner = false
  await p.reload()
  await expect(p.getByText('A warning from the moderators')).toHaveCount(0)
  await p.getByRole('button', { name: 'Report' }).click()
  const dialog = p.getByRole('dialog', { name: 'Report this group' })
  await dialog.getByText('Hate', { exact: true }).click()
  await dialog.getByLabel('Anything moderators should know (optional)').fill('The group name')
  await dialog.getByRole('button', { name: 'Send report' }).click()
  await expect(dialog.getByText('Thank you for telling us')).toBeVisible()
  expect(calls.find((c) => c.op === 'ReportContent')?.variables).toEqual({ input: { entityType: 'GROUP', entityId: GROUP, reason: 'HATE', details: 'The group name' } })
})
