import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * The Community page (lvn-backend ADR-0049, ADR-0076) against a mocked API: For You, Trending, the Following feed and
 * the activity of one's places; every part of a post card leads somewhere.
 */

const GROUP = '01920000-0000-7000-8000-0000000a0009'
const CLASS = '01920000-0000-7000-8000-0000000c0001'
const meera = { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Meera Iyer', handle: 'meera' }
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const page = (edges: unknown[], hasNextPage = false) => ({ edges, pageInfo: { __typename: 'PageInfo', hasNextPage, endCursor: hasNextPage ? 'c1' : null } })
const item = (key: string, kind: string, over: Record<string, unknown> = {}) => ({
  __typename: 'ActivityEdge',
  node: { __typename: 'ActivityItem', key, kind, at: new Date().toISOString(), actor: meera, group: null, classroom: null, post: null, announcement: null, doubt: null, note: null, repositoryEvent: null, ...over },
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
  // For You opens first (ADR-0076); the activity of one's places is its own tab.
  await p.getByRole('tab', { name: 'Your groups and classes' }).click()
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
  await p.getByRole('tab', { name: 'Your groups and classes' }).click()
  await expect(p.getByText('Nothing new in your groups and classes yet.', { exact: false })).toBeVisible()
  await p.getByRole('tab', { name: 'Following' }).click()
  await expect(p.getByRole('link', { name: /Why heaps matter/ })).toHaveAttribute('href', '/n/why-heaps-matter-01920000-0000-7000-8000-00000000a0b1')
  await expect(p.getByRole('link', { name: /Why heaps matter/ })).toContainText('Blog')
})

const TOPIC = { __typename: 'Topic', id: '01920000-0000-7000-8000-0000000070a1', title: 'Heaps' }
const NOTE = '01920000-0000-7000-8000-00000000a0c1'
const reactions = { __typename: 'Reactions', viewerReaction: null, counts: ['LIKE', 'HELPFUL', 'CELEBRATE'].map((kind) => ({ __typename: 'ReactionCount', kind, count: null, atLeast: false })) }
const post = (over: Record<string, unknown> = {}) => ({
  __typename: 'Note',
  id: NOTE,
  title: 'Heaps in ten minutes',
  slug: 'heaps-in-ten-minutes',
  kind: 'POST',
  visibility: 'PUBLIC',
  publishedAt: new Date().toISOString(),
  excerpt: 'A heap keeps the smallest item on top.',
  viewerSaved: false,
  owner: { ...meera, profile: { __typename: 'StudentProfile', department: 'CSE' } },
  topics: [{ ...TOPIC, __typename: 'Topic' }],
  previewPicture: null,
  discussion: { __typename: 'Discussion', commentCount: 3, reactions },
  ...over,
})
const forYou = (edges: unknown[], basedOn: unknown[] = [TOPIC]) => ({ forYouFeed: { __typename: 'CommunityConnection', edges, pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null }, basedOn } })

test('For You opens first: post cards on the person’s topics, every part leading somewhere, and Save', async ({ page: p }) => {
  const calls = await mockApi(p, {
    ForYouFeed: () => forYou([{ __typename: 'CommunityEdge', cursor: 'c', node: post(), topic: TOPIC }]),
    SaveNote: () => ({ saveNote: { __typename: 'NotePayload', note: { __typename: 'Note', id: NOTE, viewerSaved: true }, userErrors: [] } }),
  })
  await p.goto('/community')
  await expect(p.getByRole('tab', { name: 'For You' })).toHaveAttribute('aria-selected', 'true')
  const card = p.getByRole('article', { name: 'Heaps in ten minutes' })
  await expect(card.getByRole('link', { name: 'Heaps in ten minutes' })).toHaveAttribute('href', `/notes/${NOTE}`)
  await expect(card.getByRole('link', { name: 'Meera Iyer' })).toHaveAttribute('href', '/u/meera')
  await expect(card).toContainText('CSE')
  await expect(card.getByRole('link', { name: 'Heaps', exact: true })).toHaveAttribute('href', `/search?topic=${TOPIC.id}&topicTitle=Heaps`)
  await expect(card.getByRole('link', { name: '3 comments' })).toHaveAttribute('href', `/notes/${NOTE}?tab=discussions`)
  await expect(p.getByRole('link', { name: 'Change' })).toHaveAttribute('href', '/profile#interests')
  await card.getByRole('button', { name: 'Save', exact: true }).click()
  await expect(card.getByRole('button', { name: 'Saved', exact: true })).toBeVisible()
  expect(calls.find((c) => c.op === 'SaveNote')?.variables).toEqual({ noteId: NOTE })
})

test('with no topics, For You leads to choosing some or adding an exam; an empty Trending leads back to For You', async ({ page: p }) => {
  await mockApi(p, {
    ForYouFeed: () => forYou([], []),
    TrendingFeed: () => ({ trendingFeed: { __typename: 'CommunityConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null }, basedOn: [] } }),
  })
  await p.goto('/community')
  await expect(p.getByRole('link', { name: 'Choose topics' })).toHaveAttribute('href', '/profile#interests')
  await expect(p.getByRole('link', { name: 'Add an exam' })).toHaveAttribute('href', '/exams')
  await p.getByRole('tab', { name: 'Trending' }).click()
  await expect(p.getByText('Nothing is trending this week yet.')).toBeVisible()
  await p.getByRole('button', { name: 'See For You' }).click()
  await expect(p.getByRole('tab', { name: 'For You' })).toHaveAttribute('aria-selected', 'true')
})

test('Trending lists the week’s most discussed public notes as cards', async ({ page: p }) => {
  await mockApi(p, { ForYouFeed: () => forYou([]), TrendingFeed: () => ({ trendingFeed: { __typename: 'CommunityConnection', edges: [{ __typename: 'CommunityEdge', cursor: 'c', node: post({ title: 'Most talked about' }), topic: null }], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null }, basedOn: [] } }) })
  await p.goto('/community')
  await p.getByRole('tab', { name: 'Trending' }).click()
  await expect(p.getByRole('article', { name: 'Most talked about' }).getByRole('link', { name: 'Most talked about' })).toHaveAttribute('href', `/notes/${NOTE}`)
})

test('the topics a person follows are chosen on their account: added from a search, removed in one tap', async ({ page: p }) => {
  let chosen: unknown[] = []
  const calls = await mockApi(
    p,
    {
      MyInterests: () => ({ viewer: { __typename: 'User', id: '01920000-0000-7000-8000-00000000aaaa', profile: { __typename: 'StudentProfile', interests: chosen } } }),
      FindTopics: () => ({ findTopics: [{ __typename: 'Topic', id: TOPIC.id, title: 'Heaps', origin: 'CURATED', subject: { __typename: 'Subject', id: 's1', title: 'Data structures' } }] }),
      SetInterests: (v) => {
        chosen = (v.ids as string[]).map((id) => ({ __typename: 'Topic', id, title: 'Heaps', subject: { __typename: 'Subject', id: 's1', title: 'Data structures' } }))
        return { updateProfile: { __typename: 'ProfilePayload', profile: { __typename: 'StudentProfile', interests: chosen }, userErrors: [] } }
      },
    },
    // The account's own question reads the profile's other fields; the two share the cached profile.
    { profile: { __typename: 'StudentProfile', department: null, yearOfStudy: null, showOnProfile: false }, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } },
  )
  await p.goto('/profile#interests')
  const box = p.getByRole('region', { name: 'Topics you follow' })
  await expect(box.getByText('No topics chosen yet.')).toBeVisible()
  await box.getByLabel('Add a topic').fill('heap')
  await box.getByRole('button', { name: /Heaps/ }).click()
  await expect(box.getByRole('list', { name: 'Your topics' })).toContainText('Heaps')
  expect(calls.filter((c) => c.op === 'SetInterests').at(-1)?.variables).toEqual({ ids: [TOPIC.id] })
  await box.getByRole('button', { name: 'Remove Heaps' }).click()
  await expect(box.getByText('No topics chosen yet.')).toBeVisible()
  expect(calls.filter((c) => c.op === 'SetInterests').at(-1)?.variables).toEqual({ ids: [] })
})
