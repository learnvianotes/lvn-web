import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * College ID verification (lvn-backend ADR-0099) against a mocked API: a student sends one card,
 * and a platform admin turns the option on, opens the card, and approves or rejects it.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const unverified = { ...viewerExtras, verified: false, verificationMethod: null }
const person = (id: string, displayName: string, handle: string) => ({ __typename: 'User', id, displayName, handle })
const ravi = person('01920000-0000-7000-8000-0000000000e2', 'Ravi Kumar', 'ravi')
const request = (over: Record<string, unknown> = {}) => ({
  __typename: 'StudentIdVerificationRequest',
  id: '01920000-0000-7000-8000-0000000id001',
  status: 'PENDING',
  reason: null,
  createdAt: new Date().toISOString(),
  decidedAt: null,
  requester: ravi,
  ...over,
})
const none = { userErrors: [] }
const basics = {
  MyDataExports: () => ({ myDataExports: [] }),
  NoteImports: () => ({ noteImports: [] }),
  MyVerificationRequests: () => ({ myVerificationRequests: [] }),
}
const on = { StudentIdVerificationEnabled: () => ({ studentIdVerificationEnabled: true }) }
const FILE_ID = '01920000-0000-7000-8000-00000000f0d1'

test('the option is hidden while college ID checks are off', async ({ page }) => {
  await mockApi(page, { ...basics, MyStudentIdVerification: () => ({ myStudentIdVerification: null }) }, unverified)
  await page.goto('/profile')
  await expect(page.getByRole('button', { name: 'Ask a teacher' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Send your college ID card' })).toHaveCount(0)
  await expect(page.getByLabel('Choose your ID card')).toHaveCount(0)
})

test('a restricted minor is not offered a college ID card', async ({ page }) => {
  await mockApi(page, { ...basics, ...on }, { ...unverified, restrictedMinor: true })
  await page.goto('/profile')
  await expect(page.getByRole('button', { name: 'Ask a teacher' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Send your college ID card' })).toHaveCount(0)
})

test('a student sends a college ID card and can withdraw it; completeUpload is not called', async ({ page }) => {
  let mine: unknown = null
  const puts: string[] = []
  await page.route('http://storage.test/**', async (route) => {
    if (route.request().method() === 'OPTIONS') return route.fulfill({ status: 204, headers: { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'PUT', 'access-control-allow-headers': '*' } })
    puts.push(route.request().headers()['content-type'] ?? '')
    return route.fulfill({ status: 200, headers: { 'access-control-allow-origin': '*' } })
  })
  const calls = await mockApi(
    page,
    {
      ...basics,
      ...on,
      MyStudentIdVerification: () => ({ myStudentIdVerification: mine }),
      CreateStudentIdUploadIntent: () => ({
        createStudentIdUploadIntent: {
          intent: { __typename: 'UploadIntent', fileId: FILE_ID, uploadUrl: 'http://storage.test/put', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: 'image/png' }] },
          ...none,
        },
      }),
      SubmitStudentIdVerification: () => ((mine = request()), { submitStudentIdVerification: { request: mine, ...none } }),
      WithdrawStudentIdVerification: () => ((mine = request({ status: 'WITHDRAWN' })), { withdrawStudentIdVerification: { ok: true, ...none } }),
    },
    unverified,
  )
  await page.goto('/profile')
  await page.getByRole('button', { name: 'Send your college ID card' }).click()
  await page.getByLabel('Choose your ID card').setInputFiles({ name: 'id-card.png', mimeType: 'image/png', buffer: Buffer.from('\x89PNG') })
  await expect(page.getByText('id-card.png')).toBeVisible()
  await page.getByRole('button', { name: 'Send to an admin' }).click()
  await expect(page.getByText('An admin is checking your college ID card.')).toBeVisible()
  expect(calls.find((c) => c.op === 'CreateStudentIdUploadIntent')?.variables).toEqual({ input: { fileName: 'id-card.png', mimeType: 'image/png', sizeBytes: 5 } })
  expect(puts).toEqual(['image/png'])
  expect(calls.find((c) => c.op === 'SubmitStudentIdVerification')?.variables).toEqual({ input: { fileId: FILE_ID } })
  expect(calls.some((c) => c.op === 'CompleteNoteUpload' || /completeUpload/.test(JSON.stringify(c)))).toBe(false)
  await page.getByRole('button', { name: 'Withdraw the request' }).click()
  await expect(page.getByRole('button', { name: 'Send your college ID card' })).toBeVisible()
  expect(calls.find((c) => c.op === 'WithdrawStudentIdVerification')?.variables).toEqual({ requestId: request().id })
})

test('a refusal is shown, and the wrong size, type, or limit is said plainly', async ({ page }) => {
  let outcome: { code: string; message: string } | null = null
  await mockApi(
    page,
    {
      ...basics,
      ...on,
      MyStudentIdVerification: () => ({ myStudentIdVerification: request({ status: 'REJECTED', reason: 'The name does not match.' }) }),
      CreateStudentIdUploadIntent: () => ({
        createStudentIdUploadIntent: { intent: null, userErrors: [{ __typename: 'UserError', field: null, code: outcome?.code, message: outcome?.message }] },
      }),
    },
    unverified,
  )
  await page.goto('/profile')
  await expect(page.getByText('Your college ID was not accepted: The name does not match.')).toBeVisible()
  await page.getByRole('button', { name: 'Send your college ID card' }).click()

  const alert = page.locator('p[role="alert"]')
  await page.getByLabel('Choose your ID card').setInputFiles({ name: 'huge.png', mimeType: 'image/png', buffer: Buffer.alloc(5 * 1024 * 1024 + 1) })
  await expect(alert).toHaveText('That file is over 5 MB.')

  await page.getByLabel('Choose your ID card').setInputFiles({ name: 'card.gif', mimeType: 'image/gif', buffer: Buffer.from('GIF') })
  await expect(alert).toHaveText('Use a JPEG, PNG, WebP or PDF.')

  const send = async (code: string, message: string, shown: string) => {
    outcome = { code, message }
    await page.getByLabel('Choose your ID card').setInputFiles({ name: 'id-card.png', mimeType: 'image/png', buffer: Buffer.from('\x89PNG') })
    await page.getByRole('button', { name: 'Send to an admin' }).click()
    await expect(alert).toHaveText(shown)
  }
  await send('UNAVAILABLE', 'UNAVAILABLE', 'College ID checks are turned off right now.')
  await send('RATE_LIMITED', 'You already have a request waiting.', 'You already have a college ID waiting. Withdraw it before sending another.')
  await send('RATE_LIMITED', 'Three cards in seven days.', 'You can send three college ID cards in seven days.')
})

test('a platform admin turns college ID checks on, opens a card on demand, and approves or rejects it', async ({ page, context }) => {
  let enabled = false
  let waiting = [request(), request({ id: '01920000-0000-7000-8000-0000000id002', requester: person('u3', 'Dev Patel', 'dev') })]
  let cardReads = 0
  await context.route('http://storage.test/**', (route) => {
    cardReads += 1
    return route.fulfill({ status: 200, body: 'png', headers: { 'content-type': 'image/png' } })
  })
  const calls = await mockApi(
    page,
    {
      ...basics,
      StudentIdVerificationEnabled: () => ({ studentIdVerificationEnabled: enabled }),
      SetStudentIdVerificationEnabled: (v) => ((enabled = (v.input as { enabled: boolean }).enabled), { setStudentIdVerificationEnabled: { settings: { __typename: 'StudentIdVerificationSettings', enabled }, ...none } }),
      StudentIdVerificationQueue: () => ({ studentIdVerificationQueue: waiting }),
      StudentIdCardUrl: () => ({ studentIdCardUrl: { __typename: 'SignedUrl', url: 'http://storage.test/card', expiresAt: new Date(Date.now() + 60_000).toISOString() } }),
      ReviewStudentIdVerification: (v) => {
        const input = v.input as { requestId: string; approve: boolean }
        waiting = waiting.filter((item) => item.id !== input.requestId)
        return { reviewStudentIdVerification: { request: { __typename: 'StudentIdVerificationRequest', id: input.requestId, status: input.approve ? 'APPROVED' : 'REJECTED' }, ...none } }
      },
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/admin/student-id')
  await expect(page.getByRole('switch', { name: 'Students can send a college ID card' })).not.toBeChecked()
  expect(calls.some((c) => c.op === 'StudentIdCardUrl')).toBe(false)
  expect(cardReads).toBe(0)

  await page.getByRole('switch', { name: 'Students can send a college ID card' }).click()
  await expect(page.getByRole('switch', { name: 'Students can send a college ID card' })).toBeChecked()
  expect(calls.find((c) => c.op === 'SetStudentIdVerificationEnabled')?.variables).toEqual({ input: { enabled: true } })

  const raviCard = page.getByRole('article', { name: 'Ravi Kumar' })
  await raviCard.getByRole('button', { name: 'View college ID card' }).click()
  await expect(raviCard.getByRole('link', { name: 'Open in a new tab' })).toHaveAttribute('href', 'http://storage.test/card')
  expect(calls.filter((c) => c.op === 'StudentIdCardUrl')).toEqual([{ op: 'StudentIdCardUrl', variables: { requestId: request().id } }])
  await raviCard.getByRole('button', { name: 'Approve' }).click()
  await expect(raviCard).toHaveCount(0)
  expect(calls.find((c) => c.op === 'ReviewStudentIdVerification')?.variables).toEqual({ input: { requestId: request().id, approve: true, reason: null } })

  const dev = page.getByRole('article', { name: 'Dev Patel' })
  await dev.getByLabel(/^Reason/).fill('The card is expired.')
  await dev.getByRole('button', { name: 'Reject' }).click()
  await expect(dev).toHaveCount(0)
  expect(calls.filter((c) => c.op === 'ReviewStudentIdVerification').at(-1)?.variables).toEqual({
    input: { requestId: '01920000-0000-7000-8000-0000000id002', approve: false, reason: 'The card is expired.' },
  })
})

test('the college ID page is for platform admins only', async ({ page }) => {
  const calls = await mockApi(page, basics, viewerExtras)
  await page.goto('/profile')
  await expect(page.getByRole('link', { name: 'College ID cards', exact: true })).toHaveCount(0)
  await page.goto('/admin/student-id')
  await expect(page.getByText('Only platform admins and verified teachers can review these.')).toBeVisible()
  expect(calls.some((c) => c.op === 'StudentIdVerificationQueue' || c.op === 'StudentIdCardUrl')).toBe(false)
})
