/**
 * Contracts for the verification, roles, institution-domain, error and usage APIs
 * (lvn-backend PR #27). Names match the patched graphql/schema.graphql:
 * `ingestAnalytics`, `adminErrors(since)`, `adminUsage(from, to)`, `adminUserActivity`,
 * `usersByIds`, `institutionDomains`, `reviewInstitutionDomain`, `setAnalyticsOptOut`,
 * and `aiCheck { extracted }` on a verification request.
 *
 * The ID-card switches are still written with `updateAdminSetting` and the catalog keys.
 * A query the running API does not know yet falls back to the slimmer document.
 *
 * Account admin uses the final names from lvn-backend PR #27: `adminUsers`, `adminUpdateUser`,
 * `adminSetAccountStanding` and `adminDeleteUser`.
 */
import { CombinedGraphQLErrors } from '@apollo/client/errors'
import type { DocumentNode } from 'graphql'
import { parseAge } from '@/lib/age'
import { apolloClient } from '@/lib/apollo'
import {
  AdminDeleteUserDocument,
  AdminErrorsDocument,
  AdminSetAccountStandingDocument,
  AdminUpdateUserDocument,
  AdminUsageDocument,
  AdminUserActivityDocument,
  AdminUsersDocument,
  AnalyticsOptOutDocument,
  IngestAnalyticsDocument,
  InstitutionDomainsDocument,
  ReviewInstitutionDomainDocument,
  ReviewVerificationRequestDocument,
  SetAnalyticsOptOutDocument,
  SetGlobalRoleDocument,
  StudentIdCardUrlDocument,
  StudentIdVerificationQueueBasicDocument,
  StudentIdVerificationQueueDocument,
  UsersByIdsDocument,
  VerificationDocumentUrlDocument,
  VerificationRequestsToReviewBasicDocument,
  VerificationRequestsToReviewDocument,
} from '@/graphql/generated/graphql'

export type StaffRole = 'PLATFORM_ADMIN' | 'MANAGER' | 'TEACHER'
export type AssignableRole = 'MANAGER' | 'TEACHER' | 'STUDENT'

/** Names `UsageEventInput` accepts. Anything else is refused with VALIDATION. */
export const USAGE_EVENT_NAMES = ['page_view', 'note_open', 'note_upload', 'search', 'download', 'sign_in'] as const

export type IdCardFieldsView = {
  name: string | null
  institution: string | null
  idNumber: string | null
  validUntil: string | null
}

export type AiVerdictView = {
  verdict: string
  confidence: number | null
  /** `IdCardCheck.reason`, one string. */
  reason: string | null
  checkedAt: string | null
  extracted: IdCardFieldsView
}

/** Admin setting catalog keys for the college-ID vision check (not a separate settings type). */
export const STUDENT_ID_AI_CHECK = 'student_id_ai_check'
export const STUDENT_ID_AI_AUTO_APPROVE = 'student_id_ai_auto_approve'
export const STUDENT_ID_AI_CONFIDENCE_THRESHOLD = 'student_id_ai_confidence_threshold'
export const STUDENT_ID_IMAGE_RETENTION_DAYS = 'student_id_image_retention_days'

export const STUDENT_ID_AI_SETTING_KEYS = [
  STUDENT_ID_AI_CHECK,
  STUDENT_ID_AI_AUTO_APPROVE,
  STUDENT_ID_AI_CONFIDENCE_THRESHOLD,
  STUDENT_ID_IMAGE_RETENTION_DAYS,
] as const

export type ReviewDocument = {
  fileId: string
  fileName: string
  mimeType: string
  sizeBytes: number
}

export type ReviewRequestView = {
  id: string
  purpose: string
  institution: string | null
  subjects: string | null
  method: string
  status: string
  message: string | null
  reason: string | null
  createdAt: string
  requester: {
    id: string
    displayName: string
    handle: string
    email: string | null
    institutionName: string | null
    department: string | null
  }
  documents: ReviewDocument[]
  ai: AiVerdictView | null
}

export type StudentIdReviewItem = {
  id: string
  status: string
  reason: string | null
  createdAt: string
  requester: ReviewRequestView['requester']
  ai: AiVerdictView | null
}

export type DomainStatus = 'ACADEMIC_QUEUED' | 'APPROVED' | 'NEEDS_REVIEW' | 'REJECTED'

export type InstitutionDomain = {
  domain: string
  status: DomainStatus
  requests: number
  firstSeenAt: string
}

export type ErrorGroup = {
  code: string
  count: number
  firstSeen: string
  lastSeen: string
  sampleMessage: string
  userIds: string[]
}

export type LookupUser = {
  id: string
  displayName: string
  email: string
  globalRole: string
}

export type UsageCount = { name: string; count: number }

export type UsageSummary = {
  dau: number
  wau: number
  mau: number
  topFeatures: UsageCount[]
  topEvents: UsageCount[]
}

export type TimelineEntry = {
  name: string
  occurredAt: string
  platform: string
  props: Record<string, unknown> | null
  appVersion: string | null
}

export type UsageEventInput = {
  name: string
  platform: 'WEB'
  occurredAt: string
  props?: Record<string, string | number | boolean>
}

export type ErrorEventInput = {
  code: string
  message: string
  platform: 'WEB'
  route?: string | null
  occurredAt: string
}

export class PlatformError extends Error {
  readonly forbidden: boolean
  constructor(message: string, forbidden = false) {
    super(message)
    this.name = 'PlatformError'
    this.forbidden = forbidden
  }
}


function toPlatformError(error: unknown): PlatformError {
  if (error instanceof PlatformError) return error
  if (CombinedGraphQLErrors.is(error)) {
    const forbidden = error.errors.some((e) => e.extensions?.code === 'FORBIDDEN')
    return new PlatformError(error.errors[0]?.message ?? 'Request failed', forbidden)
  }
  return new PlatformError(error instanceof Error ? error.message : 'Request failed')
}

export function isUnknownFieldError(error: unknown): boolean {
  const text = error instanceof Error ? error.message : String(error)
  return /Cannot query field|GRAPHQL_VALIDATION_FAILED|Unknown argument|is not defined on type/i.test(text)
}

async function run<T>(document: DocumentNode, variables: Record<string, unknown> | undefined, kind: 'query' | 'mutation'): Promise<T> {
  const client = apolloClient()
  try {
    const result = kind === 'mutation' ? await client.mutate({ mutation: document, variables }) : await client.query({ query: document, variables, fetchPolicy: 'no-cache' })
    if (!result.data) throw new PlatformError('Empty response')
    return result.data as T
  } catch (error) {
    throw toPlatformError(error)
  }
}

type RawExtracted = { name?: string | null; institution?: string | null; idNumber?: string | null; validUntil?: string | null }

type RawCheck = {
  verdict?: string | null
  confidence?: number | null
  reason?: string | null
  checkedAt?: string | null
  extracted?: RawExtracted | null
}

function textOrNull(value: string | null | undefined): string | null {
  const text = value?.trim()
  return text ? text : null
}

function aiOf(raw: { aiCheck?: RawCheck | null }): AiVerdictView | null {
  const check = raw.aiCheck
  if (!check?.verdict) return null
  const extracted = check.extracted ?? {}
  return {
    verdict: check.verdict,
    confidence: typeof check.confidence === 'number' ? check.confidence : null,
    reason: textOrNull(check.reason),
    checkedAt: check.checkedAt ?? null,
    extracted: {
      name: textOrNull(extracted.name),
      institution: textOrNull(extracted.institution),
      idNumber: textOrNull(extracted.idNumber),
      validUntil: textOrNull(extracted.validUntil),
    },
  }
}

type RawRequester = {
  id: string
  displayName: string
  handle: string
  email?: string | null
  institution?: { name?: string | null } | null
  profile?: { department?: string | null } | null
}

function requesterOf(raw: RawRequester): ReviewRequestView['requester'] {
  return {
    id: raw.id,
    displayName: raw.displayName,
    handle: raw.handle,
    email: raw.email ?? null,
    institutionName: raw.institution?.name ?? null,
    department: raw.profile?.department ?? null,
  }
}

type RawReview = {
  id: string
  purpose: string
  institution?: string | null
  subjects?: string | null
  method: string
  status: string
  message?: string | null
  reason?: string | null
  createdAt: string
  requester: RawRequester
  documents?: ReviewDocument[] | null
  aiCheck?: RawCheck | null
}

function reviewOf(raw: RawReview): ReviewRequestView {
  return {
    id: raw.id,
    purpose: raw.purpose,
    institution: raw.institution ?? null,
    subjects: raw.subjects ?? null,
    method: raw.method,
    status: raw.status,
    message: raw.message ?? null,
    reason: raw.reason ?? null,
    createdAt: raw.createdAt,
    requester: requesterOf(raw.requester),
    documents: raw.documents ?? [],
    ai: aiOf(raw),
  }
}

export async function loadVerificationQueue(): Promise<ReviewRequestView[]> {
  try {
    const data = await run<{ verificationRequestsToReview: RawReview[] }>(VerificationRequestsToReviewDocument, {}, 'query')
    return (data.verificationRequestsToReview ?? []).map(reviewOf)
  } catch (error) {
    if (!isUnknownFieldError(error)) throw error
    const data = await run<{ verificationRequestsToReview: RawReview[] }>(VerificationRequestsToReviewBasicDocument, {}, 'query')
    return (data.verificationRequestsToReview ?? []).map(reviewOf)
  }
}

export async function verificationDocumentUrl(requestId: string, fileId: string): Promise<string | null> {
  const data = await run<{ verificationDocumentUrl: { url: string } | null }>(VerificationDocumentUrlDocument, { requestId, fileId }, 'query')
  return data.verificationDocumentUrl?.url ?? null
}

/** The first user error, or null when the decision was saved. */
export async function reviewVerification(input: { requestId: string; approve: boolean; reason: string | null }): Promise<string | null> {
  const data = await run<{ reviewVerificationRequest: { userErrors: { message: string }[] } }>(ReviewVerificationRequestDocument, { input }, 'mutation')
  return data.reviewVerificationRequest.userErrors[0]?.message ?? null
}

type RawStudentId = {
  id: string
  status: string
  reason?: string | null
  createdAt: string
  requester: RawRequester
  aiCheck?: RawCheck | null
}

function studentIdOf(raw: RawStudentId): StudentIdReviewItem {
  return { id: raw.id, status: raw.status, reason: raw.reason ?? null, createdAt: raw.createdAt, requester: requesterOf(raw.requester), ai: aiOf(raw) }
}

export async function loadStudentIdQueue(first = 30): Promise<StudentIdReviewItem[]> {
  try {
    const data = await run<{ studentIdVerificationQueue: RawStudentId[] }>(StudentIdVerificationQueueDocument, { first }, 'query')
    return (data.studentIdVerificationQueue ?? []).map(studentIdOf)
  } catch (error) {
    if (!isUnknownFieldError(error)) throw error
    const data = await run<{ studentIdVerificationQueue: RawStudentId[] }>(StudentIdVerificationQueueBasicDocument, { first }, 'query')
    return (data.studentIdVerificationQueue ?? []).map(studentIdOf)
  }
}

export async function studentIdCardUrl(requestId: string): Promise<string | null> {
  const data = await run<{ studentIdCardUrl: { url: string } | null }>(StudentIdCardUrlDocument, { requestId }, 'query')
  return data.studentIdCardUrl?.url ?? null
}

export async function listInstitutionDomains(status?: DomainStatus): Promise<InstitutionDomain[]> {
  const data = await run<{ institutionDomains: InstitutionDomain[] }>(InstitutionDomainsDocument, status ? { status } : {}, 'query')
  return data.institutionDomains ?? []
}

export async function decideInstitutionDomain(domain: string, approve: boolean): Promise<string | null> {
  const data = await run<{ reviewInstitutionDomain: { ok: boolean; userErrors: { message: string }[] } }>(ReviewInstitutionDomainDocument, { input: { domain, approve } }, 'mutation')
  const payload = data.reviewInstitutionDomain
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}

export async function setStaffRole(userId: string, role: AssignableRole): Promise<string | null> {
  const data = await run<{ setGlobalRole: { ok: boolean; userErrors: { message: string }[] } }>(SetGlobalRoleDocument, { input: { userId, role } }, 'mutation')
  const payload = data.setGlobalRole
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}

export async function loadErrorGroups(since?: string): Promise<ErrorGroup[]> {
  const data = await run<{ adminErrors: ErrorGroup[] }>(AdminErrorsDocument, since ? { since } : {}, 'query')
  return (data.adminErrors ?? []).map((group) => ({
    code: group.code,
    count: group.count,
    firstSeen: group.firstSeen,
    lastSeen: group.lastSeen,
    sampleMessage: group.sampleMessage,
    userIds: group.userIds ?? [],
  }))
}

export async function lookupUsers(ids: string[]): Promise<LookupUser[]> {
  if (!ids.length) return []
  const data = await run<{ usersByIds: LookupUser[] }>(UsersByIdsDocument, { ids }, 'query')
  return data.usersByIds ?? []
}

export async function loadUsageSummary(range?: { from?: string; to?: string }): Promise<UsageSummary> {
  const data = await run<{ adminUsage: UsageSummary }>(AdminUsageDocument, { from: range?.from, to: range?.to }, 'query')
  return {
    ...data.adminUsage,
    topEvents: data.adminUsage.topEvents ?? [],
    topFeatures: data.adminUsage.topFeatures ?? [],
  }
}

export async function loadUserTimeline(userId: string, first = 50): Promise<TimelineEntry[]> {
  const data = await run<{ adminUserActivity: TimelineEntry[] }>(AdminUserActivityDocument, { userId, first }, 'query')
  return (data.adminUserActivity ?? []).map((row) => ({
    name: row.name,
    occurredAt: row.occurredAt,
    platform: row.platform,
    props: row.props && typeof row.props === 'object' && !Array.isArray(row.props) ? row.props : null,
    appVersion: row.appVersion ?? null,
  }))
}

export async function ingestAnalytics(input: { events?: UsageEventInput[]; errors?: ErrorEventInput[] }): Promise<void> {
  const events = input.events ?? []
  const errors = input.errors ?? []
  if (!events.length && !errors.length) return
  const data = await run<{ ingestAnalytics: { ok: boolean; userErrors: { code: string; message: string }[] } }>(IngestAnalyticsDocument, { input: { events, errors } }, 'mutation')
  const problem = data.ingestAnalytics.userErrors[0]
  if (!problem) return
  // A refused name is not worth retrying; the tracker would put the same batch back.
  if (problem.code === 'VALIDATION') return
  throw new PlatformError(problem.message)
}

export async function loadAnalyticsOptOut(): Promise<boolean> {
  const data = await run<{ viewer: { analyticsOptOut: boolean | null } | null }>(AnalyticsOptOutDocument, undefined, 'query')
  return data.viewer?.analyticsOptOut === true
}

export async function saveAnalyticsOptOut(optOut: boolean): Promise<string | null> {
  const data = await run<{ setAnalyticsOptOut: { ok: boolean; userErrors: { message: string }[] } }>(SetAnalyticsOptOutDocument, { optOut }, 'mutation')
  const payload = data.setAnalyticsOptOut
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}

export type AccountStatus = 'ACTIVE' | 'AGE_BLOCKED' | 'BLOCKED' | 'SUSPENDED'

export type AdminUserStatusFilter = 'ACTIVE' | 'AGE_BLOCKED' | 'BLOCKED_OR_SUSPENDED'

export type AgeOutcome = 'unblocked' | 'still_under_age'

export type AdminManagedUser = {
  id: string
  accountStatus: AccountStatus
  /** Whole years now (lvn-backend ADR-0104): from the date of birth when there is one, else the age given. */
  age: number | null
  createdAt: string
  /** YYYY-MM-DD, only for accounts that gave one (before ADR-0104) or had one set by an admin. */
  dateOfBirth: string | null
  displayName: string
  email: string
  globalRole: string
  handle: string
  statusReason: string | null
}


type RawUser = {
  id: string
  accountStatus?: string | null
  age?: number | null
  createdAt?: string | null
  dateOfBirth?: string | null
  displayName?: string | null
  email?: string | null
  globalRole?: string | null
  handle?: string | null
  statusReason?: string | null
}

function statusOf(value: string | null | undefined): AccountStatus {
  if (value === 'AGE_BLOCKED' || value === 'BLOCKED' || value === 'SUSPENDED' || value === 'ACTIVE') return value
  return 'ACTIVE'
}

function userOf(raw: RawUser): AdminManagedUser {
  return {
    id: raw.id,
    accountStatus: statusOf(raw.accountStatus),
    age: raw.age ?? null,
    createdAt: raw.createdAt ?? '',
    dateOfBirth: raw.dateOfBirth ?? null,
    displayName: raw.displayName ?? '',
    email: raw.email ?? '',
    globalRole: raw.globalRole ?? 'STUDENT',
    handle: raw.handle ?? '',
    statusReason: raw.statusReason ?? null,
  }
}

/** A corrected age or date of birth comes back as ACTIVE when it passes, and stays AGE_BLOCKED when it does not. */
export function ageOutcomeOf(status: string | null | undefined): AgeOutcome | null {
  if (status === 'ACTIVE') return 'unblocked'
  if (status === 'AGE_BLOCKED') return 'still_under_age'
  return null
}

export async function loadAdminUsers(filter: { status: AdminUserStatusFilter; search: string }): Promise<{ total: number; users: AdminManagedUser[] }> {
  const variables = { status: filter.status, search: filter.search.trim() || null, first: 50 }
  const data = await run<{ adminUsers: { total: number; users: RawUser[] | null } }>(AdminUsersDocument, variables, 'query')
  return { total: data.adminUsers.total ?? 0, users: (data.adminUsers.users ?? []).map(userOf) }
}

/**
 * At most one of `age` and `dateOfBirth`, and only when it changes (lvn-backend ADR-0104): the API refuses both
 * together, refuses `age` on an account whose date of birth decides its age, and restarts a declared age's clock on
 * every `age` it is sent.
 */
export type AdminUserEdit = { userId: string; reason: string; displayName: string; email: string } & (
  | { age?: number; dateOfBirth?: never }
  | { age?: never; dateOfBirth?: string }
)

/**
 * The age part of an admin's edit, from what the form holds (lvn-backend ADR-0104). An account with a date of birth is
 * corrected by its date; one without, by an age in whole years. A value left as it was sends nothing, and an empty
 * age on an account that never had one is left alone. 'invalid' when the age typed is not a whole number from
 * AGE_MIN to AGE_MAX.
 */
export function ageEditOf(user: Pick<AdminManagedUser, 'age' | 'dateOfBirth'>, form: { age: string; dateOfBirth: string }): { age: number } | { dateOfBirth: string } | Record<string, never> | 'invalid' {
  if (user.dateOfBirth !== null) return form.dateOfBirth === user.dateOfBirth ? {} : { dateOfBirth: form.dateOfBirth }
  if (!form.age.trim() && user.age === null) return {}
  const parsed = parseAge(form.age)
  if ('problem' in parsed) return 'invalid'
  return parsed.age === user.age ? {} : { age: parsed.age }
}

export async function updateAdminUser(input: AdminUserEdit): Promise<{ problem: string | null; outcome: AgeOutcome | null; user: AdminManagedUser | null }> {
  type Payload = { user?: RawUser | null; userErrors?: { message: string }[] }
  const data = await run<{ adminUpdateUser: Payload }>(AdminUpdateUserDocument, { input }, 'mutation')
  const payload = data.adminUpdateUser
  const problem = payload.userErrors?.[0]?.message ?? null
  const user = payload.user ? userOf(payload.user) : null
  return { problem, outcome: problem ? null : ageOutcomeOf(user?.accountStatus), user }
}

/** ACTIVE lifts a block. until is required when status is SUSPENDED. AGE_BLOCKED is not sent. */
export async function setAccountStanding(input: { userId: string; status: 'ACTIVE' | 'BLOCKED' | 'SUSPENDED'; reason: string; until?: string | null }): Promise<{ problem: string | null; user: AdminManagedUser | null }> {
  const data = await run<{ adminSetAccountStanding: { user?: RawUser | null; userErrors?: { message: string }[] } }>(AdminSetAccountStandingDocument, { input: { ...input, until: input.until ?? null } }, 'mutation')
  const payload = data.adminSetAccountStanding
  const problem = payload.userErrors?.[0]?.message ?? null
  return { problem, user: problem || !payload.user ? null : userOf(payload.user) }
}

/** confirm is the exact word DELETE. */
export async function deleteAdminUser(input: { userId: string; confirm: string; reason: string }): Promise<string | null> {
  const data = await run<{ adminDeleteUser: { ok: boolean; userErrors?: { message: string }[] } }>(AdminDeleteUserDocument, { input }, 'mutation')
  const payload = data.adminDeleteUser
  return payload.userErrors?.[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}
