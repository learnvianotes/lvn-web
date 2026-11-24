import { execFileSync } from 'node:child_process'
import { describe, expect, it } from 'vitest'

describe('graphql operations', () => {
  it('validates every operation document against graphql/schema.graphql and rejects a hand-written request', () => {
    const out = execFileSync('node', ['scripts/graphql-check.mjs'], { encoding: 'utf8' })
    expect(out).toMatch(/graphql:check ok/)
  })
})
