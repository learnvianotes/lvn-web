import { expect, test, type Page } from '@playwright/test'
import { mockApi, NOTE_ID, USER } from './support/notes-api'

/**
 * Every screen's four states (P9e): when a query cannot be answered (here a server error), the screen says it could not
 * be loaded and offers Try again — never "nothing here" or "not found", and never a form that would save over what it
 * could not read.
 */

const GROUP = '01920000-0000-7000-8000-0000000a0001'
const page1 = (edges: unknown[]) => ({ edges, pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } })

/** Answers `op` with a server error while `failing()` holds; everything else goes on to the mocked API. */
async function failWhile(page: Page, op: string, failing: () => boolean) {
  await page.route('**/graphql', (route) => {
    const body = route.request().postDataJSON() as { operationName?: string }
    if (body.operationName === op && failing()) return route.fulfill({ status: 500, json: { errors: [{ message: 'Service unavailable' }] } })
    return route.fallback()
  })
}

const loadFailed = (page: Page) => page.getByRole('alert').filter({ hasText: 'This could not be loaded.' })

test('the Skills editor shows no form to save over a profile it could not load; Try again loads it', async ({ page }) => {
  let failing = true
  const calls = await mockApi(
    page,
    {
      MyTeacherProfile: () => ({ viewer: { __typename: 'User', id: USER, handle: 'asharao', globalRole: 'TEACHER', teacherProfile: { __typename: 'TeacherProfile', headline: 'Teaches graphs', bio: 'Ten years of graphs.', skills: [], drafts: [] } } }),
      MySkillsImport: () => ({ mySkillsImport: { __typename: 'SkillsImport', allowed: true, sources: ['GITHUB', 'WEBSITE'], identities: [] } }),
    },
    { globalRole: 'TEACHER' },
  )
  await failWhile(page, 'MyTeacherProfile', () => failing)
  await page.goto('/profile/skills')
  await expect(loadFailed(page)).toBeVisible()
  // No empty form, so nothing can wipe the headline, bio and skills it could not read.
  await expect(page.getByLabel('Headline')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Save', exact: true })).toHaveCount(0)

  failing = false
  await loadFailed(page).getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByLabel('Headline')).toHaveValue('Teaches graphs')
  await expect(page.getByLabel('About you')).toHaveValue('Ten years of graphs.')
  await expect(loadFailed(page)).toHaveCount(0)
  expect(calls.some((c) => c.op === 'UpdateTeacherProfile')).toBe(false)
})

test('a notes list that could not be loaded says so, not "Start your first note"; Try again shows the notes', async ({ page }) => {
  let failing = true
  await mockApi(page, {
    Organise: () => ({ myFolders: [], myTags: [] }),
    MyNotes: () => ({
      myNotes: page1([
        {
          __typename: 'NoteEdge',
          node: { __typename: 'Note', id: NOTE_ID, title: 'Searching', excerpt: 'Halve the range each step.', kind: 'NOTE', visibility: 'PRIVATE', draftUpdatedAt: new Date().toISOString(), publishedAt: null, deletedAt: null, cardCount: 2, folder: null, tags: [] },
        },
      ]),
    }),
  })
  await failWhile(page, 'MyNotes', () => failing)
  await page.goto('/notes')
  await expect(loadFailed(page)).toBeVisible()
  await expect(page.getByText('Start your first note')).toHaveCount(0)

  failing = false
  await loadFailed(page).getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByRole('link', { name: /Searching/ }).first()).toHaveAttribute('href', `/notes/${NOTE_ID}`)
  await expect(loadFailed(page)).toHaveCount(0)
})

test('a group that could not be loaded is not called unavailable; Try again opens it', async ({ page }) => {
  let failing = true
  const can = { __typename: 'GroupActions', join: false, requestJoin: true, post: false, moderate: false, manage: false, delete: false, reviewRequests: false, leave: false, askDoubt: false, inviteMentor: false, acceptMentorInvite: false }
  const calls = await mockApi(page, {
    Group: () => ({
      group: {
        __typename: 'Group', id: GROUP, type: 'COMMUNITY', name: 'Algorithms study', description: 'Weekly problems and solutions', privacy: 'PUBLIC', joinPolicy: 'APPROVAL', memberCount: 12, viewerRole: null, createdAt: '2026-10-01T10:00:00.000Z', viewerRequestId: null, viewerMentorInviteId: null, moderationWarning: null, pictureUrl: null,
        owner: { __typename: 'User', id: '01920000-0000-7000-8000-00000000bbbb', displayName: 'Meera Iyer' }, viewerCan: can,
      },
    }),
  })
  await failWhile(page, 'Group', () => failing)
  await page.goto(`/groups/${GROUP}`)
  await expect(loadFailed(page)).toBeVisible()
  await expect(page.getByText('This group is not available.')).toHaveCount(0)
  // A failure is not a removed group: the owner's removal notice is not even asked for.
  expect(calls.some((c) => c.op === 'RemovedGroup')).toBe(false)

  failing = false
  await loadFailed(page).getByRole('button', { name: 'Try again' }).click()
  await expect(page.getByRole('heading', { level: 1, name: 'Algorithms study' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Ask to join' })).toBeVisible()
  await expect(loadFailed(page)).toHaveCount(0)
})
