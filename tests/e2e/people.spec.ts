import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'
import { mockApi, USER } from './support/notes-api'
import { MEERA, profileRelation, RAVI, relation } from './support/people'

/**
 * People (lvn-backend ADR-0043): profiles rendered on the server from what people made public (the stand-in API in
 * tests/e2e/support), the viewer's buttons in the browser against a mocked API, and the viewer's own lists.
 */

const payload = (name: string, rel: unknown) => ({ [name]: { __typename: 'PersonPayload', user: { __typename: 'User', id: MEERA, relation: rel }, userErrors: [] } })

/** A visitor who is not signed in: the refresh is refused. */
async function signedOut(page: Page) {
  await page.route('**/graphql', (route) => route.fulfill({ json: { data: { refreshSession: { session: null, userErrors: [] } } } }))
}

test('a teacher’s profile is rendered for anyone, indexed, with what they made public', async ({ page }) => {
  await signedOut(page)
  await page.goto('/u/meera')
  await expect(page.getByRole('heading', { level: 1, name: /Meera Iyer/ })).toBeVisible()
  await expect(page.getByText('@meera', { exact: true })).toBeVisible()
  await expect(page.getByText('Teacher', { exact: true })).toBeVisible()
  await expect(page.getByText('1,000+ followers')).toBeVisible()
  await expect(page.getByRole('tab')).toHaveText(['Notes 2', 'Blog 0', 'Projects 0', 'Posts 0', 'Skills'])
  await expect(page.getByRole('link', { name: /Heaps, explained/ })).toHaveAttribute('href', '/n/heaps-explained-01920000-0000-7000-8000-00000000d0e1')
  await page.getByRole('tab', { name: /Blog/ }).click()
  await expect(page.getByText('No blog posts yet.')).toBeVisible()
  expect(await page.locator('meta[name="robots"]').getAttribute('content')).not.toContain('noindex')
  // Signed out, Follow leads to sign-in and back.
  await expect(page.getByRole('link', { name: 'Follow' })).toHaveAttribute('href', '/sign-in?next=%2Fu%2Fmeera')

  const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
  expect(violations.filter((v) => v.impact === 'critical' || v.impact === 'serious').map((v) => v.id)).toEqual([])
})

test('a student’s profile shows Notes and Projects only, with what they chose to share, and is not indexed', async ({ page }) => {
  await signedOut(page)
  await page.goto('/u/ravi')
  await expect(page.getByRole('heading', { level: 1, name: /Ravi Kumar/ })).toBeVisible()
  await expect(page.getByText('Computer Science · 3rd year')).toBeVisible()
  await expect(page.getByRole('tab')).toHaveText(['Notes 1', 'Projects 0'])
  expect(await page.locator('meta[name="robots"]').getAttribute('content')).toContain('noindex')
})

test('an id or another spelling moves to the handle; nobody is a 404', async ({ page }) => {
  await signedOut(page)
  await page.goto(`/u/${RAVI}`)
  await expect(page).toHaveURL(/\/u\/ravi$/)
  await page.goto('/u/MEERA')
  await expect(page).toHaveURL(/\/u\/meera$/)
  const res = await page.goto('/u/nobody-here')
  expect(res?.status()).toBe(404)
})

test('a signed-in viewer follows, then blocks after reading what it does', async ({ page }) => {
  let rel = relation()
  const calls = await mockApi(page, {
    ProfileRelation: () => profileRelation(rel),
    FollowUser: () => ((rel = relation({ following: true }, { follow: false, unfollow: true })), payload('followUser', rel)),
    BlockUser: () => ((rel = relation({ blocked: true }, { follow: false, block: false, unblock: true, restrict: false })), payload('blockUser', rel)),
  })
  await page.goto('/u/meera')
  await page.getByRole('button', { name: 'Follow' }).click()
  await expect(page.getByRole('button', { name: 'Following — select to unfollow' })).toBeVisible()
  expect(calls.find((c) => c.op === 'FollowUser')?.variables).toEqual({ input: { userId: MEERA } })

  await page.getByRole('button', { name: 'More options' }).click()
  await page.getByRole('menuitem', { name: 'Block' }).click()
  const dialog = page.getByRole('dialog', { name: 'Block this person?' })
  await expect(dialog.getByText('They are not told. You can unblock them any time.')).toBeVisible()
  await dialog.getByRole('button', { name: 'Block' }).click()
  await expect(page.getByRole('button', { name: 'Unblock' })).toBeVisible()
  expect(calls.some((c) => c.op === 'BlockUser')).toBe(true)
})

test('a refusal is shown in the API’s words', async ({ page }) => {
  await mockApi(page, { ProfileRelation: () => profileRelation(relation({ followedBy: true }, { removeFollower: true })) })
  await page.route('**/graphql', async (route, request) => {
    const body = request.postDataJSON() as { operationName?: string }
    if (body.operationName === 'FollowUser') return route.fulfill({ json: { data: null, errors: [{ message: 'Verify your account to follow people.', extensions: { code: 'FORBIDDEN' } }] } })
    return route.fallback()
  })
  await page.goto('/u/meera')
  await expect(page.getByText('Follows you')).toBeVisible()
  await page.getByRole('button', { name: 'Follow' }).click()
  await expect(page.getByRole('main').getByRole('alert')).toHaveText('Verify your account to follow people.')
})

test('on one’s own profile: exact counts and the way to edit it', async ({ page }) => {
  await mockApi(page, { ProfileRelation: () => profileRelation(null, MEERA) })
  await page.goto('/u/meera')
  await expect(page.getByRole('link', { name: '12 followers · 3 following' })).toHaveAttribute('href', '/profile/people')
  await expect(page.getByRole('link', { name: 'Edit your profile' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Follow' })).toHaveCount(0)
})

test('your people: followers (young learners counted, not named), following, blocked; each undone in one step', async ({ page }) => {
  const person = (id: string, name: string, handle: string) => ({ __typename: 'User', id, displayName: name, handle, globalRole: 'STUDENT', verified: true })
  let followers = [person(RAVI, 'Ravi Kumar', 'ravi')]
  const edge = (node: unknown) => ({ __typename: 'PersonEdge', since: '2026-10-10T10:00:00.000Z', node })
  const calls = await mockApi(page, {
    MyPeople: () => ({
      viewer: { __typename: 'User', id: USER, handle: 'asharao', globalRole: 'STUDENT', followerCount: followers.length + 1, followingCount: 1 },
      myConnections: [],
      myConnectionRequests: [],
      myFollowers: { __typename: 'PersonConnection', edges: followers.map(edge), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } },
      myFollowing: { __typename: 'PersonConnection', edges: [edge(person(MEERA, 'Meera Iyer', 'meera'))], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } },
      myBlocked: [],
      myRestricted: [],
    }),
    RemoveFollower: () => ((followers = []), { removeFollower: { __typename: 'PersonPayload', user: null, userErrors: [] } }),
  })
  await page.goto('/profile/people')
  await expect(page.getByRole('tab', { name: 'Followers 2' })).toBeVisible()
  await expect(page.getByRole('link', { name: /Ravi Kumar/ })).toHaveAttribute('href', '/u/ravi')
  await expect(page.getByText('1 more follower is not shown by name: young learners never appear in lists.')).toBeVisible()
  await page.getByRole('button', { name: 'Remove' }).click()
  await expect(page.getByRole('tab', { name: 'Followers 1' })).toBeVisible()
  expect(calls.find((c) => c.op === 'RemoveFollower')?.variables).toEqual({ input: { userId: RAVI } })
  await page.getByRole('tab', { name: /Following/ }).click()
  await expect(page.getByRole('button', { name: 'Unfollow' })).toBeVisible()
  await page.getByRole('tab', { name: /Blocked/ }).click()
  await expect(page.getByText("You haven't blocked anyone.")).toBeVisible()
})

test('search finds people and links to their profiles', async ({ page }) => {
  await mockApi(page, {
    Search: () => ({ search: { __typename: 'SearchResults', notes: [], notesCursor: null, groups: [], classrooms: [], topics: [], people: [{ __typename: 'User', id: MEERA, handle: 'meera', displayName: 'Meera Iyer', globalRole: 'TEACHER' }] } }),
  })
  await page.goto('/search?q=meera')
  const link = page.getByRole('link', { name: /Meera Iyer/ })
  await expect(link).toHaveAttribute('href', '/u/meera')
  await expect(link).toContainText('Teacher')
})

test('Ctrl+K finds a person; Enter opens their profile', async ({ page }) => {
  await mockApi(page, {
    Search: () => ({ search: { __typename: 'SearchResults', notes: [], notesCursor: null, groups: [], classrooms: [], topics: [], people: [{ __typename: 'User', id: MEERA, handle: 'meera', displayName: 'Meera Iyer', globalRole: 'TEACHER' }] } }),
  })
  await page.goto('/notes')
  // The palette listens once the signed-in app is up; the bell shows when it is.
  await expect(page.getByRole('link', { name: 'Notifications', exact: true })).toBeVisible()
  await page.keyboard.press('Control+k')
  const palette = page.getByRole('dialog', { name: 'Search notes, people, groups and topics' })
  await palette.getByRole('combobox').fill('meera')
  await expect(palette.getByRole('option', { name: /Meera Iyer @meera/ })).toBeVisible()
  await page.keyboard.press('Enter')
  await expect(page).toHaveURL(/\/u\/meera$/)
})

test('a signed-in viewer reports a person from the menu (ADR-0051)', async ({ page }) => {
  const calls = await mockApi(page, {
    ProfileRelation: () => profileRelation(relation()),
    ReportContent: () => ({ reportContent: { __typename: 'OkPayload', ok: true, userErrors: [] } }),
  })
  await page.goto('/u/meera')
  await page.getByRole('button', { name: 'More options' }).click()
  await page.getByRole('menuitem', { name: 'Report' }).click()
  const dialog = page.getByRole('dialog', { name: 'Report this person' })
  await dialog.getByText('Bullying or harassment').click()
  await dialog.getByLabel('Anything moderators should know (optional)').fill('Messages me every day')
  await dialog.getByRole('button', { name: 'Send report' }).click()
  await expect(dialog.getByText('Thank you for telling us')).toBeVisible()
  expect(calls.find((c) => c.op === 'ReportContent')?.variables).toEqual({ input: { entityType: 'USER', entityId: MEERA, reason: 'HARASSMENT', details: 'Messages me every day' } })
})
