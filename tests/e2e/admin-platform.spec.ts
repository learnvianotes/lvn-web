import { deflateSync } from 'node:zlib'
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

function crc32(buf: Buffer): number {
  let c = ~0
  for (const byte of buf) {
    c ^= byte
    for (let i = 0; i < 8; i++) c = (c >>> 1) ^ (0xedb88320 & -(c & 1))
  }
  return ~c >>> 0
}

function chunk(type: string, data: Buffer): Buffer {
  const body = Buffer.concat([Buffer.from(type), data])
  const out = Buffer.alloc(8 + body.length)
  out.writeUInt32BE(data.length, 0)
  body.copy(out, 4)
  out.writeUInt32BE(crc32(body), 4 + body.length)
  return out
}

/** A small college-ID stand-in, so the review thumbnail paints in a screenshot. */
function cardPng(width = 240, height = 140): Buffer {
  const raw = Buffer.alloc((width * 4 + 1) * height)
  for (let y = 0; y < height; y++) {
    const row = y * (width * 4 + 1)
    raw[row] = 0
    for (let x = 0; x < width; x++) {
      const i = row + 1 + x * 4
      const band = y < 36
      raw[i] = band ? 15 : 232
      raw[i + 1] = band ? 118 : 244
      raw[i + 2] = band ? 110 : 248
      raw[i + 3] = 255
    }
  }
  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(width, 0)
  ihdr.writeUInt32BE(height, 4)
  ihdr[8] = 8
  ihdr[9] = 6
  return Buffer.concat([Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]), chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw)), chunk('IEND', Buffer.alloc(0))])
}

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
  aiVerdict: 'MATCH',
  aiConfidence: 0.82,
  aiReason: 'The name and college on the card match the profile.',
  aiExtracted: { __typename: 'AiExtractedId', name: 'Ravi Kumar', institution: 'IIT Hyderabad', idNumberPresent: true },
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

test('a manager reviews proof, and only sees the admin sections they are allowed', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'desktop shows the admin sidebar beside the card')
  await page.route('http://storage.test/**', (route) => route.fulfill({ status: 200, body: cardPng(), headers: { 'content-type': 'image/png' } }))
  await mockApi(
    page,
    { VerificationRequestsToReview: () => ({ verificationRequestsToReview: [reviewRequest] }), VerificationDocumentUrl: () => ({ verificationDocumentUrl: { __typename: 'SignedUrl', url: 'http://storage.test/doc', expiresAt: '2026-10-25T12:00:00.000Z' } }) },
    { ...viewerExtras, globalRole: 'MANAGER' },
  )
  await page.goto('/admin/verification')
  const nav = page.getByRole('navigation', { name: 'Admin settings' })
  await expect(nav.getByRole('link', { name: 'Errors' })).toBeVisible()
  await expect(nav.getByRole('link', { name: 'Usage' })).toBeVisible()
  await expect(nav.getByRole('link', { name: 'Proof of study to review' })).toBeVisible()
  await expect(nav.getByRole('link', { name: 'College ID cards' })).toBeVisible()
  await expect(nav.getByRole('link', { name: 'Roles' })).toHaveCount(0)
  await expect(nav.getByRole('link', { name: 'Overview' })).toHaveCount(0)

  const card = page.getByRole('article', { name: 'Ravi Kumar' })
  await expect(card.getByText('MATCH', { exact: true })).toBeVisible()
  await expect(card.getByText('82% confidence')).toBeVisible()
  await expect(card.getByText('The name and college on the card match the profile.')).toBeVisible()
  await expect(card.getByText('matches the profile').first()).toBeVisible()
  await card.getByRole('button', { name: 'id-card.png' }).click()
  await expect(card.getByRole('img', { name: 'id-card.png' })).toBeVisible()
  await expect(card.getByRole('link', { name: 'Open in a new tab' })).toHaveAttribute('href', 'http://storage.test/doc')
  await shot(page, 'review_card')
})

test('a teacher sees the review sections and cannot assign roles', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the sections are the same list')
  await mockApi(page, { VerificationRequestsToReview: () => ({ verificationRequestsToReview: [] }) }, { ...viewerExtras, globalRole: 'TEACHER' })
  await page.goto('/admin/verification')
  const nav = page.getByRole('navigation', { name: 'Admin settings' })
  await expect(nav.getByRole('link')).toHaveText(['Proof of study to review', 'College ID cards'])
  await page.goto('/admin/roles')
  await expect(page.getByText('Only platform admins can assign roles.')).toBeVisible()
})

test('an admin assigns a role, decides a domain, and turns on the ID-card check', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the forms are the same')
  let domains = [{ __typename: 'DomainReview', domain: 'newcollege.edu', status: 'NEEDS_REVIEW', requests: 4, firstSeenAt: '2026-10-01T00:00:00.000Z' }]
  let ai = { aiCheckEnabled: false, autoApproveOnHighConfidence: false }
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
      SetStaffRole: () => ({ setGlobalRole: { __typename: 'OkPayload', ok: true, ...none } }),
      InstitutionDomains: () => ({ domainReviews: domains }),
      DecideInstitutionDomain: (v) => {
        const input = v.input as { domain: string; approve: boolean }
        domains = domains.map((row) => (row.domain === input.domain ? { ...row, status: input.approve ? 'APPROVED' : 'REJECTED' } : row))
        return { decideDomainReview: { __typename: 'OkPayload', ok: true, ...none } }
      },
      AdminSettings: () => ({
        adminSettings: [
          {
            __typename: 'AdminSetting',
            key: 'uploads_enabled',
            type: 'BOOLEAN',
            category: 'uploads',
            description: 'Allow files to be uploaded.',
            value: 'true',
            overridden: false,
            updatedAt: '2026-10-01T00:00:00.000Z',
            constraints: { __typename: 'AdminSettingConstraints', min: null, max: null, maxLength: null, pattern: null, nullable: false },
          },
        ],
      }),
      AiVerificationSettings: () => ({ aiVerificationSettings: { __typename: 'AiVerificationSettings', ...ai } }),
      UpdateAiVerificationSettings: (v) => {
        ai = v.input as typeof ai
        return { updateAiVerificationSettings: { __typename: 'AiVerificationSettingsPayload', settings: { __typename: 'AiVerificationSettings', ...ai }, ...none } }
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
  expect(calls.find((call) => call.op === 'SetStaffRole')?.variables).toEqual({ input: { userId: raviId, role: 'MANAGER' } })

  await page.goto('/admin/domains')
  await expect(page.getByText('newcollege.edu')).toBeVisible()
  await page.getByRole('button', { name: 'Approve' }).click()
  await expect(page.getByText('No domains are waiting.')).toBeVisible()
  await expect(page.getByRole('list').getByText('newcollege.edu')).toBeVisible()
  expect(calls.find((call) => call.op === 'DecideInstitutionDomain')?.variables).toEqual({ input: { domain: 'newcollege.edu', approve: true } })

  await page.goto('/admin/settings')
  const check = page.getByRole('switch', { name: 'Run the AI check' })
  await expect(check).toHaveAttribute('aria-checked', 'false')
  await check.click()
  await expect(check).toHaveAttribute('aria-checked', 'true')
  await expect.poll(() => calls.find((call) => call.op === 'UpdateAiVerificationSettings')?.variables).toEqual({ input: { aiCheckEnabled: true, autoApproveOnHighConfidence: false } })
})

test('errors group by type and open the people who hit them', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'the list is the same')
  await mockApi(
    page,
    {
      AdminErrors: () => ({
        adminErrors: [
          {
            __typename: 'ErrorGroup',
            fingerprint: 'upload-403',
            type: 'upload',
            message: 'The file could not be uploaded. Storage refused it (403).',
            count: 12,
            firstSeen: '2026-10-01T08:00:00.000Z',
            lastSeen: '2026-10-25T09:00:00.000Z',
            trend: [1, 2, 4, 8, 12],
            affectedUserIds: [raviId],
            affectedUsers: [{ __typename: 'AffectedUser', userId: raviId, lastSeen: '2026-10-25T09:00:00.000Z' }],
          },
        ],
      }),
      UsersByIds: () => ({ usersByIds: [{ __typename: 'User', id: raviId, displayName: 'Ravi Kumar', email: 'ravi@college.edu', handle: 'ravi', globalRole: 'STUDENT' }] }),
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
          topPages: [
            { __typename: 'UsageCount', name: '/home', count: 900 },
            { __typename: 'UsageCount', name: '/notes', count: 420 },
          ],
          topEvents: [
            { __typename: 'UsageCount', name: 'note_open', count: 300 },
            { __typename: 'UsageCount', name: 'search', count: 80 },
          ],
        },
      }),
      AdminUserTimeline: () => ({
        adminUserTimeline: [
          { __typename: 'TimelineEntry', id: '01920000-0000-7000-8000-00000000e101', name: 'page_view', at: '2026-10-25T09:00:00.000Z', path: '/home' },
          { __typename: 'TimelineEntry', id: '01920000-0000-7000-8000-00000000e102', name: 'note_open', at: '2026-10-25T09:01:00.000Z', path: '/notes/abc' },
        ],
      }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/usage')
  await expect(page.getByText('128')).toBeVisible()
  await expect(page.getByText('640')).toBeVisible()
  await expect(page.getByText('2,104')).toBeVisible()
  await expect(page.getByText('/home')).toBeVisible()
  await expect(page.getByText('note_open')).toBeVisible()
  await page.getByPlaceholder('User id').fill(USER)
  await page.getByRole('button', { name: 'Show activity' }).click()
  await expect(page.getByText('/notes/abc')).toBeVisible()
  expect(calls.find((call) => call.op === 'AdminUserTimeline')?.variables).toEqual({ userId: USER })
  await shot(page, 'admin_usage')
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
