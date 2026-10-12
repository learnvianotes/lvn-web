import { expect, test } from '@playwright/test'
import { mockApi, NOTE_ID, USER } from './support/notes-api'

/** Classes (lvn-backend ADR-0046) against a mocked API: joining with a code or link, invites, announcements, staff tools. */

const CLASS = '01920000-0000-7000-8000-0000000c0001'
const TEACHER = '01920000-0000-7000-8000-00000000bbbb'
const PUPIL = '01920000-0000-7000-8000-00000000cccc'
const can = (over: Record<string, boolean> = {}) => ({ __typename: 'ClassroomActions', requestJoin: false, acceptInvite: false, review: false, post: false, manage: false, leave: false, ...over })
const teacherRef = { __typename: 'User', id: TEACHER, displayName: 'Meera Iyer' }
const classroom = (over: Record<string, unknown> = {}) => ({
  __typename: 'Classroom', id: CLASS, name: 'Physics 9A', description: 'Mechanics this term', memberCount: 31, viewerRole: null, teacher: teacherRef, createdAt: '2026-10-01T10:00:00.000Z',
  joinCode: null, viewerRequestId: null, viewerInviteId: null, viewerCan: can(), ...over,
})
const asTeacher = () => classroom({ viewerRole: 'TEACHER', teacher: { __typename: 'User', id: USER, displayName: 'Asha Rao' }, joinCode: 'K7PQ2MXA', viewerCan: can({ review: true, post: true, manage: true }) })
const asStudent = () => classroom({ viewerRole: 'STUDENT', viewerCan: can({ leave: true }) })
const doc = (s: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text: s }] }] })
const post = (id: string, text: string, over: Record<string, unknown> = {}) => ({ __typename: 'ClassroomPost', id, body: doc(text), createdAt: new Date().toISOString(), viewerCanDelete: false, author: { __typename: 'User', id: TEACHER, displayName: 'Meera Iyer', handle: 'meera' }, discussion: { __typename: 'Discussion', commentCount: 0 }, ...over })
const posts = (nodes: unknown[]) => ({ classroom: { __typename: 'Classroom', id: CLASS, posts: { __typename: 'ClassroomPostConnection', edges: nodes.map((node) => ({ __typename: 'ClassroomPostEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } } })
const card = (over: Record<string, unknown> = {}) => ({ __typename: 'Classroom', id: CLASS, name: 'Physics 9A', description: null, memberCount: 31, viewerRole: 'STUDENT', teacher: teacherRef, ...over })

test('a student sees their classes and invites, and answers an invite', async ({ page: p }) => {
  let invited = true
  const calls = await mockApi(p, {
    MyClassrooms: () => ({
      myClassrooms: invited ? [] : [card()],
      myClassroomInvites: invited ? [{ __typename: 'ClassroomInviteItem', id: 'inv1', role: 'STUDENT', expiresAt: '2026-10-26T10:00:00.000Z', classroom: { __typename: 'ClassroomPreview', id: CLASS, name: 'Physics 9A', teacher: teacherRef }, invitedBy: teacherRef }] : [],
    }),
    AnswerClassroomInvite: () => ((invited = false), { answerClassroomInvite: { __typename: 'ClassroomPayload', classroom: asStudent(), userErrors: [] } }),
  })
  await p.goto('/classes')
  await expect(p.getByRole('heading', { name: 'Classes', level: 1 })).toBeVisible()
  // Only teachers start classes.
  await expect(p.getByRole('button', { name: 'New class' })).toHaveCount(0)
  await expect(p.getByText('Meera Iyer invited you as Student')).toBeVisible()
  await p.getByRole('button', { name: 'Accept' }).click()
  await expect(p.getByRole('link', { name: /Physics 9A/ })).toHaveAttribute('href', `/classes/${CLASS}`)
  expect(calls.find((c) => c.op === 'AnswerClassroomInvite')?.variables).toEqual({ inviteId: 'inv1', accept: true })
})

test('a typed code shows the class by name and teacher only, and the student asks to join', async ({ page: p }) => {
  let asked = false
  const calls = await mockApi(p, {
    MyClassrooms: () => ({ myClassrooms: [], myClassroomInvites: [] }),
    ClassroomByCode: (v) => ({ classroomByCode: v.code === 'K7PQ2MXA' ? { __typename: 'ClassroomPreview', id: CLASS, name: 'Physics 9A', viewerRole: null, viewerRequestId: asked ? 'jr1' : null, teacher: teacherRef } : null }),
    RequestToJoinClassroom: () => ((asked = true), { requestToJoinClassroom: { __typename: 'ClassroomPayload', classroom: classroom({ viewerRequestId: 'jr1' }), userErrors: [] } }),
  })
  await p.goto('/classes')
  await p.getByLabel('Class code').fill('k7pq-2mxa')
  await p.getByRole('button', { name: 'Find' }).click()
  await expect(p).toHaveURL(/\/classes\/join\/K7PQ2MXA\?via=code$/)
  await expect(p.getByRole('heading', { name: 'Physics 9A' })).toBeVisible()
  await expect(p.getByText('Teacher: Meera Iyer')).toBeVisible()
  await p.getByRole('button', { name: 'Ask to join' }).click()
  await expect(p.getByText('Your request is waiting for your teacher.')).toBeVisible()
  expect(calls.find((c) => c.op === 'RequestToJoinClassroom')?.variables).toEqual({ code: 'K7PQ2MXA', via: 'CODE' })
})

test('the join link asks with the link; an unknown code says so', async ({ page: p }) => {
  const calls = await mockApi(p, {
    ClassroomByCode: (v) => ({ classroomByCode: v.code === 'K7PQ2MXA' ? { __typename: 'ClassroomPreview', id: CLASS, name: 'Physics 9A', viewerRole: null, viewerRequestId: null, teacher: teacherRef } : null }),
    RequestToJoinClassroom: () => ({ requestToJoinClassroom: { __typename: 'ClassroomPayload', classroom: classroom({ viewerRequestId: 'jr1' }), userErrors: [] } }),
  })
  await p.goto('/classes/join/k7pq2mxa')
  await p.getByRole('button', { name: 'Ask to join' }).click()
  await expect.poll(() => calls.find((c) => c.op === 'RequestToJoinClassroom')?.variables).toEqual({ code: 'K7PQ2MXA', via: 'LINK' })
  await p.goto('/classes/join/ZZZZZZZZ')
  await expect(p.getByText('No class has that code. Check it with your teacher.')).toBeVisible()
})

test('a student reads announcements and notes; staff tools and the code stay hidden', async ({ page: p }) => {
  await mockApi(p, {
    Classroom: () => ({ classroom: asStudent() }),
    ClassroomPosts: () => posts([post('p1', 'Test on Friday')]),
    ClassroomNotes: () => ({ classroom: { __typename: 'Classroom', id: CLASS, sharedNotes: { __typename: 'NoteConnection', edges: [{ __typename: 'NoteEdge', node: { __typename: 'Note', id: NOTE_ID, title: 'Kinematics summary', publishedAt: '2026-10-10T10:00:00.000Z', owner: teacherRef } }] } } }),
  })
  await p.goto(`/classes/${CLASS}`)
  await expect(p.getByRole('heading', { name: 'Physics 9A' })).toBeVisible()
  await expect(p.getByRole('tabpanel')).toContainText('Test on Friday')
  await expect(p.getByLabel('Write an announcement')).toHaveCount(0)
  await expect(p.getByRole('button', { name: 'Delete announcement' })).toHaveCount(0)
  await expect(p.getByRole('tab')).toHaveText(['Announcements', 'Notes'])
  await expect(p.getByTestId('class-code')).toHaveCount(0)
  await p.getByRole('tab', { name: 'Notes' }).click()
  await expect(p.getByRole('link', { name: /Kinematics summary/ })).toHaveAttribute('href', `/notes/${NOTE_ID}`)
  await expect(p.getByLabel('Share one of your notes with the class')).toHaveCount(0)
})

test('the teacher starts a class, sees its code, and posts an announcement', async ({ page: p }) => {
  let list: unknown[] = []
  const calls = await mockApi(
    p,
    {
      MyClassrooms: () => ({ myClassrooms: [], myClassroomInvites: [] }),
      CreateClassroom: () => ({ createClassroom: { __typename: 'ClassroomPayload', classroom: asTeacher(), userErrors: [] } }),
      Classroom: () => ({ classroom: asTeacher() }),
      ClassroomPosts: () => posts(list),
      CreateClassroomPost: () => ((list = [post('p9', 'Test on Friday', { viewerCanDelete: true, author: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' } })]), { createClassroomPost: { __typename: 'ClassroomPayload', classroom: { __typename: 'Classroom', id: CLASS }, userErrors: [] } }),
    },
    { globalRole: 'TEACHER' },
  )
  await p.goto('/classes')
  await p.getByRole('button', { name: 'New class' }).click()
  const dialog = p.getByRole('dialog', { name: 'New class' })
  await dialog.getByLabel('Name').fill('Physics 9A')
  await dialog.getByRole('button', { name: 'Create class' }).click()
  await expect(p).toHaveURL(new RegExp(`/classes/${CLASS}$`))
  await expect(p.getByTestId('class-code')).toHaveText('K7PQ2MXA')
  await expect(p.getByRole('tab')).toHaveText(['Announcements', 'Notes', 'People', 'Requests', 'Settings'])
  await p.getByLabel('Write an announcement').fill('Test on Friday')
  await p.getByRole('button', { name: 'Post', exact: true }).click()
  await expect(p.getByRole('tabpanel')).toContainText('Test on Friday')
  await expect(p.getByRole('button', { name: 'Delete announcement' })).toBeVisible()
  expect(calls.find((c) => c.op === 'CreateClassroom')?.variables).toEqual({ input: { name: 'Physics 9A', description: null } })
  expect(calls.find((c) => c.op === 'CreateClassroomPost')?.variables).toEqual({ classroomId: CLASS, body: doc('Test on Friday') })
})

test('staff let students in, invite a TA, and hand the class over only after confirming', async ({ page: p }) => {
  let pending = true
  const member = (id: string, name: string, role: string) => ({ __typename: 'ClassroomMember', role, joinedAt: '2026-10-01T10:00:00.000Z', user: { __typename: 'User', id, displayName: name, handle: name.split(' ')[0]!.toLowerCase() } })
  const calls = await mockApi(
    p,
    {
      Classroom: () => ({ classroom: asTeacher() }),
      ClassroomPosts: () => posts([]),
      ClassroomPeople: () => ({
        classroom: {
          __typename: 'Classroom', id: CLASS, viewerRole: 'TEACHER',
          members: [member(USER, 'Asha Rao', 'TEACHER'), member(PUPIL, 'Ravi Kumar', 'STUDENT')],
          joinRequests: pending ? [{ __typename: 'ClassroomJoinRequest', id: 'jr1', via: 'CODE', createdAt: new Date().toISOString(), user: { __typename: 'User', id: '01920000-0000-7000-8000-00000000dddd', displayName: 'Kiran Das', handle: 'kiran' } }] : [],
        },
      }),
      ReviewClassroomJoinRequest: () => ((pending = false), { reviewClassroomJoinRequest: { __typename: 'ClassroomPayload', classroom: { __typename: 'Classroom', id: CLASS, memberCount: 32 }, userErrors: [] } }),
      InviteToClassroom: () => ({ inviteToClassroom: { __typename: 'ClassroomPayload', classroom: { __typename: 'Classroom', id: CLASS }, userErrors: [] } }),
      SetClassroomRole: () => ({ setClassroomRole: { __typename: 'ClassroomPayload', classroom: asTeacher(), userErrors: [] } }),
    },
    { globalRole: 'TEACHER' },
  )
  await p.goto(`/classes/${CLASS}`)
  await p.getByRole('tab', { name: 'Requests' }).click()
  await expect(p.getByText('Kiran Das')).toBeVisible()
  await expect(p.getByText(/with the code/)).toBeVisible()
  await p.getByRole('button', { name: 'Let in' }).click()
  await expect(p.getByText('No requests waiting.')).toBeVisible()
  expect(calls.find((c) => c.op === 'ReviewClassroomJoinRequest')?.variables).toEqual({ requestId: 'jr1', decision: 'APPROVED' })

  await p.getByRole('tab', { name: 'People' }).click()
  await p.getByLabel('Handle or email').fill('@priya')
  await p.getByLabel('Invite as').selectOption('TA')
  await p.getByRole('button', { name: 'Invite', exact: true }).click()
  await expect(p.getByText('Invite sent. It lasts 14 days.')).toBeVisible()
  expect(calls.find((c) => c.op === 'InviteToClassroom')?.variables).toEqual({ classroomId: CLASS, person: '@priya', role: 'TA' })
  // The teacher's own row has no controls; handing over asks first, and nothing happens on "cancel".
  await expect(p.getByLabel('Role of Asha Rao')).toHaveCount(0)
  p.once('dialog', (d) => void d.dismiss())
  await p.getByLabel('Role of Ravi Kumar').selectOption({ label: 'Hand the class to Ravi Kumar' })
  expect(calls.filter((c) => c.op === 'SetClassroomRole')).toEqual([])
  await p.getByLabel('Role of Ravi Kumar').selectOption('TA')
  await expect.poll(() => calls.find((c) => c.op === 'SetClassroomRole')?.variables).toEqual({ classroomId: CLASS, userId: PUPIL, role: 'TA' })
})
