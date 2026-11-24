import { describe, expect, it } from 'vitest'
import { contentCsv, funnelCsv, growthCsv, overviewCsv, retentionCsv, subjectsCsv } from '@/features/admin/usage/csv'
import {
  addDays,
  csvCell,
  csvFileName,
  funnelRows,
  heat,
  istToday,
  lastDays,
  linePoints,
  niceMax,
  rangeIssue,
  rangeVariables,
  retentionWidth,
  share,
  sumSince,
  toCsv,
  valueOn,
  withShares,
} from '@/features/admin/usage/shape'

describe('usage dashboard: IST date range', () => {
  it('reads today in India Standard Time, not UTC', () => {
    // 20:00 UTC on 4 Nov is 01:30 on 5 Nov in IST.
    expect(istToday(new Date('2026-11-04T20:00:00.000Z'))).toBe('2026-11-05')
    expect(istToday(new Date('2026-11-04T18:00:00.000Z'))).toBe('2026-11-04')
  })

  it('builds the last N days, today included', () => {
    expect(lastDays(30, new Date('2026-11-04T20:00:00.000Z'))).toEqual({ from: '2026-10-07', to: '2026-11-05' })
    expect(lastDays(1, new Date('2026-11-05T06:00:00.000Z'))).toEqual({ from: '2026-11-05', to: '2026-11-05' })
    expect(addDays('2026-03-01', -1)).toBe('2026-02-28')
  })

  it('sends whole IST days as DateTime bounds', () => {
    expect(rangeVariables({ from: '2026-11-01', to: '2026-11-05' })).toEqual({ from: '2026-10-31T18:30:00.000Z', to: '2026-11-05T18:29:59.999Z' })
    expect(() => rangeVariables({ from: '', to: '2026-11-05' })).toThrow()
  })

  it('refuses incomplete, reversed and over-long ranges', () => {
    expect(rangeIssue({ from: '', to: '2026-11-05' })).toBe('incomplete')
    expect(rangeIssue({ from: '2026-11-06', to: '2026-11-05' })).toBe('order')
    expect(rangeIssue({ from: '2025-01-01', to: '2026-11-05' })).toBe('span')
    expect(rangeIssue({ from: '2025-11-05', to: '2026-11-05' })).toBeNull()
  })
})

describe('usage dashboard: shaping', () => {
  it('never invents a share from an empty denominator', () => {
    expect(share(3, 0)).toBeNull()
    expect(share(1, 4)).toBe(0.25)
  })

  it('picks and sums buckets by day', () => {
    const series = [
      { date: '2026-11-03', n: 2 },
      { date: '2026-11-04', n: 5 },
      { date: '2026-11-05', n: 7 },
    ]
    expect(valueOn(series, '2026-11-05', (p) => p.n)).toBe(7)
    expect(valueOn(series, '2026-11-06', (p) => p.n)).toBe(0)
    expect(sumSince(series, '2026-11-04', (p) => p.n)).toBe(12)
  })

  it('sorts a split largest first with each share', () => {
    const rows = withShares([{ m: 'EMAIL', u: 10 }, { m: 'GOOGLE', u: 30 }], (r) => r.u)
    expect(rows.map((r) => [r.row.m, r.share])).toEqual([['GOOGLE', 0.75], ['EMAIL', 0.25]])
  })

  it('computes funnel conversion from the first and the previous step', () => {
    expect(funnelRows([{ name: 'signed_up', users: 200 }, { name: 'email_verified', users: 150 }, { name: 'first_note', users: 60 }])).toEqual([
      { name: 'signed_up', users: 200, ofFirst: 1, ofPrevious: null },
      { name: 'email_verified', users: 150, ofFirst: 0.75, ofPrevious: 0.75 },
      { name: 'first_note', users: 60, ofFirst: 0.3, ofPrevious: 0.4 },
    ])
    expect(funnelRows([{ name: 'signed_up', users: 0 }, { name: 'first_note', users: 0 }])[1]).toEqual({ name: 'first_note', users: 0, ofFirst: null, ofPrevious: null })
  })

  it('rounds chart axes and maps values to SVG points', () => {
    expect(niceMax(0)).toBe(1)
    expect(niceMax(7)).toBe(10)
    expect(niceMax(130)).toBe(200)
    expect(niceMax(4100)).toBe(5000)
    expect(linePoints([0, 5, 10], 100, 50, 10)).toBe('0,50 50,25 100,0')
    expect(linePoints([3], 100, 50, 10)).toBe('50,35')
    expect(linePoints([], 100, 50, 10)).toBe('')
  })

  it('clamps heat and sizes the retention grid to the longest cohort', () => {
    expect(heat(1.4)).toBe(1)
    expect(heat(-1)).toBe(0)
    expect(heat(Number.NaN)).toBe(0)
    expect(retentionWidth([{ returned: [1, 0.5] }, { returned: [1] }])).toBe(2)
  })
})

describe('usage dashboard: CSV export', () => {
  it('quotes RFC 4180 cells and defuses spreadsheet formulas', () => {
    expect(csvCell('plain')).toBe('plain')
    expect(csvCell('a,b')).toBe('"a,b"')
    expect(csvCell('say "hi"')).toBe('"say ""hi"""')
    expect(csvCell('=HYPERLINK("x")')).toBe(`"'=HYPERLINK(""x"")"`)
    expect(csvCell('@SUM(A1)')).toBe("'@SUM(A1)")
    expect(csvCell(12)).toBe('12')
    expect(csvCell(null)).toBe('')
    expect(csvCell(Number.POSITIVE_INFINITY)).toBe('')
  })

  it('writes one table plainly and several with their names', () => {
    expect(toCsv({ name: 'x', header: ['a', 'b'], rows: [[1, 2]] })).toBe('a,b\r\n1,2\r\n')
    expect(toCsv([{ name: 'one', header: ['a'], rows: [[1]] }, { name: 'two', header: ['b'], rows: [[2]] }])).toBe('one\r\na\r\n1\r\n\r\ntwo\r\nb\r\n2\r\n')
    expect(csvFileName('growth', { from: '2026-10-07', to: '2026-11-05' })).toBe('lvn-usage-growth-2026-10-07_2026-11-05.csv')
  })

  it('exports aggregates only, with the hidden-group count', () => {
    const growth = growthCsv({
      adminGrowth: {
        generatedAt: '2026-11-05T00:00:00.000Z',
        interval: 'DAY',
        hiddenSmallGroups: 2,
        range: { firstDay: '2026-11-04', lastDay: '2026-11-05', timeZone: 'Asia/Kolkata' },
        totals: { signUps: 9, emailVerified: 8, registrationsCompleted: 7, verifications: 3 },
        series: [{ date: '2026-11-04', signUps: 4, emailVerified: 4, registrationsCompleted: 3, verifications: 1 }],
        signUpMethods: [{ method: 'GOOGLE', users: 6 }],
      },
    })
    const csv = toCsv(growth)
    expect(csv).toContain('bucket_start,sign_ups,email_verified,registrations_completed,verifications\r\n2026-11-04,4,4,3,1')
    expect(csv).toContain('method,users\r\nGOOGLE,6')
    expect(csv).toContain('hidden_small_groups\r\n2')
    expect(csv).not.toMatch(/[0-9a-f]{8}-[0-9a-f]{4}-/i)
  })

  it('leaves subject ids out and ranks subjects', () => {
    const csv = toCsv(
      subjectsCsv({
        adminTopSubjects: {
          generatedAt: '2026-11-05T00:00:00.000Z',
          by: 'LEARNING_TIME',
          hiddenSmallGroups: 3,
          range: { firstDay: '2026-11-01', lastDay: '2026-11-05', timeZone: 'Asia/Kolkata' },
          subjects: [{ subjectId: '01920000-0000-7000-8000-000000000001', title: 'Physics, Class 12', value: 420, users: 18 }],
        },
      }),
    )
    expect(csv).toContain('rank,subject,value_learning_time,people\r\n1,"Physics, Class 12",420,18')
    expect(csv).not.toContain('01920000')
    expect(csv).toContain('hidden_small_groups\r\n3')
  })

  it('pads retention rows and writes funnel conversions', () => {
    const r = toCsv(retentionCsv({ adminRetention: { generatedAt: '', firstWeek: '2026-10-26', lastWeek: '2026-11-02', timeZone: 'Asia/Kolkata', hiddenSmallGroups: 1, cohorts: [{ start: '2026-10-26', size: 12, returned: [1, 0.5] }, { start: '2026-11-02', size: 8, returned: [1] }] } }))
    expect(r).toContain('cohort_week,size,week_0,week_1\r\n2026-10-26,12,1,0.5\r\n2026-11-02,8,1,\r\n')
    const f = toCsv(funnelCsv({ adminFunnel: [{ name: 'signed_up', users: 10 }, { name: 'first_note', users: 5 }] }))
    expect(f).toBe('step,people,of_first_step,of_previous_step\r\nsigned_up,10,1,\r\nfirst_note,5,0.5,0.5\r\n')
  })

  it('exports the overview KPIs and the content counts', () => {
    const o = toCsv(
      overviewCsv(
        {
          adminMetrics: { generatedAt: '', users: { total: 1000, newLast7Days: 40, newLast30Days: 120, active: 300 } },
          adminEngagement: { dau: 50, wau: 200, mau: 400, stickiness: 0.125, range: { firstDay: '', lastDay: '', timeZone: 'Asia/Kolkata' } },
          adminGrowth: { totals: { signUps: 120, verifications: 30 }, series: [] },
        },
        null,
        6,
      ),
    )
    expect(o).toContain('users_total,1000')
    expect(o).toContain('new_today,6')
    expect(o).toContain('stickiness,0.125')
    expect(o).toContain('verifications_per_sign_up,0.25')
    const c = toCsv(
      contentCsv({
        adminContentStats: {
          generatedAt: '',
          range: { firstDay: '', lastDay: '', timeZone: '' },
          notes: { created: 10, private: 4, shared: 2, unlisted: 1, public: 3 },
          uploads: { files: 6, bytes: '2048', hiddenSmallGroups: 1, byPurpose: [{ purpose: 'ATTACHMENT', files: 6, bytes: '2048' }] },
          doubts: { asked: 5, answered: 4, resolved: 2, answers: 9, medianHoursToFirstAnswer: null },
          places: { groups: 1, groupPosts: 2, classrooms: 3, classroomPosts: 4 },
          sharing: { noteShares: 5, placeShares: 6, saves: 7 },
          scans: { clean: 6, pending: 0, failed: 0, infected: 0 },
        },
      }),
    )
    expect(c).toContain('notes_created,10')
    expect(c).toContain('median_hours_to_first_answer,\r\n')
    expect(c).toContain('purpose,files,bytes\r\nATTACHMENT,6,2048')
  })
})
