import { expect, test, type Page } from '@playwright/test'
import { mockApi, USER } from './support/notes-api'

/**
 * Admin sidebar, verification review, roles, institution domains, AI switches, grouped errors and usage.
 * Screenshots are written when ADMIN_PLATFORM_SHOTS is set.
 */

const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const none = { userErrors: [] }
const raviId = '01920000-0000-7000-8000-0000000000e2'
const requestId = '01920000-0000-7000-8000-0000000ve001'
const fileId = '01920000-0000-7000-8000-00000000f0d1'

async function shot(page: Page, name: string) {
  const dir = process.env.ADMIN_PLATFORM_SHOTS
  if (!dir) return
  await page.screenshot({ path: `${dir}/${name}.png`, fullPage: true })
}

const reviewRequest = {
  __typename: 'VerificationRequest',
  id: requestId,
  purpose: 'ACCOUNT',
  institution: 'IIT Hyderabad',
  subjects: null,
  method: 'DOCUMENTS',
  status: 'PENDING',
  message: 'This is my college ID.',
  reason: null,
  createdAt: '2026-10-20T08:00:00.000Z',
  requester: {
    __typename: 'User',
    id: raviId,
    displayName: 'Ravi Kumar',
    handle: 'ravi',
    email: 'ravi@college.edu',
    institution: { __typename: 'Institution', name: 'IIT Hyderabad' },
    profile: { __typename: 'Profile', department: 'Computer Science' },
  },
  documents: [{ __typename: 'VerificationDocument', fileId, fileName: 'id-card.png', mimeType: 'image/png', sizeBytes: 400 }],
  aiCheck: {
    __typename: 'IdCardCheck',
    verdict: 'MATCH',
    confidence: 0.82,
    reason: 'The name and college on the card match the profile.',
    checkedAt: '2026-10-20T08:05:00.000Z',
    extracted: { __typename: 'IdCardFields', name: 'Ravi Kumar', institution: 'IIT Hyderabad', idNumber: 'IH20201234', validUntil: '2027-05' },
  },
}

test('an admin sees Admin in the sidebar; a student does not', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the phone menu is the same list, checked with the review card')
  await mockApi(page, {}, { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' })
  await page.goto('/home')
  const nav = page.getByRole('navigation', { name: 'Main' })
  await expect(nav.getByRole('link', { name: 'Admin', exact: true })).toHaveAttribute('href', '/admin')
  const labels = await nav.getByRole('link').allTextContents()
  expect(labels.slice(0, 4)).toEqual(['Home', 'My Notes', 'Explore', 'Admin'])
  await shot(page, 'sidebar_admin')

  await mockApi(page, {})
  await page.goto('/home')
  await expect(page.getByRole('navigation', { name: 'Main' }).getByRole('link', { name: 'Admin', exact: true })).toHaveCount(0)
})

test('a manager cannot open the verification or college ID queues', async ({ page }) => {
  const calls = await mockApi(
    page,
    { VerificationRequestsToReview: () => ({ verificationRequestsToReview: [reviewRequest] }) },
    { ...viewerExtras, globalRole: 'MANAGER' },
  )
  await page.goto('/admin/verification')
  await expect(page.getByText('Only platform admins and verified teachers can review these.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0)
  await expect(page.getByRole('navigation', { name: 'Admin settings' })).toHaveCount(0)
  expect(calls.some((call) => call.op === 'VerificationRequestsToReview')).toBe(false)

  await page.goto('/admin/student-id')
  await expect(page.getByText('Only platform admins and verified teachers can review these.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0)
})

test('a teacher sees the review sections and cannot assign roles', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the sections are the same list')
  await mockApi(page, { VerificationRequestsToReview: () => ({ verificationRequestsToReview: [] }) }, { ...viewerExtras, globalRole: 'TEACHER', verified: true })
  await page.goto('/admin/verification')
  const nav = page.getByRole('navigation', { name: 'Admin settings' })
  await expect(nav.getByRole('link')).toHaveText(['Proof of study to review', 'College ID cards'])
  await page.goto('/admin/roles')
  await expect(page.getByText('Only platform admins can assign roles.')).toBeVisible()
})

test('an unverified teacher cannot review verification requests', async ({ page }) => {
  const calls = await mockApi(
    page,
    { VerificationRequestsToReview: () => ({ verificationRequestsToReview: [reviewRequest] }) },
    { ...viewerExtras, globalRole: 'TEACHER', verified: false },
  )
  await page.goto('/admin/verification')
  await expect(page.getByText('Only platform admins and verified teachers can review these.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Approve' })).toHaveCount(0)
  await expect(page.getByRole('navigation', { name: 'Admin settings' })).toHaveCount(0)
  expect(calls.some((call) => call.op === 'VerificationRequestsToReview')).toBe(false)
})

test('an admin assigns a role, decides a domain, and turns on the ID-card check', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the forms are the same')
  let domains = [{ __typename: 'DomainReview', domain: 'newcollege.edu', status: 'NEEDS_REVIEW', requests: 4, firstSeenAt: '2026-10-01T00:00:00.000Z' }]
  const constraints = { __typename: 'AdminSettingConstraints', min: null, max: null, maxLength: null, pattern: null, nullable: false }
  const setting = (key: string, type: string, value: string, description: string, extra: Record<string, unknown> = {}) => ({
    __typename: 'AdminSetting',
    key,
    type,
    category: 'verification',
    description,
    value,
    overridden: false,
    updatedAt: '2026-10-01T00:00:00.000Z',
    constraints,
    ...extra,
  })
  let catalog = [
    setting('uploads_enabled', 'BOOLEAN', 'true', 'Allow files to be uploaded.', { category: 'uploads' }),
    setting('student_id_ai_check', 'BOOLEAN', 'false', 'Store the verdict, confidence and the reasons on the request.'),
    setting('student_id_ai_auto_approve', 'BOOLEAN', 'false', 'Approve on its own when the score is at least the threshold.'),
    setting('student_id_ai_confidence_threshold', 'INTEGER', '80', 'Lowest score that can be approved on its own.', { constraints: { ...constraints, min: 0, max: 100 } }),
    setting('student_id_image_retention_days', 'INTEGER', '7', 'How long a card image is kept after it is read.', { constraints: { ...constraints, min: 0, max: 365 } }),
  ]
  const calls = await mockApi(
    page,
    {
      Search: () => ({
        search: {
          __typename: 'SearchResults',
          notes: [],
          notesCursor: null,
          people: [{ __typename: 'User', id: raviId, handle: 'ravi', displayName: 'Ravi Kumar', globalRole: 'STUDENT' }],
          topics: [],
          groups: [],
          classes: [],
        },
      }),
      SetGlobalRole: () => ({ setGlobalRole: { __typename: 'OkPayload', ok: true, ...none } }),
      InstitutionDomains: () => ({ institutionDomains: domains }),
      ReviewInstitutionDomain: (v) => {
        const input = v.input as { domain: string; approve: boolean }
        domains = domains.map((row) => (row.domain === input.domain ? { ...row, status: input.approve ? 'APPROVED' : 'REJECTED' } : row))
        return { reviewInstitutionDomain: { __typename: 'OkPayload', ok: true, ...none } }
      },
      AdminSettings: () => ({ adminSettings: catalog }),
      UpdateAdminSetting: (v) => {
        const input = v.input as { key: string; value: string }
        catalog = catalog.map((row) => (row.key === input.key ? { ...row, value: input.value, overridden: true } : row))
        return { updateAdminSetting: { __typename: 'AdminSettingPayload', setting: catalog.find((row) => row.key === input.key), ...none } }
      },
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )

  await page.goto('/admin/roles')
  await page.getByPlaceholder('Name or handle').fill('ravi')
  const person = page.getByRole('article', { name: 'Ravi Kumar' })
  await expect(person.getByText('Student')).toBeVisible()
  await person.getByRole('button', { name: 'Make manager' }).click()
  await expect(person.getByText('@ravi · Manager')).toBeVisible()
  expect(calls.find((call) => call.op === 'SetGlobalRole')?.variables).toEqual({ input: { userId: raviId, role: 'MANAGER' } })

  await page.goto('/admin/domains')
  await expect(page.getByText('newcollege.edu')).toBeVisible()
  await page.getByRole('button', { name: 'Approve' }).click()
  await expect(page.getByText('No domains are waiting.')).toBeVisible()
  await expect(page.getByRole('list').getByText('newcollege.edu')).toBeVisible()
  expect(calls.find((call) => call.op === 'ReviewInstitutionDomain')?.variables).toEqual({ input: { domain: 'newcollege.edu', approve: true } })

  await page.goto('/admin/settings')
  const check = page.getByRole('switch', { name: 'Run the AI check' })
  await expect(check).toHaveAttribute('aria-checked', 'false')
  await check.click()
  await expect(check).toHaveAttribute('aria-checked', 'true')
  await expect.poll(() => calls.find((call) => call.op === 'UpdateAdminSetting')?.variables).toEqual({ input: { key: 'student_id_ai_check', value: 'true' } })
  await expect(page.getByLabel('Confidence threshold')).toHaveValue('80')
  await expect(page.getByLabel('Days to keep the card image')).toHaveValue('7')
})

test('errors group by type and open the people who hit them', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the list is the same')
  await mockApi(
    page,
    {
      AdminErrors: () => ({
        adminErrors: [
          {
            __typename: 'AdminErrorGroup',
            code: 'upload',
            sampleMessage: 'The file could not be uploaded. Storage refused it (403).',
            count: 12,
            firstSeen: '2026-10-01T08:00:00.000Z',
            lastSeen: '2026-10-25T09:00:00.000Z',
            userIds: [raviId],
          },
        ],
      }),
      UsersByIds: () => ({ usersByIds: [{ __typename: 'AdminUserLookup', id: raviId, displayName: 'Ravi Kumar', email: 'ravi@college.edu', globalRole: 'STUDENT' }] }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/errors')
  await expect(page.getByRole('heading', { name: 'Errors', level: 1 })).toBeVisible()
  await expect(page.getByText('The file could not be uploaded. Storage refused it (403).')).toBeVisible()
  await expect(page.getByText('12')).toBeVisible()
  await page.getByRole('button', { name: '1 person' }).click()
  await expect(page.getByRole('heading', { name: 'Affected people' })).toBeVisible()
  await expect(page.getByText('ravi@college.edu')).toBeVisible()
  await expect(page.getByText('STUDENT')).toBeVisible()
  await shot(page, 'admin_errors')
})

test('usage shows active people, top pages and one person’s timeline', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the figures are the same')
  const calls = await mockApi(
    page,
    {
      AdminUsage: () => ({
        adminUsage: {
          __typename: 'AdminUsage',
          dau: 128,
          wau: 640,
          mau: 2104,
          topFeatures: [
            { __typename: 'UsageCount', name: 'flashcards', count: 900 },
            { __typename: 'UsageCount', name: 'reader', count: 420 },
          ],
          topEvents: [
            { __typename: 'UsageCount', name: 'note_open', count: 300 },
            { __typename: 'UsageCount', name: 'search', count: 80 },
          ],
        },
      }),
      AdminUserActivity: () => ({
        adminUserActivity: [
          { __typename: 'UserActivityEvent', name: 'page_view', occurredAt: '2026-10-25T09:00:00.000Z', platform: 'WEB', props: null, appVersion: null },
          { __typename: 'UserActivityEvent', name: 'note_open', occurredAt: '2026-10-25T09:01:00.000Z', platform: 'WEB', props: { feature: 'reader' }, appVersion: null },
        ],
      }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/usage')
  await expect(page.getByText('128')).toBeVisible()
  await expect(page.getByText('640')).toBeVisible()
  await expect(page.getByText('2,104')).toBeVisible()
  await expect(page.getByText('flashcards', { exact: true })).toBeVisible()
  await expect(page.getByText('note_open')).toBeVisible()
  await page.getByPlaceholder('User id').fill(USER)
  await page.getByRole('button', { name: 'Show activity' }).click()
  await expect(page.getByText('page_view')).toBeVisible()
  await expect(page.getByText('WEB').first()).toBeVisible()
  expect(calls.find((call) => call.op === 'AdminUserActivity')?.variables).toEqual({ userId: USER, first: 50 })
  await shot(page, 'admin_usage')
})

test('an admin filters users, corrects a date of birth, and deletes only after typing DELETE', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the drawer is the same form')
  const asha = {
    __typename: 'AdminManagedUser',
    id: '01920000-0000-7000-8000-0000000000a1',
    displayName: 'Asha Rao',
    email: 'asha@example.com',
    handle: 'asharao',
    dateOfBirth: '2004-05-01',
    globalRole: 'STUDENT',
    accountStatus: 'ACTIVE',
    createdAt: '2026-01-01T00:00:00.000Z',
    statusReason: null,
  }
  let accounts = [
    {
      __typename: 'AdminManagedUser',
      id: raviId,
      displayName: 'Ravi Kumar',
      email: 'ravi@college.edu',
      handle: 'ravik',
      dateOfBirth: '2014-04-02',
      globalRole: 'STUDENT',
      accountStatus: 'AGE_BLOCKED',
      createdAt: '2026-10-01T00:00:00.000Z',
      statusReason: 'Date of birth is under the requirement.',
    },
    asha,
  ]
  const listed = (v: Record<string, unknown>) =>
    accounts.filter((account) => {
      const status = String(v.status ?? '')
      const inTab = status === 'BLOCKED_OR_SUSPENDED' ? account.accountStatus === 'BLOCKED' || account.accountStatus === 'SUSPENDED' : account.accountStatus === status
      if (!inTab) return false
      const term = String(v.search ?? '').trim().toLowerCase()
      return !term || account.displayName.toLowerCase().includes(term) || account.email.toLowerCase().includes(term)
    })
  const calls = await mockApi(
    page,
    {
      AdminUsers: (v) => {
        const users = listed(v)
        return { adminUsers: { __typename: 'AdminUserList', total: users.length, users } }
      },
      AdminUpdateUser: (v) => {
        const input = v.input as { userId: string; displayName: string; email: string; dateOfBirth: string }
        accounts = accounts.map((account) => (account.id === input.userId ? { ...account, displayName: input.displayName, email: input.email, dateOfBirth: input.dateOfBirth, accountStatus: 'ACTIVE', statusReason: null } : account))
        const user = accounts.find((row) => row.id === input.userId)
        return { adminUpdateUser: { __typename: 'AdminUserPayload', user, userErrors: [] } }
      },
      AdminSetAccountStanding: (v) => {
        const input = v.input as { userId: string; status: string; reason: string }
        accounts = accounts.map((account) => (account.id === input.userId ? { ...account, accountStatus: input.status, statusReason: input.reason } : account))
        const user = accounts.find((row) => row.id === input.userId)
        return { adminSetAccountStanding: { __typename: 'AdminUserPayload', user, userErrors: [] } }
      },
      AdminDeleteUser: (v) => {
        const input = v.input as { userId: string }
        accounts = accounts.filter((account) => account.id !== input.userId)
        return { adminDeleteUser: { __typename: 'OkPayload', ok: true, ...none } }
      },
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/users')
  await expect(page.getByRole('heading', { name: 'Users', level: 1 })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Age-blocked' })).toHaveAttribute('aria-pressed', 'true')
  await expect(page.getByRole('button', { name: 'Blocked or suspended' })).toBeVisible()
  await expect(page.getByText('1 account')).toBeVisible()
  await expect(page.getByText('ravi@college.edu')).toBeVisible()
  await expect(page.getByText('asha@example.com')).toHaveCount(0)
  await page.getByRole('textbox', { name: 'Search' }).fill('nobody')
  await expect(page.getByText('No accounts in this list.')).toBeVisible()
  await page.getByRole('textbox', { name: 'Search' }).fill('')
  await expect(page.getByText('ravi@college.edu')).toBeVisible()
  await page.getByRole('button', { name: 'Open' }).click()
  const drawer = page.getByRole('dialog', { name: 'Ravi Kumar' })
  await expect(drawer.getByText('Date of birth is under the requirement.')).toBeVisible()
  await drawer.getByLabel('Date of birth').fill('2004-04-02')
  await drawer.getByRole('button', { name: 'Save details' }).click()
  await expect(drawer.getByRole('alert')).toHaveText('Add a reason first.')
  await drawer.getByPlaceholder('Why you are making this change').first().fill('The date of birth was typed wrong.')
  await drawer.getByRole('button', { name: 'Save details' }).click()
  await expect(drawer.getByText('Age check: unblocked.')).toBeVisible()
  expect(calls.find((call) => call.op === 'AdminUpdateUser')?.variables).toMatchObject({
    input: { userId: raviId, dateOfBirth: '2004-04-02', displayName: 'Ravi Kumar', email: 'ravi@college.edu', reason: 'The date of birth was typed wrong.' },
  })
  await drawer.getByRole('button', { name: 'Block' }).click()
  await expect(drawer.getByRole('alert')).toHaveText('Add a reason first.')
  await drawer.getByPlaceholder('Why you are making this change').nth(1).fill('Asked to pause the account.')
  await drawer.getByRole('button', { name: 'Block' }).click()
  await expect(drawer.getByRole('button', { name: 'Unblock' })).toBeVisible()
  expect(calls.find((call) => call.op === 'AdminSetAccountStanding')?.variables).toMatchObject({
    input: { userId: raviId, status: 'BLOCKED', reason: 'Asked to pause the account.', until: null },
  })
  await drawer.getByRole('button', { name: 'Suspend', exact: true }).click()
  await expect(drawer.getByRole('alert')).toHaveText('Add when the suspension ends.')
  await drawer.getByLabel('Suspended until').fill('2026-12-01T09:00')
  await drawer.getByRole('button', { name: 'Suspend', exact: true }).click()
  await expect.poll(() => {
    const last = calls.filter((call) => call.op === 'AdminSetAccountStanding').at(-1)?.variables as { input?: { status?: string; until?: string } } | undefined
    return last?.input
  }).toMatchObject({ status: 'SUSPENDED', until: expect.stringContaining('2026-12-01') })
  const remove = drawer.getByRole('button', { name: 'Delete this user' })
  await expect(remove).toBeDisabled()
  await drawer.getByLabel('Type DELETE').fill('delete')
  await expect(remove).toBeDisabled()
  await drawer.getByLabel('Type DELETE').fill('DELETE')
  await drawer.getByPlaceholder('Why you are making this change').nth(2).fill('Duplicate account.')
  await expect(remove).toBeEnabled()
  await shot(page, 'admin_users')
  await remove.click()
  await expect(drawer).toBeHidden()
  await expect(page.getByText('ravi@college.edu')).toHaveCount(0)
  expect(calls.find((call) => call.op === 'AdminDeleteUser')?.variables).toEqual({
    input: { userId: raviId, confirm: 'DELETE', reason: 'Duplicate account.' },
  })
})

test('the profile can opt out of usage analytics', async ({ page }) => {
  const calls = await mockApi(page, { SetAnalyticsOptOut: () => ({ setAnalyticsOptOut: { __typename: 'OkPayload', ok: true, ...none } }) })
  await page.goto('/profile')
  const choice = page.getByRole('switch', { name: 'Usage analytics' })
  await expect(choice).toHaveAttribute('aria-checked', 'false')
  await choice.click()
  await expect(choice).toHaveAttribute('aria-checked', 'true')
  expect(calls.find((call) => call.op === 'SetAnalyticsOptOut')?.variables).toEqual({ optOut: true })
})
