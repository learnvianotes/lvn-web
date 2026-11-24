/**
 * College ID cards (lvn-backend ADR-0099). One JPEG, PNG, WebP or PDF, at most 5 MB.
 * The upload is createStudentIdUploadIntent, a PUT, then submitStudentIdVerification — never completeUpload.
 */

/** Platform-admin review. Listed in the admin sidebar (`ADMIN_SECTIONS`) and on the account page. */
export const STUDENT_ID_ADMIN_PATH = '/admin/student-id'

export const STUDENT_ID_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'application/pdf'] as const
/** 5 MB, the limit the API enforces. */
export const STUDENT_ID_MAX_BYTES = 5 * 1024 * 1024

const BY_EXTENSION: Record<string, string> = {
  jpg: 'image/jpeg',
  jpeg: 'image/jpeg',
  png: 'image/png',
  webp: 'image/webp',
  pdf: 'application/pdf',
}

export type StudentIdFile = { name: string; type: string; size: number }
export type StudentIdFileProblem = 'type' | 'size' | 'empty'

/** The MIME type the API wants. Browsers leave some files blank or say image/jpg. */
export function studentIdMime(file: Pick<StudentIdFile, 'name' | 'type'>): string {
  const type = file.type === 'image/jpg' ? 'image/jpeg' : file.type
  if ((STUDENT_ID_TYPES as readonly string[]).includes(type)) return type
  return BY_EXTENSION[file.name.split('.').pop()?.toLowerCase() ?? ''] ?? type
}

/** Null when the file may be sent. Checked before the API is asked. */
export function studentIdFileProblem(file: StudentIdFile): StudentIdFileProblem | null {
  if (file.size <= 0) return 'empty'
  if (!(STUDENT_ID_TYPES as readonly string[]).includes(studentIdMime(file))) return 'type'
  if (file.size > STUDENT_ID_MAX_BYTES) return 'size'
  return null
}

export type StudentIdApiProblem = { code?: string | null; message?: string | null }

export type StudentIdErrorCopy = {
  unavailable: string
  pending: string
  week: string
  eitherLimit: string
  tooBig: string
  wrongType: string
  failed: string
}

const pendingLimit = (message: string) => /pending|waiting|already/i.test(message)
const weekLimit = (message: string) => /seven|7\s*days|week|three/i.test(message)
const sizeProblem = (message: string) => /size|large|big|bytes|5\s*mb/i.test(message)
const typeProblem = (message: string) => /type|mime|format|jpeg|png|webp|pdf|content-type/i.test(message)

/**
 * A sentence for the student or the admin. UNAVAILABLE, the two rate limits, and size/type
 * are never left as a raw code. A server sentence is kept when it is already specific.
 */
export function studentIdErrorMessage(problem: StudentIdApiProblem, copy: StudentIdErrorCopy): string {
  const code = problem.code ?? ''
  const message = (problem.message ?? '').trim()
  if (code === 'UNAVAILABLE') return copy.unavailable
  if (code === 'RATE_LIMITED') {
    const pending = pendingLimit(message)
    const week = weekLimit(message)
    if (pending && !week) return copy.pending
    if (week && !pending) return copy.week
    return message || copy.eitherLimit
  }
  if (code === 'VALIDATION') {
    const size = sizeProblem(message)
    const type = typeProblem(message)
    if (size && !type) return copy.tooBig
    if (type && !size) return copy.wrongType
    return message || copy.failed
  }
  if (message && !/^[A-Z0-9_]+$/.test(message)) return message
  return copy.failed
}
