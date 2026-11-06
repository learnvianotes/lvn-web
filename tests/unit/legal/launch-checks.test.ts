import { describe, expect, it } from 'vitest'
import { missingLegalFields } from '@/config/legal'
import { firebaseProblem, isLocalSite, launchProblems, productionFirebaseProject, transportProblem } from '@/lib/launch-checks'

const filled = { operator: 'Asha Rao', address: '1 MG Road, Bengaluru, Karnataka 560001', courtsCity: 'Bengaluru', grievanceOfficer: 'Asha Rao', email: 'grievance@learnvianotes.in' }

describe('missingLegalFields', () => {
  it('lists the blank ones, spaces counting as blank', () => {
    expect(missingLegalFields({ ...filled, address: ' ', email: '' })).toEqual(['address', 'email'])
    expect(missingLegalFields(filled)).toEqual([])
  })

  it('config/legal.ts has every detail a production build needs', () => {
    expect(missingLegalFields()).toEqual([])
  })
})

const prod = 'learnvianotes-in'

describe('firebaseProblem (lvn-backend ADR-0093)', () => {
  it('a production build needs the production project', () => {
    expect(firebaseProblem('production', prod, prod)).toBe('')
    expect(firebaseProblem('production', 'learnvianotes-test', prod)).toMatch(/must use the production/)
    expect(firebaseProblem('production', '', prod)).toMatch(/must use the production/)
  })

  it('any other build must not touch it', () => {
    expect(firebaseProblem('sandbox', prod, prod)).toMatch(/must not use the production/)
    expect(firebaseProblem('development', prod, prod)).toMatch(/must not use the production/)
    expect(firebaseProblem('sandbox', 'learnvianotes-test', prod)).toBe('')
    // CI's build check has no Google sign-in.
    expect(firebaseProblem('development', '', prod)).toBe('')
  })

  it('reads the production project from config/firebase-projects.json', () => {
    expect(productionFirebaseProject()).toBe(prod)
  })
})

describe('launchProblems (lvn-backend ADR-0093)', () => {
  it('stops a production build while a legal detail is blank, naming it', () => {
    const [problem] = launchProblems({ appEnv: 'production', firebaseProject: prod, legal: { ...filled, grievanceOfficer: '' } })
    expect(problem).toMatch(/Grievance Officer’s name/)
  })

  it('lets a production build with every detail and the production project through', () => {
    expect(launchProblems({ appEnv: 'production', firebaseProject: prod, legal: filled })).toEqual([])
  })

  it('reports a wrong project beside blank details', () => {
    expect(launchProblems({ appEnv: 'production', firebaseProject: 'learnvianotes-test', legal: { ...filled, email: '' } })).toHaveLength(2)
  })

  it('a production build for this machine (Lighthouse) is not a launch, and passes', () => {
    expect(launchProblems({ appEnv: 'production', siteUrl: 'http://localhost:3102', legal: { ...filled, operator: '' } })).toEqual([])
    expect(isLocalSite('http://127.0.0.1:3000/')).toBe(true)
    expect(isLocalSite('https://www.learnvianotes.in')).toBe(false)
    expect(isLocalSite('https://localhost.example.com')).toBe(false)
    // A real address is checked whatever else is set.
    expect(launchProblems({ appEnv: 'production', siteUrl: 'https://www.learnvianotes.in', firebaseProject: prod, legal: { ...filled, operator: '' } })).toHaveLength(1)
  })

  it('refuses a production launch whose site, API, or live socket is cleartext', () => {
    expect(transportProblem('api', 'http://api.learnvianotes.in/graphql')).toMatch(/https:\/\//)
    expect(transportProblem('live', 'ws://live.learnvianotes.in/graphql/live')).toMatch(/wss:\/\//)
    expect(transportProblem('site', 'https://www.learnvianotes.in')).toBeNull()
    const problems = launchProblems({
      appEnv: 'production',
      siteUrl: 'https://www.learnvianotes.in',
      apiUrl: 'http://api.learnvianotes.in/graphql',
      liveUrl: 'ws://live.learnvianotes.in/graphql/live',
      firebaseProject: prod,
      legal: filled,
    })
    expect(problems.some((problem) => problem.includes('NEXT_PUBLIC_API_URL'))).toBe(true)
    expect(problems.some((problem) => problem.includes('NEXT_PUBLIC_LIVE_URL'))).toBe(true)
    expect(launchProblems({
      appEnv: 'production',
      siteUrl: 'https://www.learnvianotes.in',
      apiUrl: 'https://api.learnvianotes.in/graphql',
      liveUrl: 'wss://live.learnvianotes.in/graphql/live',
      firebaseProject: prod,
      legal: filled,
    })).toEqual([])
  })

  it('lets other builds through with the gaps shown on the pages', () => {
    expect(launchProblems({ appEnv: 'sandbox', firebaseProject: 'learnvianotes-test', legal: { ...filled, operator: '' } })).toEqual([])
    expect(launchProblems({ appEnv: 'development' })).toEqual([])
  })
})
