import { expect, test, type Page } from '@playwright/test'
import { mockApi, NOTE_ID, USER } from './support/notes-api'
import { MEERA, profileRelation, relation } from './support/people'

/**
 * Teachers (lvn-backend ADR-0012, ADR-0013, ADR-0014, ADR-0044): connections, the Skills tab and its editor, sharing
 * with all connections, and starting blogs and posts.
 */

const payload = (name: string, rel: unknown) => ({ [name]: { __typename: 'PersonPayload', user: { __typename: 'User', id: MEERA, relation: rel }, userErrors: [] } })

async function signedOut(page: Page) {
  await page.route('**/graphql', (route) => route.fulfill({ json: { data: { refreshSession: { session: null, userErrors: [] } } } }))
}

test('a teacher’s Skills tab: headline, about, and items grouped', async ({ page }) => {
  await signedOut(page)
  await page.goto('/u/meera')
  await expect(page.getByRole('tab')).toHaveText(['Notes 2', 'Blog 0', 'Projects 0', 'Posts 0', 'Skills'])
  await page.getByRole('tab', { name: 'Skills' }).click()
  await expect(page.getByText('Teaches algorithms to second-year students')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Qualifications' })).toBeVisible()
  await expect(page.getByText('IIT Madras, 2014')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Skills', exact: true })).toBeVisible()
  await expect(page.getByText('Graph algorithms')).toBeVisible()
})

test('a teacher asks another to connect, and withdraws; an incoming request is accepted', async ({ page }) => {
  let rel = relation({}, { requestConnection: true })
  const calls = await mockApi(page, {
    ProfileRelation: () => profileRelation(rel),
    RequestConnection: () => ((rel = relation({ pendingConnection: { __typename: 'PendingConnection', direction: 'OUTGOING', requestId: 'r1' } })), payload('requestConnection', rel)),
    WithdrawConnectionRequest: () => ((rel = relation({}, { requestConnection: true })), payload('withdrawConnectionRequest', rel)),
  })
  await page.goto('/u/meera')
  await page.getByRole('button', { name: 'Connect' }).click()
  await page.getByRole('button', { name: 'Connection requested — select to withdraw' }).click()
  await expect(page.getByRole('button', { name: 'Connect' })).toBeVisible()
  expect(calls.find((c) => c.op === 'WithdrawConnectionRequest')?.variables).toEqual({ input: { requestId: 'r1' } })
})

test('an incoming request: Accept, then Connected', async ({ page }) => {
  let rel = relation({ pendingConnection: { __typename: 'PendingConnection', direction: 'INCOMING', requestId: 'r2' } }, { respondToConnection: true })
  const calls = await mockApi(page, {
    ProfileRelation: () => profileRelation(rel),
    RespondToConnectionRequest: () => ((rel = relation({ connected: true }, { removeConnection: true })), payload('respondToConnectionRequest', rel)),
  })
  await page.goto('/u/meera')
  await page.getByRole('button', { name: 'Accept' }).click()
  await expect(page.getByText('Connected', { exact: true })).toBeVisible()
  expect(calls.find((c) => c.op === 'RespondToConnectionRequest')?.variables).toEqual({ input: { requestId: 'r2', accept: true } })
  await page.getByRole('button', { name: 'More options' }).click()
  await expect(page.getByRole('menuitem', { name: 'Remove connection' })).toBeVisible()
})

test('an unverified viewer still sees Follow, and learns why it needs verification', async ({ page }) => {
  await mockApi(page, { ProfileRelation: () => profileRelation(relation({}, { follow: false }), USER, MEERA, false) }, { verified: false })
  await page.route('**/graphql', async (route, request) => {
    if ((request.postDataJSON() as { operationName?: string }).operationName === 'FollowUser') return route.fulfill({ json: { data: null, errors: [{ message: 'Verify your account to follow people.', extensions: { code: 'FORBIDDEN' } }] } })
    return route.fallback()
  })
  await page.goto('/u/meera')
  await page.getByRole('button', { name: 'Follow' }).click()
  await expect(page.getByRole('main').getByRole('alert')).toHaveText('Verify your account to follow people.')
})

test('a teacher edits the Skills tab: adds, orders and saves in one go', async ({ page }) => {
  const calls = await mockApi(page, {
    MyTeacherProfile: () => ({ viewer: { __typename: 'User', id: USER, handle: 'asharao', globalRole: 'TEACHER', teacherProfile: { __typename: 'TeacherProfile', headline: 'Teaches graphs', bio: null, skills: [{ __typename: 'TeacherSkill', id: 's1', kind: 'SKILL', name: 'Graphs', detail: null }] } } }),
    UpdateTeacherProfile: (v) => ({ updateTeacherProfile: { __typename: 'TeacherProfilePayload', profile: { __typename: 'TeacherProfile', headline: 'x', bio: null, skills: [] }, userErrors: [] }, _v: v }),
  }, { globalRole: 'TEACHER' })
  await page.goto('/profile/skills')
  await expect(page.getByLabel('Headline')).toHaveValue('Teaches graphs')
  await page.getByRole('button', { name: 'Add an item' }).click()
  const second = page.getByRole('group', { name: 'Item 2' })
  await second.getByLabel('Kind').selectOption('QUALIFICATION')
  await second.getByLabel('Name').fill('M.Tech')
  await second.getByRole('button', { name: 'Move up' }).click()
  await page.getByRole('button', { name: 'Save' }).click()
  await expect(page.getByRole('status')).toHaveText('Saved.')
  expect(calls.find((c) => c.op === 'UpdateTeacherProfile')?.variables).toEqual({
    input: { headline: 'Teaches graphs', bio: null, skills: [{ kind: 'QUALIFICATION', name: 'M.Tech', detail: null }, { kind: 'SKILL', name: 'Graphs', detail: null }] },
  })
})

test('teachers start blogs and posts from their notes; students start projects', async ({ page }) => {
  const created: unknown[] = []
  await mockApi(
    page,
    {
      MyNotes: () => ({ myNotes: { __typename: 'NoteConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
      CreateNote: (v) => (created.push(v), { createNote: { __typename: 'NotePayload', note: { __typename: 'Note', id: NOTE_ID }, userErrors: [] } }),
    },
    { globalRole: 'TEACHER' },
  )
  await page.goto('/notes')
  const group = page.getByRole('group', { name: 'Start something else' })
  await expect(group.getByRole('button')).toHaveText(['+ Project', '+ Blog post', '+ Post'])
  await group.getByRole('button', { name: '+ Blog post' }).click()
  await expect.poll(() => created.length).toBe(1)
  expect(created[0]).toMatchObject({ input: { kind: 'BLOG' } })
})
