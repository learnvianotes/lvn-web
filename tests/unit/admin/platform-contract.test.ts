import { readFileSync } from 'node:fs'
import { describe, expect, it } from 'vitest'
import { STUDENT_ID_AI_SETTING_KEYS } from '@/lib/platform-api'

describe('platform API names', () => {
  const source = readFileSync('lib/platform-api.ts', 'utf8')

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
    expect(source).toMatch(/aiCheck \{/)
    expect(source).toMatch(/extracted \{ name institution idNumber validUntil \}/)
    expect(source).not.toMatch(/aiReasons|aiVerdict|ingestEvents|adminUserTimeline|topPages/)
    expect(source).toMatch(/institutionDomains\(status: \$status\)/)
    expect(source).toMatch(/reviewInstitutionDomain\(input: \$input\)/)
    expect(source).toMatch(/ingestAnalytics\(input: \$input\)/)
    expect(source).toMatch(/adminErrors\(since: \$since\)/)
    expect(source).toMatch(/adminUsage\(from: \$from, to: \$to\)/)
    expect(source).toMatch(/adminUserActivity\(userId: \$userId, first: \$first\)/)
    expect(source).toMatch(/usersByIds\(ids: \$ids\)/)
    expect(source).toMatch(/setAnalyticsOptOut\(optOut: \$optOut\)/)
    expect(source).toMatch(/setGlobalRole\(input: \$input\)/)
    expect(source).toMatch(/\$input: SetGlobalRoleInput!/)
    expect(source).toMatch(/\$input: DecideDomainReviewInput!/)
    expect(source).toMatch(/\$input: IngestAnalyticsInput!/)
  })
})
