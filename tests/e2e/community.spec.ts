import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/** The Community page (lvn-backend ADR-0049) against a mocked API: the activity of one's places, and the Following feed. */

const GROUP = '01920000-0000-7000-8000-0000000a0009'
const CLASS = '01920000-0000-7000-8000-0000000c0001'
const meera = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Meera Iyer', handle: 'meera' }
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const page = (edges: unknown[], hasNextPage = false) => ({ edges, pageInfo: { __typename: 'PageInfo', hasNextPage, endCursor: hasNextPage ? 'c1' : null } })
const item = (key: string, kind: string, over: Record<string, unknown> = {}) => ({
  __typename: 'ActivityEdge',
  node: { __typename: 'ActivityItem', key, kind, at: new Date().toISOString(), actor: meera, group: null, classroom: null, post: null, announcement: null, doubt: null, note: null, ...over },
})
const group = { __typename: 'Group', id: GROUP, name: 'Heap team' }
const classroom = { __typename: 'Classroom', id: CLASS, name: 'DSA 101' }

test('the activity of your groups and classes, in words, page by page', async ({ page: p }) => {
  const calls = await mockApi(p, {
    ActivityFeed: (v) =>
      v.after
        ? { activityFeed: { __typename: 'ActivityConnection', ...page([item('k5', 'GROUP_POST', { group, post: { __typename: 'GroupPost', id: 'p1', body: doc('Standup at 5'), discussion: { __typename: 'Discussion', commentCount: 2 } } })]) } }
        : {
            activityFeed: {
              __typename: 'ActivityConnection',
              ...page(
                [
                  item('k1', 'SHARED_NOTE', { group, note: { __typename: 'Note', id: 'n1', title: 'Design doc' } }),
                  item('k2', 'CLASS_ANNOUNCEMENT', { classroom, announcement: { __typename: 'ClassroomPost', id: 'a1', body: doc('Quiz on Monday') } }),
                  item('k3', 'DOUBT', { group, doubt: { __typename: 'Doubt', id: 'd1', title: 'Which heap library?', status: 'OPEN' } }),
                  item('k4', 'SHARED_NOTE', { group, note: null }),
                ],
                true,
              ),
            },
          },
  })
  await p.goto('/community')
  const feed = p.getByRole('tabpanel')
  await expect(feed.getByRole('article')).toHaveCount(3)
  await expect(feed.getByRole('article').first()).toContainText('Meera Iyer shared a note with Heap team')
  await expect(feed.getByRole('link', { name: 'Design doc' })).toHaveAttribute('href', '/notes/n1')
  await expect(feed.getByRole('article').nth(1)).toContainText('Meera Iyer posted an announcement in DSA 101')
  await expect(feed.getByRole('link', { name: 'DSA 101' })).toHaveAttribute('href', `/classes/${CLASS}`)
  await expect(feed.getByRole('link', { name: 'Which heap library?' })).toHaveAttribute('href', `/groups/${GROUP}/doubts/d1`)
  await p.getByRole('button', { name: 'Show more' }).click()
  await expect(feed.getByRole('article')).toHaveCount(4)
  await expect(feed.getByText('2 comments')).toBeVisible()
  expect(calls.filter((c) => c.op === 'ActivityFeed').map((c) => c.variables)).toEqual([{}, { after: 'c1' }])
  await expect(p.getByRole('main').getByRole('link', { name: 'Groups' })).toHaveAttribute('href', '/groups')
  await expect(p.getByRole('link', { name: 'Classes' })).toHaveAttribute('href', '/classes')
})

test('the Following feed lists followed people’s public notes, linked to their public pages', async ({ page: p }) => {
  await mockApi(p, {
    ActivityFeed: () => ({ activityFeed: { __typename: 'ActivityConnection', ...page([]) } }),
    FollowingFeed: () => ({
      followingFeed: {
        __typename: 'NoteConnection',
        ...page([{ __typename: 'NoteEdge', node: { __typename: 'Note', id: '01920000-0000-7000-8000-00000000a0b1', title: 'Why heaps matter', slug: 'why-heaps-matter', kind: 'BLOG', publishedAt: new Date().toISOString(), owner: meera } }]),
      },
    }),
  })
  await p.goto('/community')
  await expect(p.getByText('Nothing new in your groups and classes yet.', { exact: false })).toBeVisible()
  await p.getByRole('tab', { name: 'Following' }).click()
  await expect(p.getByRole('link', { name: /Why heaps matter/ })).toHaveAttribute('href', '/n/why-heaps-matter-01920000-0000-7000-8000-00000000a0b1')
  await expect(p.getByRole('link', { name: /Why heaps matter/ })).toContainText('Blog')
})
