/**
 * Contracts for the verification, roles, institution-domain, error and usage APIs
 * (lvn-backend branch feat/verification-manager-ai-analytics).
 *
 * The operations live in this file so the web app can line up with that branch in one place
 * when its schema is published. Existing fields (`domainReviews`, `decideDomainReview`,
 * `setGlobalRole`, `verificationRequestsToReview`) are called by the names the API already uses.
 * New fields (`aiVerdict`, `aiVerificationSettings`, `adminErrors`, `adminUsage`, `usersByIds`,
 * `ingestEvents`, `analyticsOptOut`) use the names from that branch. A query that the running API
 * does not know yet falls back where a slimmer query still answers.
 */
import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { parse, type DocumentNode } from 'graphql'
import { apolloClient } from '@/lib/apollo'

export type StaffRole = 'PLATFORM_ADMIN' | 'MANAGER' | 'TEACHER'
export type AssignableRole = 'MANAGER' | 'TEACHER' | 'STUDENT'

export type AiExtractedFields = {
  name: string | null
  institution: string | null
  idNumberPresent: boolean | null
}

export type AiVerdictView = {
  verdict: string
  confidence: number | null
  reason: string | null
  extracted: AiExtractedFields
}

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

export type AiCheckSettings = {
  aiCheckEnabled: boolean
  autoApproveOnHighConfidence: boolean
}

export type DomainStatus = 'ACADEMIC_QUEUED' | 'APPROVED' | 'NEEDS_REVIEW' | 'REJECTED'

export type InstitutionDomain = {
  domain: string
  status: DomainStatus
  requests: number
  firstSeenAt: string
}

export type ErrorGroup = {
  fingerprint: string
  type: string
  message: string
  count: number
  firstSeen: string
  lastSeen: string
  trend: number[]
  affectedUserIds: string[]
  affectedUsers: { userId: string; lastSeen: string }[]
}

export type LookupUser = {
  id: string
  displayName: string
  email: string | null
  handle: string
  globalRole: string
}

export type UsageSummary = {
  dau: number
  wau: number
  mau: number
  topPages: { name: string; count: number }[]
  topEvents: { name: string; count: number }[]
}

export type TimelineEntry = {
  id: string
  name: string
  at: string
  path: string | null
}

export type UsageEventInput = {
  name: string
  at: string
  path: string | null
  props: { key: string; value: string }[]
}

export type ErrorEventInput = {
  type: string
  message: string
  route: string | null
  stack: string | null
  at: string
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
      aiVerdict
      aiConfidence
      aiReason
      aiExtracted { name institution idNumberPresent }
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
      aiVerdict
      aiConfidence
      aiReason
      aiExtracted { name institution idNumberPresent }
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

const AI_SETTINGS = documentOf(/* GraphQL */ `
  query AiVerificationSettings {
    aiVerificationSettings { aiCheckEnabled autoApproveOnHighConfidence }
  }
`)

const SAVE_AI_SETTINGS = documentOf(/* GraphQL */ `
  mutation UpdateAiVerificationSettings($input: AiVerificationSettingsInput!) {
    updateAiVerificationSettings(input: $input) {
      settings { aiCheckEnabled autoApproveOnHighConfidence }
      userErrors { message code }
    }
  }
`)

const DOMAINS = documentOf(/* GraphQL */ `
  query InstitutionDomains($status: DomainReviewStatus) {
    domainReviews(status: $status) { domain status requests firstSeenAt }
  }
`)

const DECIDE_DOMAIN = documentOf(/* GraphQL */ `
  mutation DecideInstitutionDomain($input: DecideDomainReviewInput!) {
    decideDomainReview(input: $input) { ok userErrors { message code } }
  }
`)

const SET_ROLE = documentOf(/* GraphQL */ `
  mutation SetStaffRole($input: SetGlobalRoleInput!) {
    setGlobalRole(input: $input) { ok userErrors { message code } }
  }
`)

const ADMIN_ERRORS = documentOf(/* GraphQL */ `
  query AdminErrors {
    adminErrors {
      fingerprint
      type
      message
      count
      firstSeen
      lastSeen
      trend
      affectedUserIds
      affectedUsers { userId lastSeen }
    }
  }
`)

const USERS_BY_IDS = documentOf(/* GraphQL */ `
  query UsersByIds($ids: [UUID!]!) {
    usersByIds(ids: $ids) { id displayName email handle globalRole }
  }
`)

const ADMIN_USAGE = documentOf(/* GraphQL */ `
  query AdminUsage {
    adminUsage {
      dau
      wau
      mau
      topPages { name count }
      topEvents { name count }
    }
  }
`)

const USER_TIMELINE = documentOf(/* GraphQL */ `
  query AdminUserTimeline($userId: UUID!) {
    adminUserTimeline(userId: $userId) { id name at path }
  }
`)

const INGEST = documentOf(/* GraphQL */ `
  mutation IngestEvents($input: IngestEventsInput!) {
    ingestEvents(input: $input) { ok }
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

type RawAi = { aiVerdict?: string | null; aiConfidence?: number | null; aiReason?: string | null; aiExtracted?: { name?: string | null; institution?: string | null; idNumberPresent?: boolean | null } | null }

function aiOf(raw: RawAi): AiVerdictView | null {
  if (!raw.aiVerdict) return null
  return {
    verdict: raw.aiVerdict,
    confidence: typeof raw.aiConfidence === 'number' ? raw.aiConfidence : null,
    reason: raw.aiReason ?? null,
    extracted: {
      name: raw.aiExtracted?.name ?? null,
      institution: raw.aiExtracted?.institution ?? null,
      idNumberPresent: raw.aiExtracted?.idNumberPresent ?? null,
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

type RawReview = RawAi & {
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

type RawStudentId = RawAi & { id: string; status: string; reason?: string | null; createdAt: string; requester: RawRequester }

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

export async function loadAiCheckSettings(): Promise<AiCheckSettings> {
  const data = await run<{ aiVerificationSettings: AiCheckSettings }>(AI_SETTINGS, undefined, 'query')
  return data.aiVerificationSettings
}

export async function saveAiCheckSettings(input: AiCheckSettings): Promise<string | null> {
  const settings = { aiCheckEnabled: input.aiCheckEnabled, autoApproveOnHighConfidence: input.autoApproveOnHighConfidence }
  const data = await run<{ updateAiVerificationSettings: { userErrors: { message: string }[] } }>(SAVE_AI_SETTINGS, { input: settings }, 'mutation')
  return data.updateAiVerificationSettings.userErrors[0]?.message ?? null
}

export async function listInstitutionDomains(status?: DomainStatus): Promise<InstitutionDomain[]> {
  const data = await run<{ domainReviews: InstitutionDomain[] }>(DOMAINS, status ? { status } : {}, 'query')
  return data.domainReviews ?? []
}

export async function decideInstitutionDomain(domain: string, approve: boolean): Promise<string | null> {
  const data = await run<{ decideDomainReview: { ok: boolean; userErrors: { message: string }[] } }>(DECIDE_DOMAIN, { input: { domain, approve } }, 'mutation')
  const payload = data.decideDomainReview
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}

export async function setStaffRole(userId: string, role: AssignableRole): Promise<string | null> {
  const data = await run<{ setGlobalRole: { ok: boolean; userErrors: { message: string }[] } }>(SET_ROLE, { input: { userId, role } }, 'mutation')
  const payload = data.setGlobalRole
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}

export async function loadErrorGroups(): Promise<ErrorGroup[]> {
  const data = await run<{ adminErrors: ErrorGroup[] }>(ADMIN_ERRORS, undefined, 'query')
  return (data.adminErrors ?? []).map((group) => ({
    ...group,
    trend: group.trend ?? [],
    affectedUserIds: group.affectedUserIds ?? group.affectedUsers?.map((user) => user.userId) ?? [],
    affectedUsers: group.affectedUsers ?? [],
  }))
}

export async function lookupUsers(ids: string[]): Promise<LookupUser[]> {
  if (!ids.length) return []
  const data = await run<{ usersByIds: LookupUser[] }>(USERS_BY_IDS, { ids }, 'query')
  return data.usersByIds ?? []
}

export async function loadUsageSummary(): Promise<UsageSummary> {
  const data = await run<{ adminUsage: UsageSummary }>(ADMIN_USAGE, undefined, 'query')
  return data.adminUsage
}

export async function loadUserTimeline(userId: string): Promise<TimelineEntry[]> {
  const data = await run<{ adminUserTimeline: TimelineEntry[] }>(USER_TIMELINE, { userId }, 'query')
  return data.adminUserTimeline ?? []
}

export async function ingestEvents(input: { usage: UsageEventInput[]; errors: ErrorEventInput[] }): Promise<void> {
  if (!input.usage.length && !input.errors.length) return
  await run(INGEST, { input }, 'mutation')
}

export async function loadAnalyticsOptOut(): Promise<boolean> {
  const data = await run<{ viewer: { analyticsOptOut: boolean } | null }>(OPT_OUT, undefined, 'query')
  return data.viewer?.analyticsOptOut === true
}

export async function saveAnalyticsOptOut(optOut: boolean): Promise<string | null> {
  const data = await run<{ setAnalyticsOptOut: { ok: boolean; userErrors: { message: string }[] } }>(SET_OPT_OUT, { optOut }, 'mutation')
  const payload = data.setAnalyticsOptOut
  return payload.userErrors[0]?.message ?? (payload.ok ? null : 'That did not work. Try again.')
}
