import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { STUDENT_ID_MAX_BYTES, studentIdErrorMessage, studentIdFileProblem, studentIdMime, type StudentIdErrorCopy } from '@/features/verification/student-id'

const copy: StudentIdErrorCopy = {
  unavailable: 'off',
  pending: 'one waiting',
  week: 'three in seven days',
  eitherLimit: 'one waiting, or three in seven days',
  tooBig: 'over 5 MB',
  wrongType: 'jpeg png webp pdf',
  failed: 'failed',
}

const file = (over: Partial<{ name: string; type: string; size: number }> = {}) => ({ name: 'card.png', type: 'image/png', size: 100, ...over })

describe('college ID card files (ADR-0099)', () => {
  it('accepts a JPEG, PNG, WebP or PDF of at most 5 MB, including a blank browser type', () => {
    expect(studentIdFileProblem(file())).toBeNull()
    expect(studentIdFileProblem(file({ type: 'image/jpeg', name: 'a.jpg' }))).toBeNull()
    expect(studentIdFileProblem(file({ type: 'image/webp', name: 'a.webp' }))).toBeNull()
    expect(studentIdFileProblem(file({ type: 'application/pdf', name: 'a.pdf' }))).toBeNull()
    expect(studentIdFileProblem(file({ type: '', name: 'scan.JPG' }))).toBeNull()
    expect(studentIdMime(file({ type: 'image/jpg', name: 'a.jpg' }))).toBe('image/jpeg')
    expect(studentIdFileProblem(file({ size: STUDENT_ID_MAX_BYTES }))).toBeNull()
  })

  it('refuses the wrong type, an empty file, and anything over 5 MB', () => {
    expect(studentIdFileProblem(file({ type: 'image/gif', name: 'card.gif' }))).toBe('type')
    expect(studentIdFileProblem(file({ type: '', name: 'notes.txt' }))).toBe('type')
    expect(studentIdFileProblem(file({ size: 0 }))).toBe('empty')
    expect(studentIdFileProblem(file({ size: STUDENT_ID_MAX_BYTES + 1 }))).toBe('size')
  })
})

describe('college ID errors', () => {
  it('says when the option is off, and which rate limit was hit', () => {
    expect(studentIdErrorMessage({ code: 'UNAVAILABLE', message: 'UNAVAILABLE' }, copy)).toBe('off')
    expect(studentIdErrorMessage({ code: 'RATE_LIMITED', message: 'You already have a request waiting.' }, copy)).toBe('one waiting')
    expect(studentIdErrorMessage({ code: 'RATE_LIMITED', message: 'Three cards in seven days.' }, copy)).toBe('three in seven days')
    expect(studentIdErrorMessage({ code: 'RATE_LIMITED', message: '' }, copy)).toBe('one waiting, or three in seven days')
  })

  it('says whether the file is the wrong type or too big', () => {
    expect(studentIdErrorMessage({ code: 'VALIDATION', message: 'file is too large' }, copy)).toBe('over 5 MB')
    expect(studentIdErrorMessage({ code: 'VALIDATION', message: 'unsupported mime type' }, copy)).toBe('jpeg png webp pdf')
    expect(studentIdErrorMessage({ code: 'VALIDATION', message: 'The name is missing.' }, copy)).toBe('The name is missing.')
    expect(studentIdErrorMessage({ code: 'INTERNAL', message: 'INTERNAL' }, copy)).toBe('failed')
  })
})

const code = (src: string) => src.replace(/\/\*[\s\S]*?\*\//g, '').replace(/^#.*$/gm, '')

describe('the college ID upload does not call completeUpload', () => {
  it('puts the bytes and submits them', () => {
    const operation = code(readFileSync('graphql/operations/student-id.graphql', 'utf8'))
    const form = code(readFileSync('features/verification/CollegeIdOption.tsx', 'utf8'))
    expect(operation).toMatch(/submitStudentIdVerification/)
    expect(operation).not.toMatch(/completeUpload/)
    expect(form).toMatch(/SubmitStudentIdVerificationDocument/)
    expect(form).toMatch(/CreateStudentIdUploadIntentDocument/)
    expect(form).not.toMatch(/completeUpload|CompleteNoteUpload/)
  })

  it('opens the card on demand and does not keep the URL', () => {
    const admin = readFileSync('features/verification/StudentIdAdmin.tsx', 'utf8')
    const api = readFileSync('lib/platform-api.ts', 'utf8')
    expect(api).toMatch(/fetchPolicy:\s*'no-cache'/)
    expect(admin).toMatch(/studentIdCardUrl\(item\.id\)/)
    expect(admin).not.toMatch(/useQuery\(StudentIdCardUrl/)
    expect(admin).not.toMatch(/<img/)
  })
})
