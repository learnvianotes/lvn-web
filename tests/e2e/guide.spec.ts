import { expect, test, type Page, type Route } from '@playwright/test'

/**
 * The public guide, and the create-profile step: no age dialog, age 7 refused, age 8 sent,
 * then the first-run tour. GraphQL is mocked. Email sign-up still confirms the age (auth.spec.ts).
 */

const USER = '01920000-0000-7000-8000-00000000aaaa'

const viewer = (over: Record<string, unknown> = {}) => ({
  __typename: 'User',
  id: USER,
  handle: 'asharao',
  displayName: 'Asha Rao',
  email: 'asha@example.com',
  emailVerified: true,
  registrationComplete: true,
  verified: false,
  verificationMethod: null,
  globalRole: 'STUDENT',
  teacherStatus: 'NONE',
  restrictedMinor: false,
  institutionalEmail: null,
  institutionalEmailStatus: 'NONE',
  institution: null,
  deletionScheduledFor: null,
  profile: null,
  legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null },
  viewerNeedsVerification: true,
  ...over,
})

test('the guide is public, names real tools, and is linked from the footer', async ({ page }) => {
  await page.goto('/guide')
  await expect(page.getByRole('heading', { level: 1, name: 'Guide' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Read and find notes' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Groups' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Classrooms' })).toBeVisible()
  await expect(page.getByText('Accounts start at age 8.')).toBeVisible()
  await expect(page.getByText('Age 7 cannot create an account.')).toBeVisible()
  await expect(page.getByRole('link', { name: 'support@learnvianotes.in' })).toHaveAttribute('href', 'mailto:support@learnvianotes.in')
  await expect(page.getByRole('contentinfo').getByRole('link', { name: 'Guide' })).toHaveAttribute('href', '/guide')
  await expect(page.getByRole('link', { name: 'Replay the walkthrough' })).toHaveAttribute('href', /\/sign-in\?next=/)
  await expect(page).toHaveTitle(/Guide · LearnViaNotes/)
})

test('age 7 is refused on create-profile, age 8 continues with no dialog, and the tour plays once', async ({ page }) => {
  let registered = false
  const calls = await mock(page, () => registered)
  await page.route('**/graphql', async (route) => {
    const body = route.request().postDataJSON() as { operationName?: string }
    if (body.operationName === 'CompleteRegistration') registered = true
    return route.fallback()
  })
  await page.goto('/sign-in')
  await page.getByLabel('Email').fill('asha@example.com')
  await page.getByLabel('Password').fill('a long enough passphrase')
  await page.getByRole('button', { name: 'Sign in' }).click()
  await expect(page).toHaveURL(/\/sign-up\/details/)
  const age = page.getByLabel('Your age')
  await page.getByRole('checkbox').check()
  await age.fill('7')
  await page.getByRole('button', { name: 'Continue' }).click()
  await expect(page.getByRole('alert').filter({ hasText: 'Enter an age from 8 to 120.' })).toBeVisible()
  await expect(page.getByRole('dialog', { name: 'Is this right?' })).toHaveCount(0)
  expect(calls.filter((c) => c.op === 'CompleteRegistration')).toHaveLength(0)
  await age.fill('8')
  await page.getByRole('button', { name: 'Continue' }).click()
  await expect(page.getByRole('dialog', { name: 'Is this right?' })).toHaveCount(0)
  await expect(page).toHaveURL(/\/home$/)
  expect(calls.find((c) => c.op === 'CompleteRegistration')?.variables.input).toMatchObject({ age: 8 })

  const tour = page.getByRole('dialog', { name: 'Read and write notes' })
  await expect(tour).toBeVisible()
  await tour.getByRole('button', { name: 'Next' }).click()
  await expect(page.getByRole('dialog', { name: 'Find notes and people' })).toBeVisible()
  await page.keyboard.press('Escape')
  await expect(page.getByRole('dialog', { name: 'Find notes and people' })).toHaveCount(0)

  await page.reload()
  await expect(page.getByRole('dialog', { name: 'Read and write notes' })).toHaveCount(0)

  await page.goto('/guide')
  await page.getByRole('button', { name: 'Replay the walkthrough' }).click()
  await expect(page.getByRole('dialog', { name: 'Read and write notes' })).toBeVisible()
  await page.getByRole('button', { name: 'Skip the tour' }).click()
  await expect(page.getByRole('dialog', { name: 'Read and write notes' })).toHaveCount(0)
})

/** Signed-out until SignIn, then a viewer whose registration flips when the test says it has. */
async function mock(page: Page, registered: () => boolean) {
  const calls: { op: string; variables: Record<string, unknown> }[] = []
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { operationName?: string; query?: string; variables?: Record<string, unknown> }
    const op = body.operationName ?? (body.query?.includes('refreshSession') ? 'Refresh' : 'unknown')
    calls.push({ op, variables: body.variables ?? {} })
    const session = {
      __typename: 'Session',
      accessToken: 'header.payload.sig',
      accessTokenExpiresAt: new Date(Date.now() + 900_000).toISOString(),
      user: viewer({ registrationComplete: registered() }),
    }
    const ok = { __typename: 'OkPayload', ok: true, userErrors: [] }
    if (op === 'Refresh' || op === 'RefreshSession') {
      if (!registered()) return route.fulfill({ json: { data: null, errors: [{ message: 'Session ended', extensions: { code: 'UNAUTHENTICATED' } }] } })
      return route.fulfill({ json: { data: { refreshSession: { session: { ...session, user: viewer({ registrationComplete: true }) } } } } })
    }
    const data: Record<string, unknown> = {
      SignInOptions: { signInOptions: { emailPassword: true, google: false, github: false, linkedin: false }, termsVersion: '2026-10-08' },
      AccessPolicy: { accessPolicy: { __typename: 'AccessPolicy', inviteOnly: false } },
      SignIn: { signIn: { __typename: 'AuthPayload', session: { ...session, user: viewer({ registrationComplete: false }) }, userErrors: [] } },
      Viewer: { viewer: viewer({ registrationComplete: registered() }) },
      CompleteRegistration: { completeRegistration: ok },
      TermsStatus: { termsVersion: '2026-10-08', viewer: { __typename: 'User', id: USER, termsAccepted: true } },
      UnreadNotificationCount: { unreadNotificationCount: 0 },
      UploadsEnabled: { uploadsEnabled: true },
      AnalyticsOptOut: { viewer: { __typename: 'User', id: USER, analyticsOptOut: false } },
      IngestAnalytics: { ingestAnalytics: ok },
      SetLearningTimeZone: { setLearningTimeZone: ok },
      MyStanding: { myStanding: { __typename: 'AccountStanding', suspendedUntil: null, suspensionReason: null, canAppeal: false, warnings: [] } },
      StudentIdVerificationEnabled: { studentIdVerificationEnabled: false },
      PublicNotesRequireVerification: { publicNotesRequireVerification: false },
      UnverifiedGatedActions: { unverifiedGatedActions: [] },
      Rhythm: { rhythm: null },
      Exams: { exams: [] },
      Recommendations: { recommendations: [] },
      DailyLine: { dailyLine: { __typename: 'DailyLine', day: '2026-11-06', title: 'Small steps count', line: 'Ten focused minutes today.', fromAi: false, pending: false } },
      MyGroups: { myGroups: [] },
      MyClassrooms: { myClassrooms: [] },
    }
    const payload = data[op]
    if (!payload) return route.fulfill({ status: 500, json: { errors: [{ message: `unmocked ${op}` }] } })
    return route.fulfill({ json: { data: payload } })
  })
  return calls
}
