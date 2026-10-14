import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page, type Route } from '@playwright/test'

/**
 * Sign-in and sign-up screens (§12.1 `(auth)`) against a mocked GraphQL API: the UI's wiring — validation, field
 * errors from userErrors, session handling, redirects — without a backend. The real API is covered by lvn-backend's
 * e2e suite; sandbox runs the two together (§17).
 */

type Handler = (variables: Record<string, unknown>) => unknown

const viewer = (over: Record<string, unknown> = {}) => ({
  __typename: 'User',
  id: '01920000-0000-7000-8000-00000000aaaa',
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
  profile: null,
  legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null },
  ...over,
})
const session = (user = viewer()) => ({ __typename: 'Session', accessToken: 'header.payload.sig', accessTokenExpiresAt: new Date(Date.now() + 900_000).toISOString(), user })
const ok = { __typename: 'OkPayload', ok: true, userErrors: [] }
/** A userError as the API sends it (Apollo matches fragments by __typename). */
const problem = (field: string[] | null, message: string, code = 'VALIDATION') => ({ __typename: 'UserError', field, message, code })
const fail = (...problems: ReturnType<typeof problem>[]) => ({ __typename: 'OkPayload', ok: false, userErrors: problems })

/**
 * Answers GraphQL by operation name; the session restore (an anonymous refreshSession) by `refresh`. A `withGoogle`
 * entry makes the API offer Google (the e2e build has a stand-in Firebase config, playwright.config.ts).
 */
async function mockApi(page: Page, handlers: Record<string, Handler>, refresh: 'signed-in' | 'signed-out' = 'signed-out') {
  const calls: { op: string; variables: Record<string, unknown> }[] = []
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { query: string; operationName?: string; variables?: Record<string, unknown> }
    const op = body.operationName ?? (body.query.includes('refreshSession') ? 'Refresh' : 'unknown')
    calls.push({ op, variables: body.variables ?? {} })
    let data: unknown
    if (op === 'Refresh' || op === 'RefreshSession') {
      data = { refreshSession: refresh === 'signed-in' ? { session: session() } : null }
      if (refresh === 'signed-out') return route.fulfill({ json: { data: null, errors: [{ message: 'Session ended', extensions: { code: 'UNAUTHENTICATED' } }] } })
    } else if (op === 'SignInOptions') {
      data = { signInOptions: { emailPassword: true, google: !!handlers.withGoogle, github: false, linkedin: false }, termsVersion: '2026-10-08' }
    } else if (handlers[op]) {
      data = handlers[op]!(body.variables ?? {})
    } else {
      return route.fulfill({ status: 500, json: { errors: [{ message: `unmocked ${op}` }] } })
    }
    return route.fulfill({ json: { data } })
  })
  return calls
}

test.describe('sign up', () => {
  test('checks the form before sending anything', async ({ page }) => {
    const calls = await mockApi(page, {})
    await page.goto('/sign-up')
    await page.getByRole('button', { name: 'Create account' }).click()
    await expect(page.getByText('Accept the terms to continue.')).toBeVisible()
    await expect(page.getByLabel('Email', { exact: true })).toHaveAttribute('aria-invalid', 'true')
    expect(calls.filter((c) => c.op === 'SignUp')).toHaveLength(0)
  })

  test('shows the API’s field errors next to the field', async ({ page }) => {
    await mockApi(page, {
      SignUp: () => ({ signUp: { __typename: 'AuthPayload', session: null, userErrors: [problem(['input', 'email'], 'An account with this email already exists. Sign in instead.', 'CONFLICT')] } }),
    })
    await page.goto('/sign-up')
    await fillSignUp(page)
    await page.getByRole('button', { name: 'Create account' }).click()
    await expect(page.getByText('An account with this email already exists. Sign in instead.')).toBeVisible()
  })

  test('signs up with the current terms version and lands on the account page', async ({ page }) => {
    const calls = await mockApi(page, { SignUp: () => ({ signUp: { __typename: 'AuthPayload', session: session(), userErrors: [] } }), Viewer: () => ({ viewer: viewer() }) })
    await page.goto('/sign-up')
    await fillSignUp(page)
    await page.getByRole('button', { name: 'Create account' }).click()
    await expect(page).toHaveURL(/\/profile$/)
    await expect(page.getByRole('heading', { name: 'Asha Rao' })).toBeVisible()
    const input = calls.find((c) => c.op === 'SignUp')!.variables.input as Record<string, unknown>
    expect(input).toMatchObject({ acceptedTermsVersion: '2026-10-08', dateOfBirth: '2004-05-01', institutionalEmail: null })
  })

  test('someone who teaches picks Teach, and goes on to apply (lvn-backend ADR-0073)', async ({ page }) => {
    await mockApi(page, { SignUp: () => ({ signUp: { __typename: 'AuthPayload', session: session(), userErrors: [] } }), Viewer: () => ({ viewer: viewer() }), MyTeacherApplication: () => ({ myTeacherApplication: null }) })
    await page.goto('/sign-up')
    await fillSignUp(page)
    await page.getByText('Teach', { exact: true }).click()
    await expect(page.getByRole('radio', { name: 'Teach' })).toBeChecked()
    await expect(page.getByText('After sign-up, tell us where you teach.', { exact: false })).toBeVisible()
    await page.getByRole('button', { name: 'Create account' }).click()
    await expect(page).toHaveURL(/\/teach$/)
    await expect(page.getByRole('form', { name: 'Apply to teach' })).toBeVisible()
  })

  test('goes to the code screen when a college email was given', async ({ page }) => {
    await mockApi(page, {
      SignUp: () => ({ signUp: { __typename: 'AuthPayload', session: session(viewer({ institutionalEmail: 'asha@iitb.ac.in', institutionalEmailStatus: 'CODE_SENT' })), userErrors: [] } }),
      Viewer: () => ({ viewer: viewer({ institutionalEmail: 'asha@iitb.ac.in', institutionalEmailStatus: 'CODE_SENT' }) }),
      VerifyInstitutionalEmail: (v) => ({ verifyInstitutionalEmail: v.code === '123456' ? ok : fail(problem(['input', 'code'], 'That code is not right. 4 tries left.')) }),
    })
    await page.goto('/sign-up')
    await fillSignUp(page)
    await page.getByLabel('College or organisation email (optional)').fill('asha@iitb.ac.in')
    await page.getByRole('button', { name: 'Create account' }).click()
    await expect(page).toHaveURL(/\/verify$/)
    await expect(page.getByText('We sent a 6-digit code to asha@iitb.ac.in.')).toBeVisible()
    await page.getByLabel('Code').fill('000000')
    await page.getByRole('button', { name: 'Verify' }).click()
    await expect(page.getByText('That code is not right. 4 tries left.')).toBeVisible()
  })
})

test.describe('sign in', () => {
  test('shows one message for a wrong email or password', async ({ page }) => {
    await mockApi(page, { SignIn: () => ({ signIn: { __typename: 'AuthPayload', session: null, userErrors: [problem(null, 'Email or password is incorrect.')] } }) })
    await page.goto('/sign-in')
    await page.getByLabel('Email').fill('asha@example.com')
    await page.getByLabel('Password').fill('wrong password')
    await page.getByRole('button', { name: 'Sign in' }).click()
    await expect(page.getByRole('main').getByRole('alert')).toHaveText('Email or password is incorrect.')
  })

  test('asks a new provider account for its registration details', async ({ page }) => {
    await mockApi(page, {
      SignIn: () => ({ signIn: { __typename: 'AuthPayload', session: session(viewer({ registrationComplete: false })), userErrors: [] } }),
      Viewer: () => ({ viewer: viewer({ registrationComplete: false }) }),
    })
    await page.goto('/sign-in?next=/subjects/dsa')
    await page.getByLabel('Email').fill('asha@example.com')
    await page.getByLabel('Password').fill('a long enough passphrase')
    await page.getByRole('button', { name: 'Sign in' }).click()
    await expect(page).toHaveURL(/\/sign-up\/details\?next=%2Fsubjects%2Fdsa$/)
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Almost there, Asha')
    await expect(page.getByLabel('Your name')).toHaveValue('Asha Rao')
  })

  test('sends signed-out visitors of the account page to sign in and back', async ({ page }) => {
    await mockApi(page, {})
    await page.goto('/profile')
    await expect(page).toHaveURL(/\/sign-in\?next=%2Fprofile$/)
  })

  test('restores the session from the refresh cookie on load', async ({ page }) => {
    await mockApi(page, { Viewer: () => ({ viewer: viewer({ verified: true, verificationMethod: 'TEACHER' }) }) }, 'signed-in')
    await page.goto('/profile')
    await expect(page.getByText('✓ Verified')).toBeVisible()
    await expect(page.getByText('by a teacher')).toBeVisible()
  })
})

test.describe('links from emails', () => {
  test('confirms the sign-in email from /verify?token=', async ({ page }) => {
    await mockApi(page, { VerifyEmail: (v) => ({ verifyEmail: v.token === 'good' ? ok : fail(problem(['input', 'token'], 'This link is invalid or has expired. Ask for a new one.')) }) })
    await page.goto('/verify?token=good')
    await expect(page.getByText('Your email is confirmed.')).toBeVisible()
    await page.goto('/verify?token=old')
    await expect(page.getByText('This link is invalid or has expired. Ask for a new one.')).toBeVisible()
  })

  test('requests a reset link, then sets a new password from it', async ({ page }) => {
    await mockApi(page, { RequestPasswordReset: () => ({ requestPasswordReset: ok }), ResetPassword: () => ({ resetPassword: ok }) })
    await page.goto('/reset')
    await page.getByLabel('Email').fill('asha@example.com')
    await page.getByRole('button', { name: 'Send link' }).click()
    await expect(page.getByText(/If an account uses that email/)).toBeVisible()
    await page.goto('/reset?token=abc')
    await page.getByLabel('New password').fill('a brand new passphrase')
    await page.getByRole('button', { name: 'Save password' }).click()
    await expect(page.getByText(/Your password is changed/)).toBeVisible()
  })

  test('refuses an OAuth callback that this tab did not start', async ({ page }) => {
    await mockApi(page, {})
    await page.goto('/oauth/callback?code=abc&state=forged')
    await expect(page.getByText(/could not be completed/)).toBeVisible()
  })
})

test.describe('Google first', () => {
  const offered = { withGoogle: () => null }

  test('the landing page offers Get Started Free and Continue with Google side by side, then sign-in (board A)', async ({ page }) => {
    await mockApi(page, offered)
    await page.goto('/')
    const main = page.getByRole('main')
    await expect(main.getByRole('heading', { level: 1 })).toHaveText('Your Learning Community for a Brighter Tomorrow')
    await expect(main.getByRole('link', { name: 'Get Started Free' })).toHaveAttribute('href', '/sign-up')
    await expect(main.getByRole('button', { name: 'Continue with Google' })).toBeVisible()
    await main.getByRole('link', { name: 'Sign in', exact: true }).click()
    await expect(page).toHaveURL(/\/sign-in$/)
    await expect(page.getByRole('button', { name: 'Continue with Google' })).toBeVisible()
  })

  test('without Google, Get Started Free is the way in', async ({ page }) => {
    await mockApi(page, {})
    await page.goto('/')
    const main = page.getByRole('main')
    await expect(main.getByRole('button', { name: 'Continue with Google' })).toHaveCount(0)
    await main.getByRole('link', { name: 'Get Started Free' }).click()
    await expect(page).toHaveURL(/\/sign-up$/)
    await expect(page.getByRole('heading', { level: 1 })).toHaveText('Create your account')
  })

  test('someone signed in is offered their account instead', async ({ page }) => {
    await mockApi(page, { Viewer: () => ({ viewer: viewer() }) }, 'signed-in')
    await page.goto('/')
    const main = page.getByRole('main')
    await expect(main.getByRole('link', { name: 'Open your home' })).toHaveAttribute('href', '/home')
    await expect(main.getByRole('link', { name: 'Get Started Free' })).toHaveCount(0)
    await main.getByRole('link', { name: 'Your account' }).click()
    await expect(page).toHaveURL(/\/profile$/)
  })
})

test('sign-in and sign-up have no serious accessibility violations', async ({ page }) => {
  // Checked as it settles: fade-ins would be measured half-transparent.
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await mockApi(page, {})
  for (const path of ['/sign-in', '/sign-up']) {
    await page.goto(path)
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
    const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
    expect(violations.filter((v) => v.impact === 'critical' || v.impact === 'serious').map((v) => `${path}: ${v.id}`)).toEqual([])
  }
})

async function fillSignUp(page: Page) {
  await page.getByLabel('Your name').fill('Asha Rao')
  await page.getByLabel('Email', { exact: true }).fill('asha@example.com')
  await page.getByLabel('Password').fill('a long enough passphrase')
  await page.getByLabel('Date of birth').fill('2004-05-01')
  await page.getByRole('checkbox').check()
}
