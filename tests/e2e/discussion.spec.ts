import { expect, test } from '@playwright/test'
import { cards, meta, mockApi, NOTE_ID, page1, USER } from './support/notes-api'

/** Comments and reactions (lvn-backend ADR-0047) against a mocked API: on a note, as its owner, on posts, on public pages. */

const OTHER = '01920000-0000-7000-8000-00000000bbbb'
const ravi = { __typename: 'User', id: OTHER, displayName: 'Ravi Kumar', handle: 'ravi' }
const asha = { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' }
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const reactions = (over: Record<string, number | null> = {}, viewerReaction: string | null = null) => ({
  __typename: 'Reactions',
  viewerReaction,
  counts: ['LIKE', 'HELPFUL', 'CELEBRATE'].map((kind) => ({ __typename: 'ReactionCount', kind, count: over[kind] ?? 0, atLeast: false })),
})
const can = (over: Record<string, boolean> = {}) => ({ __typename: 'CommentActions', reply: true, edit: false, delete: false, approve: false, ...over })
type MockComment = Record<string, unknown> & { id: string; replies: MockComment[] }
const comment = (id: string, text: string, over: Record<string, unknown> = {}): MockComment => ({
  __typename: 'Comment', id, body: doc(text), moderation: 'OK', moderationReason: null, moderationCanAppeal: false, cardId: null, removed: false, pendingApproval: false, private: false, createdAt: new Date().toISOString(), editedAt: null, author: ravi, reactions: reactions(), viewerCan: can(), replies: [], ...over,
})
const discussion = (list: unknown[], over: Record<string, unknown> = {}) => ({
  discussion: { __typename: 'Discussion', commentCount: list.length, viewerCanComment: true, whyNot: null, reactions: reactions(), comments: { __typename: 'CommentConnection', edges: list.map((node) => ({ __typename: 'CommentEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } }, ...over },
})
const asReader = () => ({ note: { ...meta({ viewerAccess: 'READER', owner: ravi, visibility: 'PUBLIC', publishedAt: new Date().toISOString(), viewerCan: { __typename: 'NotePermissions', edit: false, publish: false, changeVisibility: false, delete: false, share: false, fork: true } }), cards: page1(cards) } })
const target = { type: 'NOTE', id: NOTE_ID }

test('a reader of a note reacts, comments and replies', async ({ page }) => {
  let list: ReturnType<typeof comment>[] = [comment('c1', 'Why halve it?')]
  let mine: string | null = null
  const calls = await mockApi(page, {
    NoteToEdit: asReader,
    Discussion: () => ({ ...discussion(list), discussion: { ...discussion(list).discussion, reactions: reactions({ HELPFUL: mine ? 1 : 0 }, mine) } }),
    React: (v) => ((mine = (v.kind as string | null) ?? null), { react: { __typename: 'ReactPayload', reactions: reactions({}, mine), userErrors: [] } }),
    AddComment: (v) => {
      const input = v.input as { parentId?: string; body: unknown }
      const made = comment(`c${list.length + 2}`, (input.body as ReturnType<typeof doc>).content[0]!.content[0]!.text, { author: asha, viewerCan: can({ edit: true, delete: true, reply: !input.parentId }) })
      list = input.parentId ? list.map((c) => (c.id === input.parentId ? { ...c, replies: [...c.replies, made] } : c)) : [...list, made]
      return { addComment: { __typename: 'CommentPayload', comment: { __typename: 'Comment', id: made.id }, userErrors: [] } }
    },
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const thread = page.getByRole('region', { name: 'Discussion' })
  await expect(thread).toContainText('Why halve it?')
  await expect(thread.getByRole('heading')).toContainText('1 comment')
  await thread.getByRole('button', { name: 'Helpful' }).first().click()
  await expect(thread.getByRole('button', { name: 'Helpful' }).first()).toHaveAttribute('aria-pressed', 'true')
  expect(calls.find((c) => c.op === 'React')?.variables).toEqual({ target, kind: 'HELPFUL' })

  await thread.getByLabel('Write a comment').fill('Each step drops half')
  await thread.getByRole('button', { name: 'Comment', exact: true }).click()
  await expect(thread).toContainText('Each step drops half')
  expect(calls.find((c) => c.op === 'AddComment')?.variables).toEqual({ input: { target, body: doc('Each step drops half') } })

  await thread.getByRole('button', { name: 'Reply', exact: true }).first().click()
  const replyForm = thread.locator('form').filter({ has: page.getByLabel('Write a reply') })
  await replyForm.getByLabel('Write a reply').fill('So log n steps')
  await replyForm.getByRole('button', { name: 'Reply', exact: true }).click()
  await expect(thread).toContainText('So log n steps')
  expect(calls.filter((c) => c.op === 'AddComment')[1]?.variables).toEqual({ input: { target, parentId: 'c1', body: doc('So log n steps') } })
})

test('the owner approves a restricted person’s comment and removes another', async ({ page }) => {
  let list = [comment('c1', 'Pick me', { pendingApproval: true, viewerCan: can({ approve: true, delete: true }) }), comment('c2', 'Spam here', { viewerCan: can({ delete: true }) })]
  const calls = await mockApi(page, {
    NoteToEdit: () => ({ note: { ...meta({ visibility: 'PUBLIC', publishedAt: new Date().toISOString(), publishedVersion: { __typename: 'NoteVersion', id: 'v1', number: 1, createdAt: new Date().toISOString() } }), cards: page1(cards) } }),
    Discussion: () => discussion(list),
    ApproveComment: () => ((list = list.map((c) => (c.id === 'c1' ? { ...c, pendingApproval: false, viewerCan: can({ delete: true }) } : c))), { approveComment: { __typename: 'CommentPayload', comment: { __typename: 'Comment', id: 'c1' }, userErrors: [] } }),
    DeleteComment: () => ((list = list.filter((c) => c.id !== 'c2')), { deleteComment: { __typename: 'CommentPayload', comment: { __typename: 'Comment', id: 'c2' }, userErrors: [] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const thread = page.getByRole('region', { name: 'Discussion' })
  await expect(thread.getByText('Waiting for approval')).toBeVisible()
  await thread.getByRole('button', { name: 'Approve' }).click()
  await expect(thread.getByText('Waiting for approval')).toHaveCount(0)
  page.once('dialog', (d) => void d.accept())
  await thread.getByRole('button', { name: 'Delete' }).last().click()
  await expect(thread).not.toContainText('Spam here')
  expect(calls.find((c) => c.op === 'DeleteComment')?.variables).toEqual({ commentId: 'c2' })
})

test('someone who may not comment is told why, with no box to write in', async ({ page }) => {
  await mockApi(page, { NoteToEdit: asReader, Discussion: () => discussion([comment('c1', 'Removed later', { removed: true, author: null, body: null })], { viewerCanComment: false, whyNot: 'Verify your account to comment.' }) })
  await page.goto(`/notes/${NOTE_ID}`)
  const thread = page.getByRole('region', { name: 'Discussion' })
  await expect(thread.getByText('Verify your account to comment.')).toBeVisible()
  await expect(thread.getByText('This comment was removed.')).toBeVisible()
  await expect(thread.getByLabel('Write a comment')).toHaveCount(0)
  await expect(thread.getByRole('button', { name: 'Like' })).toBeDisabled()
})

test('a class announcement’s comments are a private thread with the staff', async ({ page }) => {
  const CLASS = '01920000-0000-7000-8000-0000000c0001'
  const teacher = { __typename: 'User', id: OTHER, displayName: 'Meera Iyer' }
  const calls = await mockApi(page, {
    Classroom: () => ({ classroom: { __typename: 'Classroom', id: CLASS, name: 'Physics 9A', description: null, memberCount: 31, viewerRole: 'STUDENT', teacher, createdAt: '2026-10-01T10:00:00.000Z', joinCode: null, viewerRequestId: null, viewerInviteId: null, viewerCan: { __typename: 'ClassroomActions', requestJoin: false, acceptInvite: false, review: false, post: false, manage: false, leave: true } } }),
    ClassroomPosts: () => ({ classroom: { __typename: 'Classroom', id: CLASS, posts: { __typename: 'ClassroomPostConnection', edges: [{ __typename: 'ClassroomPostEdge', node: { __typename: 'ClassroomPost', id: 'p1', moderation: 'OK', moderationReason: null, moderationCanAppeal: false, body: doc('Test on Friday'), createdAt: new Date().toISOString(), viewerCanDelete: false, author: { ...teacher, handle: 'meera' }, discussion: { __typename: 'Discussion', commentCount: 1 } } }], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
    Discussion: () => discussion([comment('c1', 'Which chapters?', { author: asha, private: true })]),
  })
  await page.goto(`/classes/${CLASS}`)
  await page.getByRole('button', { name: '1 comment' }).click()
  await expect(page.getByText('Private thread')).toBeVisible()
  await expect(page.getByLabel('Write a comment')).toHaveAttribute('placeholder', "Ask the teacher a question. Only you and the class's staff see it.")
  expect(calls.find((c) => c.op === 'Discussion')?.variables).toEqual({ target: { type: 'CLASSROOM_POST', id: 'p1' } })
})

test('the author of a held or hidden comment is told why, appeals once; others’ comments can be reported (ADR-0051)', async ({ page }) => {
  const held = comment('c2', 'Buy followers here', { author: asha, moderation: 'PENDING_REVIEW', moderationReason: 'A moderator will look at this before others see it: it contains words linked to spam.', viewerCan: can({ edit: true, delete: true }) })
  const hidden = comment('c3', 'You are wrong and so is everyone', { author: asha, moderation: 'HIDDEN', moderationReason: 'Disagree with the note, not the person.', moderationCanAppeal: true, viewerCan: can({ delete: true }) })
  const calls = await mockApi(page, {
    NoteToEdit: asReader,
    Discussion: () => discussion([comment('c1', 'Why halve it?'), held, hidden]),
    ReportContent: () => ({ reportContent: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
    AppealModeration: () => ({ appealModeration: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await page.goto(`/notes/${NOTE_ID}`)
  const thread = page.getByRole('region', { name: 'Discussion' })
  const items = thread.getByRole('article')
  await expect(items).toHaveCount(3)
  await expect(items.nth(1).getByText('Waiting for a moderator')).toBeVisible()
  await expect(items.nth(1).getByText(/it contains words linked to spam/)).toBeVisible()
  await expect(items.nth(1).getByText('Until then, only you can see it.')).toBeVisible()
  await expect(items.nth(1).getByRole('button', { name: 'Appeal' })).toHaveCount(0)
  await expect(items.nth(1).getByRole('button', { name: 'Report' })).toHaveCount(0)

  await items.nth(2).getByRole('button', { name: 'Appeal' }).click()
  const appeal = page.getByRole('dialog', { name: 'Appeal this decision' })
  await appeal.getByLabel('Your message').fill('I meant the argument, not the people.')
  await appeal.getByRole('button', { name: 'Send appeal' }).click()
  await expect(items.nth(2).getByText('Your appeal is with the moderators.')).toBeVisible()
  expect(calls.find((c) => c.op === 'AppealModeration')?.variables).toEqual({ input: { entityType: 'COMMENT', entityId: 'c3', message: 'I meant the argument, not the people.' } })

  await items.first().getByRole('button', { name: 'Report' }).click()
  const dialog = page.getByRole('dialog', { name: 'Report this comment' })
  await expect(dialog.getByLabel('Anything moderators should know (optional)')).toHaveAttribute('placeholder', 'What is wrong, in a few words')
  await dialog.getByText('Spam or advertising').click()
  await dialog.getByRole('button', { name: 'Send report' }).click()
  await expect(dialog.getByText('Thank you for telling us')).toBeVisible()
  expect(calls.find((c) => c.op === 'ReportContent')?.variables).toEqual({ input: { entityType: 'COMMENT', entityId: 'c1', reason: 'SPAM', details: null } })
})

test('@handle in a comment links to the person; an email address does not (lvn-backend ADR-0054)', async ({ page }) => {
  await mockApi(page, { NoteToEdit: asReader, Discussion: () => discussion([comment('c1', 'Thanks @asharao! Mail me at ravi@example.com')]) })
  await page.goto(`/notes/${NOTE_ID}`)
  const thread = page.getByRole('region', { name: 'Discussion' })
  await expect(thread.getByRole('link', { name: '@asharao' })).toHaveAttribute('href', '/u/asharao')
  await expect(thread.getByText(/Mail me at ravi@example\.com/)).toBeVisible()
  await expect(thread.getByRole('link', { name: /example\.com/ })).toHaveCount(0)
  await expect(thread.getByText('Type @ and someone’s handle to mention them.')).toBeVisible()
})
