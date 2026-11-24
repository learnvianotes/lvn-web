import { readdirSync, readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { STUDENT_ID_AI_SETTING_KEYS } from '@/lib/platform-api'

describe('platform API names', () => {
  const source = readFileSync('lib/platform-api.ts', 'utf8')
  const operations = readdirSync('graphql/operations')
    .filter((name) => name.endsWith('.graphql'))
    .map((name) => readFileSync(`graphql/operations/${name}`, 'utf8'))
    .join('\n')

  it('saves the ID-card check as admin setting keys', () => {
    expect(STUDENT_ID_AI_SETTING_KEYS).toEqual([
      'student_id_ai_check',
      'student_id_ai_auto_approve',
      'student_id_ai_confidence_threshold',
      'student_id_image_retention_days',
    ])
    expect(source).not.toMatch(/AiVerificationSettings/)
  })

  it('asks for the verdict, extracted fields and the analytics operations from the schema', () => {
    expect(operations).toMatch(/aiCheck \{/)
    expect(operations).toMatch(/extracted\s*\{[^}]*name[^}]*institution[^}]*idNumber[^}]*validUntil/)
    expect(operations).not.toMatch(/aiReasons|aiVerdict|ingestEvents|adminUserTimeline|topPages/)
    expect(operations).toMatch(/institutionDomains\(status: \$status\)/)
    expect(operations).toMatch(/reviewInstitutionDomain\(input: \$input\)/)
    expect(operations).toMatch(/ingestAnalytics\(input: \$input\)/)
    expect(operations).toMatch(/adminErrors\(since: \$since\)/)
    expect(operations).toMatch(/adminUsage\(from: \$from, to: \$to\)/)
    expect(operations).toMatch(/adminUserActivity\(userId: \$userId, first: \$first\)/)
    expect(operations).toMatch(/usersByIds\(ids: \$ids\)/)
    expect(operations).toMatch(/setAnalyticsOptOut\(optOut: \$optOut\)/)
    expect(operations).toMatch(/setGlobalRole\(input: \$input\)/)
    expect(operations).toMatch(/\$input: SetGlobalRoleInput!/)
    expect(operations).toMatch(/\$input: DecideDomainReviewInput!/)
    expect(operations).toMatch(/\$input: IngestAnalyticsInput!/)
    expect(operations).toMatch(/adminUsers\(status: \$status, search: \$search, first: \$first\)/)
    expect(operations).toMatch(/total\s+users/)
    expect(source).toMatch(/BLOCKED_OR_SUSPENDED/)
    expect(source).toMatch(/reason: string/)
    expect(operations).toMatch(/adminUpdateUser\(input: \$input\)/)
    expect(operations).toMatch(/adminSetAccountStanding\(input: \$input\)/)
    expect(operations).toMatch(/adminDeleteUser\(input: \$input\)/)
    expect(operations).toMatch(/\$input: AdminUpdateUserInput!/)
    expect(operations).toMatch(/\$input: AdminSetAccountStandingInput!/)
    expect(operations).toMatch(/\$input: AdminDeleteUserInput!/)
    expect(`${source}\n${operations}`).not.toMatch(/adminAccounts|updateAdminAccount|setAccountBlocked|deleteAdminAccount|confirmEmail|ageCheck/)
    expect(source).not.toMatch(/(?:query|mutation)\s+[A-Z][A-Za-z0-9_]*\s*(\(|\{)/)
  })
})
