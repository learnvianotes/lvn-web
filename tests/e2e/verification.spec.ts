import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Verifying without a college email (lvn-backend ADR-0019): a student asks a teacher to vouch or sends proof of
 * study; the teacher answers on their account page; platform admins check documents through recorded links.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const unverified = { ...viewerExtras, verified: false, verificationMethod: null }
const person = (id: string, displayName: string, handle: string) => ({ __typename: 'User', id, displayName, handle })
const meera = person('01920000-0000-7000-8000-0000000000e1', 'Meera Iyer', 'meera')
const ravi = person('01920000-0000-7000-8000-0000000000e2', 'Ravi Kumar', 'ravi')
const request = (over: Record<string, unknown> = {}) => ({ __typename: 'VerificationRequest', id: '01920000-0000-7000-8000-0000000ve001', purpose: 'ACCOUNT', institution: null, subjects: null, method: 'TEACHER', status: 'PENDING', message: null, reason: null, createdAt: new Date().toISOString(), decidedAt: null, requester: ravi, teacher: meera, ...over })
const none = { userErrors: [] }
const basics = { MyDataExports: () => ({ myDataExports: [] }), NoteImports: () => ({ noteImports: [] }) }

test('a student asks a teacher to vouch, and can withdraw while it waits', async ({ page }) => {
  let mine: unknown[] = []
  const calls = await mockApi(
    page,
    {
      ...basics,
      MyVerificationRequests: () => ({ myVerificationRequests: mine }),
      FindTeachers: () => ({ search: { __typename: 'SearchResults', people: [{ ...meera, globalRole: 'TEACHER' }, { ...person('s1', 'Meera Student', 'meeras'), globalRole: 'STUDENT' }] } }),
      RequestTeacherVerification: () => ((mine = [request({ message: 'Section B' })]), { requestTeacherVerification: { request: mine[0], ...none } }),
      WithdrawVerificationRequest: () => ((mine = [request({ status: 'WITHDRAWN' })]), { withdrawVerificationRequest: { ok: true, ...none } }),
    },
    unverified,
  )
  await page.goto('/profile')
  await page.getByRole('button', { name: 'Ask a teacher' }).click()
  await page.getByLabel('Find your teacher').fill('meera')
  // Only verified teachers can vouch: a student of the same name is not offered.
  await expect(page.getByRole('button', { name: /Meera Student/ })).toHaveCount(0)
  await page.getByRole('button', { name: /Meera Iyer/ }).click()
  await page.getByLabel('A note (optional)').fill('Section B')
  await page.getByRole('button', { name: 'Send request' }).click()
  await expect(page.getByText('Waiting for Meera Iyer to vouch for you.')).toBeVisible()
  expect(calls.find((c) => c.op === 'RequestTeacherVerification')?.variables).toEqual({ input: { teacherId: meera.id, message: 'Section B' } })
  await page.getByRole('button', { name: 'Withdraw the request' }).click()
  await expect(page.getByRole('button', { name: 'Ask a teacher' })).toBeVisible()
  expect(calls.find((c) => c.op === 'WithdrawVerificationRequest')?.variables).toEqual({ requestId: request().id })
})

test('a student sends proof of study, after a refusal that said why', async ({ page }) => {
  let mine: unknown[] = [request({ method: 'DOCUMENTS', status: 'REJECTED', teacher: null, reason: 'The ID card is from another college.' })]
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
      MyVerificationRequests: () => ({ myVerificationRequests: mine }),
      CreateNoteUpload: () => ({ createUploadIntent: { intent: { __typename: 'UploadIntent', fileId: '01920000-0000-7000-8000-00000000f0d1', uploadUrl: 'http://storage.test/put', uploadHeaders: [{ __typename: 'UploadHeader', name: 'content-type', value: 'image/png' }] }, ...none } }),
      CompleteNoteUpload: () => ({ completeUpload: { ok: true, ...none } }),
      RequestDocumentVerification: () => ((mine = [request({ method: 'DOCUMENTS', teacher: null }), ...mine]), { requestDocumentVerification: { request: mine[0], ...none } }),
    },
    unverified,
  )
  await page.goto('/profile')
  await expect(page.getByText('Your last request was not accepted: The ID card is from another college.')).toBeVisible()
  await page.getByRole('button', { name: 'Send proof of study' }).click()
  await page.getByLabel('Choose files').setInputFiles({ name: 'id-card.png', mimeType: 'image/png', buffer: Buffer.from('\x89PNG') })
  await expect(page.getByText('id-card.png')).toBeVisible()
  await page.getByRole('button', { name: 'Send request' }).click()
  await expect(page.getByText('Our team is checking your documents.')).toBeVisible()
  expect(calls.find((c) => c.op === 'CreateNoteUpload')?.variables).toEqual({ input: { fileName: 'id-card.png', mimeType: 'image/png', sizeBytes: 5, purpose: 'VERIFICATION_DOCUMENT' } })
  expect(puts).toEqual(['image/png'])
  expect(calls.find((c) => c.op === 'RequestDocumentVerification')?.variables).toEqual({ input: { fileIds: ['01920000-0000-7000-8000-00000000f0d1'], message: null } })
})

test('a restricted minor is offered a teacher only', async ({ page }) => {
  await mockApi(page, { ...basics, MyVerificationRequests: () => ({ myVerificationRequests: [] }) }, { ...unverified, restrictedMinor: true })
  await page.goto('/profile')
  await expect(page.getByRole('button', { name: 'Ask a teacher' })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Send proof of study' })).toHaveCount(0)
})

test('a teacher verifies a student who asked, and must say why to decline', async ({ page }) => {
  let waiting = [request({ message: 'I am in your Data Structures class.' }), request({ id: '01920000-0000-7000-8000-0000000ve002', requester: person('u3', 'Dev Patel', 'dev') })]
  const calls = await mockApi(
    page,
    {
      ...basics,
      VerificationRequestsToReview: () => ({ verificationRequestsToReview: waiting.map((r) => ({ ...r, documents: [] })) }),
      ReviewVerificationRequest: (v) => ((waiting = waiting.filter((r) => r.id !== (v.input as { requestId: string }).requestId)), { reviewVerificationRequest: { request: null, ...none } }),
    },
    { ...viewerExtras, globalRole: 'TEACHER' },
  )
  await page.goto('/profile')
  const raviCard = page.getByRole('article', { name: 'Ravi Kumar' })
  await expect(raviCard.getByText('I am in your Data Structures class.')).toBeVisible()
  await raviCard.getByRole('button', { name: 'Verify' }).click()
  await expect(raviCard).toHaveCount(0)
  expect(calls.find((c) => c.op === 'ReviewVerificationRequest')?.variables).toEqual({ input: { requestId: request().id, approve: true, reason: null } })
  const dev = page.getByRole('article', { name: 'Dev Patel' })
  await dev.getByRole('button', { name: 'Decline' }).click()
  await expect(dev.getByRole('alert')).toHaveText('Tell the student why, so they can try again.')
  await dev.getByLabel(/^Reason/).fill('I do not teach you.')
  await dev.getByRole('button', { name: 'Decline' }).click()
  await expect(page.getByRole('heading', { name: 'Students asking you to verify them' })).toHaveCount(0)
})

test('platform admins open proof of study through a recorded link and verify', async ({ page, context }) => {
  const docs = { ...request({ method: 'DOCUMENTS', teacher: null }), documents: [{ __typename: 'VerificationDocument', fileId: '01920000-0000-7000-8000-00000000f0d1', fileName: 'id-card.png', mimeType: 'image/png', sizeBytes: 4 }] }
  await context.route('http://storage.test/**', (route) => route.fulfill({ status: 200, body: 'png', headers: { 'content-type': 'image/png' } }))
  const calls = await mockApi(
    page,
    {
      ...basics,
      VerificationRequestsToReview: () => ({ verificationRequestsToReview: [docs] }),
      VerificationDocumentUrl: () => ({ verificationDocumentUrl: { __typename: 'SignedUrl', url: 'http://storage.test/doc', expiresAt: new Date(Date.now() + 900_000).toISOString() } }),
      ReviewVerificationRequest: () => ({ reviewVerificationRequest: { request: null, ...none } }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
  await page.goto('/profile')
  await page.getByRole('link', { name: /Proof of study to review/ }).click()
  await expect(page).toHaveURL(/\/admin\/verification$/)
  const card = page.getByRole('article', { name: 'Ravi Kumar' })
  const popup = page.waitForEvent('popup')
  await card.getByRole('button', { name: 'id-card.png' }).click()
  expect((await popup).url()).toBe('http://storage.test/doc')
  expect(calls.find((c) => c.op === 'VerificationDocumentUrl')?.variables).toEqual({ requestId: docs.id, fileId: docs.documents[0]!.fileId })
  await card.getByRole('button', { name: 'Verify' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'ReviewVerificationRequest')?.variables).toEqual({ input: { requestId: docs.id, approve: true, reason: null } })
})
