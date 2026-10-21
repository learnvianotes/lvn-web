import { describe, expect, it } from 'vitest'
import { missingLegalFields } from '@/config/legal'
import { launchProblems } from '@/lib/launch-checks'

const filled = { operator: 'Asha Rao', address: '1 MG Road, Bengaluru, Karnataka 560001', courtsCity: 'Bengaluru', grievanceOfficer: 'Asha Rao', email: 'grievance@learnvianotes.in' }

describe('missingLegalFields', () => {
  it('lists the blank ones, spaces counting as blank', () => {
    expect(missingLegalFields({ ...filled, address: ' ', email: '' })).toEqual(['address', 'email'])
    expect(missingLegalFields(filled)).toEqual([])
  })
})

describe('launchProblems (lvn-backend ADR-0093)', () => {
  it('stops a production build while a legal detail is blank, naming it', () => {
    const [problem] = launchProblems({ appEnv: 'production', legal: { ...filled, grievanceOfficer: '' } })
    expect(problem).toMatch(/Grievance Officer’s name/)
  })

  it('lets a production build with every detail through', () => {
    expect(launchProblems({ appEnv: 'production', legal: filled })).toEqual([])
  })

  it('lets other builds through with the gaps shown on the pages', () => {
    expect(launchProblems({ appEnv: 'sandbox', legal: { ...filled, operator: '' } })).toEqual([])
    expect(launchProblems({ appEnv: 'development' })).toEqual([])
  })
})
