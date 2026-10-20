import { describe, expect, it } from 'vitest'
import { blankLegalFields, projectProblem } from './launch-checks'

describe('projectProblem', () => {
  const prod = 'learnvianotes-2e2d7'
  it('a production build needs the production project', () => {
    expect(projectProblem('production', prod, prod)).toBe('')
    expect(projectProblem('production', 'learnvianotes-test', prod)).toMatch(/must use the production/)
    expect(projectProblem('production', '', prod)).toMatch(/must use the production/)
  })
  it('any other build must not touch it', () => {
    expect(projectProblem('test', prod, prod)).toMatch(/must not use the production/)
    expect(projectProblem('test', 'learnvianotes-test', prod)).toBe('')
    expect(projectProblem('test', '', prod)).toBe('') // CI's build check has no Firebase keys
  })
})

describe('blankLegalFields', () => {
  it('lists the blank ones', () => {
    expect(blankLegalFields({ operator: 'A', address: ' ', email: '' })).toEqual(['address', 'email'])
  })
})
