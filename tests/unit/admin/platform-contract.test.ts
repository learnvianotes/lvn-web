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
    expect(source).not.toMatch(/aiCheckEnabled|autoApproveOnHighConfidence|AiVerificationSettings/)
  })

  it('asks for the verdict columns and the schema fields that already exist', () => {
    expect(source).toMatch(/aiVerdict/)
    expect(source).toMatch(/aiConfidence/)
    expect(source).toMatch(/aiReasons/)
    expect(source).toMatch(/aiCheckedAt/)
    expect(source).not.toMatch(/aiExtracted|aiReason[^s]/)
    expect(source).toMatch(/domainReviews\(status: \$status\)/)
    expect(source).toMatch(/decideDomainReview\(input: \$input\)/)
    expect(source).toMatch(/setGlobalRole\(input: \$input\)/)
    expect(source).toMatch(/\$input: SetGlobalRoleInput!/)
    expect(source).toMatch(/\$input: DecideDomainReviewInput!/)
  })
})
