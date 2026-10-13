import { expect, test } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Becoming a teacher (lvn-backend ADR-0073), "try now, verify later": apply from Account; while waiting, set up classes
 * that say students can join once verified; admins see applications with where the person teaches.
 */
const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const CLASS = '01920000-0000-7000-8000-0000000c0001'
const me = { __typename: 'User', id: '01920000-0000-7000-8000-00000000aaaa', displayName: 'Asha Rao', handle: 'asharao' }
const application = (over: Record<string, unknown> = {}) => ({
  __typename: 'VerificationRequest', id: '01920000-0000-7000-8000-0000000ae001', purpose: 'TEACHER_ROLE', institution: 'Govt. Junior College, Guntur', subjects: 'Physics', method: 'DOCUMENTS',
  status: 'PENDING', message: null, reason: null, createdAt: new Date().toISOString(), decidedAt: null, requester: me, teacher: null, ...over,
})
const basics = { MyDataExports: () => ({ myDataExports: [] }), NoteImports: () => ({ noteImports: [] }), MyVerificationRequests: () => ({ myVerificationRequests: [] }) }

test('a student applies to teach from Account, and is told they can set up classes while waiting', async ({ page }) => {
  let status = 'NONE'
  let mine: unknown = null
  const calls = await mockApi(page, {
    ...basics,
    MyTeacherApplication: () => ({ myTeacherApplication: mine }),
    ApplyToTeach: () => {
      status = 'PENDING'
      mine = application()
      return { applyToTeach: { request: mine, userErrors: [] } }
    },
  }, { ...viewerExtras, get teacherStatus() { return status } })
  await page.goto('/profile')
  await page.getByRole('link', { name: /^Teach on LearnViaNotes/ }).click()
  await expect(page).toHaveURL(/\/teach$/)
  const form = page.getByRole('form', { name: 'Apply to teach' })
  await expect(form.getByRole('button', { name: 'Apply to teach' })).toBeDisabled()
  await form.getByLabel('Where you teach').fill('Govt. Junior College, Guntur')
  await form.getByLabel('What you teach (optional)').fill('Physics')
  await form.getByRole('button', { name: 'Apply to teach' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'ApplyToTeach')?.variables).toEqual({ input: { institution: 'Govt. Junior College, Guntur', subjects: 'Physics', message: null, fileIds: [] } })
  await expect(page.getByRole('heading', { name: 'Your application is being reviewed' })).toBeVisible()
  await expect(page.getByRole('link', { name: /Set up a class/ })).toHaveAttribute('href', '/classes')
})

test('a declined applicant reads why and may apply again; a verified teacher is told so', async ({ page }) => {
  await mockApi(page, { ...basics, MyTeacherApplication: () => ({ myTeacherApplication: application({ status: 'REJECTED', reason: 'We could not find you on the staff page.' }) }) }, { ...viewerExtras, teacherStatus: 'DECLINED' })
  await page.goto('/teach')
  await expect(page.getByText('We could not find you on the staff page. You can apply again.')).toBeVisible()
  await expect(page.getByRole('form', { name: 'Apply to teach' })).toBeVisible()
})

test('an applicant’s class says students can join once they are verified, and hides invites and requests', async ({ page }) => {
  const can = { __typename: 'ClassroomActions', requestJoin: false, acceptInvite: false, review: false, post: true, publishQuiz: true, manage: true, leave: false }
  await mockApi(page, {
    Classroom: () => ({ classroom: { __typename: 'Classroom', id: CLASS, name: 'Physics 11A', description: null, memberCount: 1, viewerRole: 'TEACHER', teacher: me, createdAt: '2026-10-13T10:00:00.000Z', joinCode: null, viewerRequestId: null, viewerInviteId: null, viewerCan: can } }),
    ClassroomPosts: () => ({ classroom: { __typename: 'Classroom', id: CLASS, posts: { __typename: 'ClassroomPostConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } }),
  }, { ...viewerExtras, teacherStatus: 'PENDING' })
  await page.goto(`/classes/${CLASS}`)
  await expect(page.getByRole('note')).toContainText('Students can join this class once you are verified as a teacher.')
  await expect(page.getByRole('tab', { name: 'Requests' })).toHaveCount(0)
  await expect(page.getByRole('tab', { name: 'People' })).toHaveCount(0)
})

test('admins see applications to teach with where the person teaches', async ({ page }) => {
  await mockApi(page, {
    ...basics,
    VerificationRequestsToReview: () => ({ verificationRequestsToReview: [{ ...application(), documents: [{ __typename: 'VerificationDocument', fileId: '01920000-0000-7000-8000-0000000f0001', fileName: 'appointment.pdf', mimeType: 'application/pdf', sizeBytes: 1000 }] }] }),
  }, { ...viewerExtras, globalRole: 'PLATFORM_ADMIN', verified: true })
  await page.goto('/admin/verification')
  const card = page.getByRole('article', { name: 'Asha Rao' })
  await expect(card.getByText('Applies to teach')).toBeVisible()
  await expect(card.getByText('Teaches at Govt. Junior College, Guntur · Physics')).toBeVisible()
  await expect(card.getByText('appointment.pdf')).toBeVisible()
})
