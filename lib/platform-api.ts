/**
 * Contracts for the verification, roles, institution-domain, error and usage APIs
 * (lvn-backend PR #27). Names match the patched graphql/schema.graphql:
 * `ingestAnalytics`, `adminErrors(since)`, `adminUsage(from, to)`, `adminUserActivity`,
 * `usersByIds`, `institutionDomains`, `reviewInstitutionDomain`, `setAnalyticsOptOut`,
 * and `aiCheck { extracted }` on a verification request.
 *
 * The ID-card switches are still written with `updateAdminSetting` and the catalog keys.
 * A query the running API does not know yet falls back to the slimmer document.
 */
import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { parse, type DocumentNode } from 'graphql'
import { apolloClient } from '@/lib/apollo'

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

const documentOf = (source: string): DocumentNode => parse(source)

const AI_CHECK = /* GraphQL */ `
  aiCheck {
    verdict
    confidence
    reason
    checkedAt
    extracted { name institution idNumber validUntil }
  }
`

const REVIEW_QUEUE = documentOf(/* GraphQL */ `
  query VerificationRequestsToReview($after: UUID) {
    verificationRequestsToReview(first: 30, after: $after) {
      id
      purpose
      institution
      subjects
      method
      status
      message
      reason
      createdAt
      ${AI_CHECK}
      requester { id displayName handle email institution { name } profile { department } }
      documents { fileId fileName mimeType sizeBytes }
    }
  }
`)

const REVIEW_QUEUE_BASIC = documentOf(/* GraphQL */ `
  query VerificationRequestsToReview($after: UUID) {
    verificationRequestsToReview(first: 30, after: $after) {
      id
      purpose
      institution
      subjects
      method
      status
      message
      reason
      createdAt
      requester { id displayName handle }
      documents { fileId fileName mimeType sizeBytes }
    }
  }
`)

const DOCUMENT_URL = documentOf(/* GraphQL */ `
  query VerificationDocumentUrl($requestId: UUID!, $fileId: UUID!) {
    verificationDocumentUrl(requestId: $requestId, fileId: $fileId) { url expiresAt }
  }
`)

const REVIEW = documentOf(/* GraphQL */ `
  mutation ReviewVerificationRequest($input: ReviewVerificationRequestInput!) {
    reviewVerificationRequest(input: $input) {
      request { id status }
      userErrors { message code }
    }
  }
`)

const STUDENT_ID_QUEUE = documentOf(/* GraphQL */ `
  query StudentIdVerificationQueue($first: Int) {
    studentIdVerificationQueue(first: $first) {
      id
      status
      reason
      createdAt
      ${AI_CHECK}
      requester { id displayName handle email institution { name } profile { department } }
    }
  }
`)

const STUDENT_ID_QUEUE_BASIC = documentOf(/* GraphQL */ `
  query StudentIdVerificationQueue($first: Int) {
    studentIdVerificationQueue(first: $first) {
      id
      status
      reason
      createdAt
      requester { id displayName handle }
    }
  }
`)

const STUDENT_ID_URL = documentOf(/* GraphQL */ `
  query StudentIdCardUrl($requestId: UUID!) {
    studentIdCardUrl(requestId: $requestId) { url expiresAt }
  }
`)

const DOMAINS = documentOf(/* GraphQL */ `
  query InstitutionDomains($status: DomainReviewStatus) {
    institutionDomains(status: $status) { domain status requests firstSeenAt }
  }
`)

const DECIDE_DOMAIN = documentOf(/* GraphQL */ `
  mutation ReviewInstitutionDomain($input: DecideDomainReviewInput!) {
    reviewInstitutionDomain(input: $input) { ok userErrors { message code } }
  }
`)

const SET_ROLE = documentOf(/* GraphQL */ `
  mutation SetGlobalRole($input: SetGlobalRoleInput!) {
    setGlobalRole(input: $input) { ok userErrors { message code } }
  }
`)

const ADMIN_ERRORS = documentOf(/* GraphQL */ `
  query AdminErrors($since: DateTime) {
    adminErrors(since: $since) {
      code
      count
      firstSeen
      lastSeen
      sampleMessage
      userIds
    }
  }
`)

const USERS_BY_IDS = documentOf(/* GraphQL */ `
  query UsersByIds($ids: [UUID!]!) {
    usersByIds(ids: $ids) { id displayName email globalRole }
  }
`)

const ADMIN_USAGE = documentOf(/* GraphQL */ `
  query AdminUsage($from: DateTime, $to: DateTime) {
    adminUsage(from: $from, to: $to) {
      dau
      wau
      mau
      from
      to
      topEvents { name count }
      topFeatures { name count }
    }
  }
`)

const USER_ACTIVITY = documentOf(/* GraphQL */ `
  query AdminUserActivity($userId: UUID!, $first: Int) {
    adminUserActivity(userId: $userId, first: $first) {
      name
      occurredAt
      platform
      props
      appVersion
    }
  }
`)

const INGEST = documentOf(/* GraphQL */ `
  mutation IngestAnalytics($input: IngestAnalyticsInput!) {
    ingestAnalytics(input: $input) {
      ok
      userErrors { code message }
    }
  }
`)

const OPT_OUT = documentOf(/* GraphQL */ `
  query AnalyticsOptOut {
    viewer { id analyticsOptOut }
  }
`)

const SET_OPT_OUT = documentOf(/* GraphQL */ `
  mutation SetAnalyticsOptOut($optOut: Boolean!) {
    setAnalyticsOptOut(optOut: $optOut) { ok userErrors { message code } }
  }
`)

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
    const data = await run<{ verificationRequestsToReview: RawReview[] }>(REVIEW_QUEUE, {}, 'query')
    return (data.verificationRequestsToReview ?? []).map(reviewOf)
  } catch (error) {
    if (!isUnknownFieldError(error)) throw error
    const data = await run<{ verificationRequestsToReview: RawReview[] }>(REVIEW_QUEUE_BASIC, {}, 'query')
    return (data.verificationRequestsToReview ?? []).map(reviewOf)
  }
}

export async function verificationDocumentUrl(requestId: string, fileId: string): Promise<string | null> {
  const data = await run<{ verificationDocumentUrl: { url: string } | null }>(DOCUMENT_URL, { requestId, fileId }, 'query')
  return data.verificationDocumentUrl?.url ?? null
}

/** The first user error, or null when the decision was saved. */
export async function reviewVerification(input: { requestId: string; approve: boolean; reason: string | null }): Promise<string | null> {
  const data = await run<{ reviewVerificationRequest: { userErrors: { message: string }[] } }>(REVIEW, { input }, 'mutation')
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
    const data = await run<{ studentIdVerificationQueue: RawStudentId[] }>(STUDENT_ID_QUEUE, { first }, 'query')
    return (data.studentIdVerificationQueue ?? []).map(studentIdOf)
  } catch (error) {
    if (!isUnknownFieldError(error)) throw error
    const data = await run<{ studentIdVerificationQueue: RawStudentId[] }>(STUDENT_ID_QUEUE_BASIC, { first }, 'query')
    return (data.studentIdVerificationQueue ?? []).map(studentIdOf)
  }
}

export async function studentIdCardUrl(requestId: string): Promise<string | null> {
  const data = await run<{ studentIdCardUrl: { url: string } | null }>(STUDENT_ID_URL, { requestId }, 'query')
  return data.studentIdCardUrl?.url ?? null
}

export async function listInstitutionDomains(status?: DomainStatus): Promise<InstitutionDomain[]> {
  const data = await run<{ institutionDomains: InstitutionDomain[] }>(DOMAINS, status ? { status } : {}, 'query')
  return data.institutionDomains ?? []
}

export async function decideInstitutionDomain(domain: string, approve: boolean): Promise<string | null> {
  const data = await run<{ reviewInstitutionDomain: { ok: boolean; userErrors: { message: string }[] } }>(DECIDE_DOMAIN, { input: { domain, approve } }, 'mutation')
  const payload = data.reviewInstitutionDomain
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}

export async function setStaffRole(userId: string, role: AssignableRole): Promise<string | null> {
  const data = await run<{ setGlobalRole: { ok: boolean; userErrors: { message: string }[] } }>(SET_ROLE, { input: { userId, role } }, 'mutation')
  const payload = data.setGlobalRole
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}

export async function loadErrorGroups(since?: string): Promise<ErrorGroup[]> {
  const data = await run<{ adminErrors: ErrorGroup[] }>(ADMIN_ERRORS, since ? { since } : {}, 'query')
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
  const data = await run<{ usersByIds: LookupUser[] }>(USERS_BY_IDS, { ids }, 'query')
  return data.usersByIds ?? []
}

export async function loadUsageSummary(range?: { from?: string; to?: string }): Promise<UsageSummary> {
  const data = await run<{ adminUsage: UsageSummary }>(ADMIN_USAGE, { from: range?.from, to: range?.to }, 'query')
  return {
    ...data.adminUsage,
    topEvents: data.adminUsage.topEvents ?? [],
    topFeatures: data.adminUsage.topFeatures ?? [],
  }
}

export async function loadUserTimeline(userId: string, first = 50): Promise<TimelineEntry[]> {
  const data = await run<{ adminUserActivity: TimelineEntry[] }>(USER_ACTIVITY, { userId, first }, 'query')
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
  const data = await run<{ ingestAnalytics: { ok: boolean; userErrors: { code: string; message: string }[] } }>(INGEST, { input: { events, errors } }, 'mutation')
  const problem = data.ingestAnalytics.userErrors[0]
  if (!problem) return
  // A refused name is not worth retrying; the tracker would put the same batch back.
  if (problem.code === 'VALIDATION') return
  throw new PlatformError(problem.message)
}

export async function loadAnalyticsOptOut(): Promise<boolean> {
  const data = await run<{ viewer: { analyticsOptOut: boolean | null } | null }>(OPT_OUT, undefined, 'query')
  return data.viewer?.analyticsOptOut === true
}

export async function saveAnalyticsOptOut(optOut: boolean): Promise<string | null> {
  const data = await run<{ setAnalyticsOptOut: { ok: boolean; userErrors: { message: string }[] } }>(SET_OPT_OUT, { optOut }, 'mutation')
  const payload = data.setAnalyticsOptOut
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}
