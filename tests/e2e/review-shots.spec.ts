import { expect, test, type Page, type Route } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Screenshots for the integration review. The API is mocked. Set REVIEW_SHOTS_DIR to write PNGs;
 * the assertions run either way.
 */

const dir = process.env.REVIEW_SHOTS_DIR
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const emptyPage = { __typename: 'PageInfo', hasNextPage: false, endCursor: null }
const zero = { tasksRun: 0, failures: 0, promptTokens: '0', completionTokens: '0', costMicroUsd: '0' }

const rhythm = {
  __typename: 'Rhythm',
  timeZone: 'UTC',
  plannedDays: [1, 2, 4, 6],
  target: 4,
  countedDays: 1,
  met: false,
  week: ['COUNTED', 'MISSED', 'REST', 'TODAY', 'AHEAD', 'AHEAD', 'AHEAD'].map((status, i) => ({
    __typename: 'RhythmDay',
    day: `2026-10-${12 + i}`,
    weekday: i + 1,
    planned: [1, 2, 4, 6].includes(i + 1),
    counted: status === 'COUNTED',
    status,
  })),
  today: { __typename: 'RhythmToday', day: '2026-10-15', learningSeconds: 300, reviews: 0, counted: false, comeback: false, cameBack: false, items: [] },
  weeksThisTerm: 2,
  weeksAllTime: 5,
  countedDaysAllTime: 30,
  pauses: [],
  pauseDaysLeft: 14,
  suggestion: null,
  shareRhythm: false,
}

const metrics = {
  __typename: 'AdminMetrics',
  generatedAt: '2026-10-26T12:00:00.000Z',
  users: { __typename: 'AdminUserMetrics', total: 128, newLast7Days: 6, newLast30Days: 22, active: 40 },
  content: { __typename: 'AdminContentMetrics', notes: 80, publicNotes: 12, subjects: 9, topics: 140, groups: 4, classrooms: 3 },
  ai: { __typename: 'AdminAiMetrics', from: null, to: null, ...zero, byProvider: [], byModel: [], byTask: [] },
  storage: { __typename: 'AdminStorageMetrics', bytes: '1048576', files: 12 },
  verification: { __typename: 'AdminVerificationMetrics', studentIdQueue: 1, pendingRequests: 2, domainReviews: 0 },
  moderation: { __typename: 'AdminModerationMetrics', openReports: 0, openAppeals: 0 },
}

async function shot(page: Page, name: string) {
  if (!dir) return
  await page.screenshot({ path: `${dir}/${name}.png`, fullPage: true })
}

async function signedOut(page: Page, google: boolean) {
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { query?: string; operationName?: string; variables?: Record<string, unknown> }
    const op = body.operationName ?? (body.query?.includes('refreshSession') ? 'Refresh' : 'unknown')
    if (op === 'Refresh' || op === 'RefreshSession') {
      return route.fulfill({ json: { data: null, errors: [{ message: 'Session ended', extensions: { code: 'UNAUTHENTICATED' } }] } })
    }
    if (op === 'SignInOptions') {
      return route.fulfill({ json: { data: { signInOptions: { emailPassword: true, google, github: false, linkedin: false }, termsVersion: '2026-10-08' } } })
    }
    if (op === 'AccessPolicy') return route.fulfill({ json: { data: { accessPolicy: { __typename: 'AccessPolicy', inviteOnly: false } } } })
    if (op === 'SignIn') {
      return route.fulfill({
        json: {
          data: {
            signIn: {
              __typename: 'AuthPayload',
              session: null,
              userErrors: [{ __typename: 'UserError', field: null, message: 'This account could not be activated.', code: 'AGE_RESTRICTED', supportEmail: 'support@learnvianotes.in' }],
            },
          },
        },
      })
    }
    return route.fulfill({ status: 500, json: { errors: [{ message: `unmocked ${op}` }] } })
  })
}

const homeHandlers = {
  Rhythm: () => ({ rhythm }),
  Exams: () => ({ exams: [] }),
  Recommendations: () => ({ recommendations: [] }),
  DailyLine: () => ({ dailyLine: { __typename: 'DailyLine', day: '2026-10-26', title: 'Small steps count', line: 'Ten focused minutes today.', fromAi: false, pending: false } }),
  MyGroups: () => ({ myGroups: [] }),
  MyClassrooms: () => ({ myClassrooms: [] }),
}

test('sign-in offers Google and email, and an age block names the support address', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop', 'desktop capture')
  await signedOut(page, true)
  await page.goto('/sign-in')
  await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Continue with Google' })).toBeVisible()
  await expect(page.getByLabel('Email')).toBeVisible()
  await shot(page, 'sign-in-google-email')

  await page.getByLabel('Email').fill('ravi@college.edu')
  await page.getByLabel('Password').fill('a long enough passphrase')
  await page.getByRole('button', { name: 'Sign in', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'This account couldn’t be activated' })).toBeVisible()
  await shot(page, 'age-blocked')
})

test('the public phone header opens Browse', async ({ page }, info) => {
  test.skip(info.project.name !== 'phone', 'phone capture')
  await signedOut(page, true)
  await page.goto('/sign-in')
  await expect(page.getByRole('button', { name: 'Continue with Google' })).toBeVisible()
  await page.getByRole('button', { name: 'Browse' }).click()
  await expect(page.getByRole('navigation', { name: 'Browse' }).getByRole('link', { name: 'Subjects' })).toBeVisible()
  await shot(page, 'phone-public-nav')
})

test('home, My Notes and Explore render for a signed-in student', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop', 'desktop capture')
  await mockApi(
    page,
    {
      ...homeHandlers,
      Organise: () => ({ myFolders: [], myTags: [] }),
      MyNotes: () => ({ myNotes: { __typename: 'NoteConnection', edges: [], pageInfo: emptyPage } }),
    },
    viewerExtras,
  )
  await page.goto('/home')
  await expect(page.getByRole('heading', { level: 1, name: /Asha/ })).toBeVisible()
  await expect(page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'Admin' })).toHaveCount(0)
  await shot(page, 'home')

  await page.goto('/notes')
  await expect(page.getByRole('heading', { level: 1, name: 'Your first note is one click away.' })).toBeVisible()
  await shot(page, 'my-notes')

  await page.goto('/search')
  await expect(page.getByRole('heading', { level: 1, name: 'Search' })).toBeVisible()
  await shot(page, 'explore')
})

test('an admin sees Admin in the sidebar and the admin pages', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop', 'desktop capture')
  await mockApi(
    page,
    {
      ...homeHandlers,
      AdminMetrics: () => ({ adminMetrics: metrics }),
      AdminErrors: () => ({ adminErrors: [] }),
      AdminUsage: () => ({
        adminUsage: { __typename: 'AdminUsage', dau: 12, wau: 40, mau: 90, from: '2026-09-26T00:00:00.000Z', to: '2026-10-26T00:00:00.000Z', topEvents: [], topFeatures: [] },
      }),
      AdminUsers: () => ({ adminUsers: { __typename: 'AdminUserList', total: 0, users: [] } }),
      StudentIdVerificationEnabled: () => ({ studentIdVerificationEnabled: true }),
      StudentIdVerificationQueue: () => ({ studentIdVerificationQueue: [] }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/home')
  const nav = page.getByRole('navigation', { name: 'Main' })
  await expect(nav.getByRole('link', { name: 'Admin', exact: true })).toBeVisible()
  await shot(page, 'admin-sidebar-item')

  await nav.getByRole('link', { name: 'Admin', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Overview' })).toBeVisible()
  await expect(page.getByRole('navigation', { name: 'Admin settings' }).getByRole('link', { name: 'College ID cards' })).toBeVisible()
  await shot(page, 'admin-overview')

  for (const [href, heading, file] of [
    ['/admin/errors', 'Errors', 'admin-errors'],
    ['/admin/usage', 'Usage', 'admin-usage'],
    ['/admin/users', 'Users', 'admin-users'],
    ['/admin/student-id', 'College ID cards', 'admin-student-id'],
  ] as const) {
    await page.goto(href)
    await expect(page.getByRole('heading', { name: heading })).toBeVisible()
    await shot(page, file)
  }
})

test('phone navigation includes Admin for an admin', async ({ page }, info) => {
  test.skip(info.project.name !== 'phone', 'phone capture')
  await mockApi(page, homeHandlers, { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' })
  await page.goto('/home')
  await page.getByRole('button', { name: 'Menu' }).click()
  const menu = page.getByRole('dialog', { name: 'Menu' })
  await expect(menu.getByRole('link', { name: 'Admin', exact: true })).toBeVisible()
  await expect(menu.getByRole('link', { name: 'My Notes' })).toBeVisible()
  await expect(menu.getByRole('link', { name: 'Explore' })).toBeVisible()
  await shot(page, 'phone-app-nav-admin')
  await menu.getByRole('link', { name: 'Admin', exact: true }).click()
  await expect(page).toHaveURL(/\/admin$/)
})
