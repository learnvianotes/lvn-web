// @vitest-environment happy-dom
import { act } from 'react'
import { createRoot, type Root } from 'react-dom/client'
import { NextIntlClientProvider } from 'next-intl'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import messages from '@/messages/en.json'
import * as docs from '@/graphql/generated/graphql'
import { AdminUsage } from '@/features/admin/AdminUsage'

// React's act() warns unless the environment says it is a test.
;(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const range = { firstDay: '2026-10-07', lastDay: '2026-11-05', timeZone: 'Asia/Kolkata' }
const at = '2026-11-05T04:00:00.000Z'

const fixtures = new Map<unknown, unknown>([
  [docs.ViewerDocument, { viewer: { globalRole: 'PLATFORM_ADMIN' } }],
  [
    docs.AdminUsageOverviewDocument,
    {
      adminMetrics: { generatedAt: at, users: { total: 12345, newLast7Days: 210, newLast30Days: 800, active: 4000 } },
      adminEngagement: { dau: 128, wau: 640, mau: 2104, stickiness: 0.183, range },
      adminGrowth: { totals: { signUps: 800, verifications: 200 }, series: [] },
    },
  ],
  [docs.AdminUsageDocument, { adminUsage: { dau: 128, wau: 640, mau: 2104, from: at, to: at, topEvents: [{ name: 'note_open', count: 90 }], topFeatures: [{ name: 'flashcards', count: 40 }] } }],
  [
    docs.AdminUsageGrowthDocument,
    {
      adminGrowth: {
        generatedAt: at,
        interval: 'DAY',
        hiddenSmallGroups: 1,
        range,
        totals: { signUps: 30, emailVerified: 25, registrationsCompleted: 20, verifications: 6 },
        series: [
          { date: '2026-11-04', signUps: 10, emailVerified: 9, registrationsCompleted: 8, verifications: 2 },
          { date: '2026-11-05', signUps: 20, emailVerified: 16, registrationsCompleted: 12, verifications: 4 },
        ],
        signUpMethods: [{ method: 'GOOGLE', users: 18 }, { method: 'EMAIL', users: 12 }],
      },
    },
  ],
  [docs.AdminUsageEngagementDocument, { adminEngagement: { generatedAt: at, interval: 'DAY', dau: 128, wau: 640, mau: 2104, stickiness: 0.2, range, series: [{ date: '2026-11-05', activeUsers: 128, learningMinutes: 900, quizAttempts: 40, notesCreated: 12, doubtsAsked: 3, doubtsAnswered: 2 }] } }],
  [
    docs.AdminUsageSubjectsDocument,
    { adminTopSubjects: { generatedAt: at, by: 'NOTES', hiddenSmallGroups: 2, range, subjects: [{ subjectId: '01920000-0000-7000-8000-000000000001', title: 'Organic Chemistry', value: 77, users: 21 }] } },
  ],
  [docs.AdminUsageRetentionDocument, { adminRetention: { generatedAt: at, firstWeek: '2026-08-17', lastWeek: '2026-11-02', timeZone: 'Asia/Kolkata', hiddenSmallGroups: 0, cohorts: [{ start: '2026-10-26', size: 40, returned: [1, 0.425] }] } }],
  [
    docs.AdminUsageContentDocument,
    {
      adminContentStats: {
        generatedAt: at,
        range,
        notes: { created: 321, private: 100, shared: 50, unlisted: 20, public: 151 },
        uploads: { files: 40, bytes: '1048576', hiddenSmallGroups: 0, byPurpose: [{ purpose: 'ATTACHMENT', files: 40, bytes: '1048576' }] },
        doubts: { asked: 30, answered: 25, resolved: 12, answers: 60, medianHoursToFirstAnswer: 3.5 },
        places: { groups: 4, groupPosts: 9, classrooms: 2, classroomPosts: 7 },
        sharing: { noteShares: 11, placeShares: 3, saves: 90 },
        scans: { clean: 40, pending: 0, failed: 0, infected: 0 },
      },
    },
  ],
  [
    docs.AdminUsageVerificationDocument,
    { adminVerificationStats: { generatedAt: at, range, requested: 50, approved: 30, rejected: 10, pending: 10, medianHoursToDecision: 20.5, oldestPendingHours: 48, hiddenSmallGroups: 0, byMethod: [{ method: 'COLLEGE_ID', requested: 50, approved: 30, rejected: 10 }] } },
  ],
  [docs.AdminUsageFunnelDocument, { adminFunnel: [{ name: 'signed_up', users: 100 }, { name: 'email_verified', users: 80 }] }],
  [
    docs.AdminUsageFeaturesDocument,
    {
      adminFeatureUsage: {
        generatedAt: at,
        range,
        events: 900,
        hiddenSmallGroups: 3,
        features: [{ feature: 'PDF_VIEWER', users: 61, events: 400 }, { feature: 'FLASHCARDS_REVIEW', users: 22, events: 90 }],
        quizStarts: { starts: 75, hiddenSmallGroups: 1, byKind: [{ kind: 'SHARED', users: 9, starts: 30 }] },
      },
    },
  ],
  [
    docs.AdminUsageSearchQualityDocument,
    {
      adminSearchQuality: {
        generatedAt: at,
        range,
        searches: 200,
        zeroResults: 30,
        zeroResultRate: 0.15,
        hiddenSmallGroups: 2,
        byScope: [{ scope: 'NOTES', users: 40, searches: 150, zeroResults: 20, zeroResultRate: 0.133 }, { scope: null, users: 12, searches: 50, zeroResults: 10, zeroResultRate: 0.2 }],
      },
    },
  ],
  [
    docs.AdminUsageVersionsDocument,
    {
      adminVersionAdoption: {
        generatedAt: at,
        range,
        hiddenSmallGroups: 4,
        platforms: [{ platform: 'WEB', users: 300, events: 5000, versions: [{ appVersion: '0.2.0', users: 250, events: 4000, share: 0.833 }, { appVersion: null, users: 60, events: 1000, share: 0.2 }] }],
      },
    },
  ],
])

const api = vi.hoisted(() => ({ calls: [] as { doc: unknown; variables: unknown }[], fail: new Map<unknown, unknown>(), role: 'PLATFORM_ADMIN' as string | null }))

vi.mock('@apollo/client/react', () => ({
  useQuery: (doc: unknown, options?: { variables?: unknown }) => {
    api.calls.push({ doc, variables: options?.variables })
    if (doc === docs.ViewerDocument) return { data: { viewer: { globalRole: api.role } }, loading: false }
    const error = api.fail.get(doc)
    return { data: error ? undefined : fixtures.get(doc), previousData: undefined, error, loading: false, refetch: vi.fn() }
  },
}))

vi.mock('@/lib/platform-api', async (orig) => ({ ...(await orig<typeof import('@/lib/platform-api')>()), loadUserTimeline: vi.fn(async () => [{ name: 'page_view', platform: 'WEB', occurredAt: at }]) }))

describe('admin usage dashboard (/admin/usage)', () => {
  let root: Root | undefined
  let container: HTMLDivElement | undefined

  beforeEach(() => {
    api.calls = []
    api.fail = new Map()
    api.role = 'PLATFORM_ADMIN'
  })
  afterEach(() => {
    if (root) act(() => root!.unmount())
    container?.remove()
    root = undefined
    container = undefined
  })

  async function mount() {
    container = document.createElement('div')
    document.body.appendChild(container)
    root = createRoot(container)
    await act(async () =>
      root!.render(
        <NextIntlClientProvider locale="en" messages={messages} timeZone="Asia/Kolkata">
          <AdminUsage />
        </NextIntlClientProvider>,
      ),
    )
    return container
  }
  const tab = (name: string) => [...container!.querySelectorAll('[role="tab"]')].find((b) => b.textContent === name) as HTMLButtonElement
  const button = (name: string) => [...container!.querySelectorAll('button')].find((b) => b.textContent === name) as HTMLButtonElement | undefined
  const click = (el: HTMLElement) => act(async () => el.click())
  const queried = () => new Set(api.calls.map((c) => c.doc))

  it('opens on the overview KPIs and queries nothing for the other tabs', async () => {
    const view = await mount()
    const text = view.textContent ?? ''
    expect(tab('Overview').getAttribute('aria-selected')).toBe('true')
    for (const v of ['12,345', '210', '128', '640', '2,104', '18.3%', '25%', 'flashcards', 'note_open']) expect(text).toContain(v)
    expect(queried().has(docs.AdminUsageGrowthDocument)).toBe(false)
    expect(queried().has(docs.AdminUsageRetentionDocument)).toBe(false)
    // IST whole days: the default range starts at 00:00 IST (18:30 UTC the day before).
    const overview = api.calls.find((c) => c.doc === docs.AdminUsageOverviewDocument)!.variables as { from: string; to: string }
    expect(overview.from).toMatch(/T18:30:00\.000Z$/)
    expect(overview.to).toMatch(/T18:29:59\.999Z$/)
  })

  it('renders every tab with its own query', async () => {
    await mount()
    const expectations: [string, unknown, string][] = [
      ['Growth', docs.AdminUsageGrowthDocument, 'Sign-ups over time'],
      ['Engagement', docs.AdminUsageEngagementDocument, 'Learning minutes'],
      ['Content', docs.AdminUsageContentDocument, '1 MB'],
      ['Subjects', docs.AdminUsageSubjectsDocument, 'Organic Chemistry'],
      ['Retention', docs.AdminUsageRetentionDocument, '42.5%'],
      ['Verification', docs.AdminUsageVerificationDocument, 'College ID'],
      ['Funnel', docs.AdminUsageFunnelDocument, 'Verified their email'],
    ]
    for (const [name, doc, needle] of expectations) {
      await click(tab(name))
      expect(tab(name).getAttribute('aria-selected')).toBe('true')
      expect(queried().has(doc)).toBe(true)
      expect(container!.querySelector('[role="tabpanel"]')!.textContent).toContain(needle)
      if (name === 'Retention') expect(container!.querySelector('[data-testid="retention-heatmap"] caption')?.textContent).toBe('Weekly retention by sign-up week')
    }
  })

  it('shows feature use, search quality and app versions with their hidden groups', async () => {
    await mount()
    expect(queried().has(docs.AdminUsageFeaturesDocument)).toBe(false)
    const panel = () => container!.querySelector('[role="tabpanel"]')!
    const hidden = () => [...container!.querySelectorAll('[data-testid="hidden-groups"]')].map((n) => n.textContent)

    await click(tab('Features'))
    expect(queried().has(docs.AdminUsageFeaturesDocument)).toBe(true)
    for (const v of ['PDF reader', '61 people · 400 uses', 'Flashcard review', 'Shared quiz', '75']) expect(panel().textContent).toContain(v)
    expect(hidden()).toEqual(['3 small groups hidden (fewer than 5 people each).', '1 small group hidden (fewer than 5 people each).'])

    await click(tab('Search quality'))
    for (const v of ['200', '15%', 'Notes', '13.3%', 'No scope sent (older app)', 'never what was searched']) expect(panel().textContent).toContain(v)
    expect(hidden()).toEqual(['2 small groups hidden (fewer than 5 people each).'])

    await click(tab('Versions'))
    for (const v of ['Web: 300 people, 5,000 events', '0.2.0', '83.3%', 'No version sent']) expect(panel().textContent).toContain(v)
    expect(hidden()).toEqual(['4 small groups hidden (fewer than 5 people each).'])
    const vars = api.calls.find((c) => c.doc === docs.AdminUsageVersionsDocument)!.variables as { from: string; to: string }
    expect(vars.from).toMatch(/T18:30:00\.000Z$/)
  })

  it('exports the new tabs with lower-case ids and their hidden counts', async () => {
    const blobs: Blob[] = []
    const create = vi.spyOn(URL, 'createObjectURL').mockImplementation((b) => (blobs.push(b as Blob), 'blob:x'))
    const revoke = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    await mount()
    for (const name of ['Features', 'Search quality', 'Versions']) {
      await click(tab(name))
      await click(button('Export CSV')!)
    }
    const [features, search, versions] = await Promise.all(blobs.map((b) => b.text()))
    expect(features).toContain('feature,users,events')
    expect(features).toContain('pdf_viewer,61,400')
    expect(features).toContain('shared,9,30')
    expect(search).toContain('scope,users,searches,zero_results,zero_result_rate')
    expect(search).toContain('none,12,50,10,0.2')
    expect(versions).toContain('platform,app_version,users,share,events')
    expect(versions).toContain('WEB,none,60,0.2,1000')
    for (const csv of [features, search, versions]) expect(csv).toContain('hidden_small_groups')
    create.mockRestore()
    revoke.mockRestore()
  })

  it('draws charts with a table of the same figures', async () => {
    await mount()
    await click(tab('Growth'))
    expect(container!.querySelector('svg[data-testid="line-chart"]')?.getAttribute('aria-hidden')).toBe('true')
    const table = container!.querySelector('figure table')!
    expect(table.textContent).toContain('2026-11-05')
    expect(table.textContent).toContain('20')
    expect(container!.textContent).toContain('18 (60%)')
  })

  it('says how many small groups were hidden (k-anonymity 5)', async () => {
    await mount()
    await click(tab('Subjects'))
    expect(container!.querySelector('[data-testid="hidden-groups"]')?.textContent).toBe('2 small groups hidden (fewer than 5 people each).')
    await click(tab('Growth'))
    expect(container!.querySelector('[data-testid="hidden-groups"]')?.textContent).toBe('1 small group hidden (fewer than 5 people each).')
    await click(tab('Retention'))
    expect(container!.querySelector('[data-testid="hidden-groups"]')).toBeNull()
  })

  it('passes the interval and the chosen ranking to the API', async () => {
    await mount()
    await click(tab('Growth'))
    await click(button('Week')!)
    expect((api.calls.filter((c) => c.doc === docs.AdminUsageGrowthDocument).at(-1)!.variables as { interval: string }).interval).toBe('WEEK')
    await click(tab('Subjects'))
    await click(button('Saves')!)
    expect((api.calls.filter((c) => c.doc === docs.AdminUsageSubjectsDocument).at(-1)!.variables as { by: string }).by).toBe('SAVES')
  })

  it('exports the tab as CSV in the browser', async () => {
    const blobs: Blob[] = []
    const create = vi.spyOn(URL, 'createObjectURL').mockImplementation((b) => (blobs.push(b as Blob), 'blob:x'))
    const revoke = vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => {})
    await mount()
    await click(tab('Subjects'))
    await click(button('Export CSV')!)
    expect(blobs).toHaveLength(1)
    const csv = await blobs[0]!.text()
    expect(csv).toContain('rank,subject,value_notes,people')
    expect(csv).toContain('1,Organic Chemistry,77,21')
    expect(csv).not.toContain('01920000')
    create.mockRestore()
    revoke.mockRestore()
  })

  it('keeps the per-person timeline behind "Look up a user"', async () => {
    await mount()
    expect(container!.querySelector('#user-timeline')).toBeNull()
    await click(button('Look up a user')!)
    expect(container!.querySelector('#user-timeline')?.textContent).toBe("One person's activity")
    expect(button('Hide user lookup')?.getAttribute('aria-expanded')).toBe('true')
  })

  it('refuses a bad range without querying it', async () => {
    const view = await mount()
    const [from, to] = [...view.querySelectorAll('input[type="date"]')] as [HTMLInputElement, HTMLInputElement]
    const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!
    await act(async () => {
      setter.call(from, '2026-11-10')
      from.dispatchEvent(new Event('input', { bubbles: true }))
      setter.call(to, '2026-11-01')
      to.dispatchEvent(new Event('input', { bubbles: true }))
    })
    const before = api.calls.filter((c) => c.doc === docs.AdminUsageOverviewDocument).map((c) => JSON.stringify(c.variables))
    await click(button('Apply')!)
    expect(view.querySelector('[role="alert"]')?.textContent).toBe('The start day must be on or before the end day.')
    const after = api.calls.filter((c) => c.doc === docs.AdminUsageOverviewDocument).map((c) => JSON.stringify(c.variables))
    expect(new Set(after)).toEqual(new Set(before))
  })

  it('shows a refusal for FORBIDDEN and nothing for non-admins', async () => {
    const { CombinedGraphQLErrors } = await import('@apollo/client/errors')
    api.fail.set(docs.AdminUsageOverviewDocument, new CombinedGraphQLErrors({ errors: [{ message: 'no', extensions: { code: 'FORBIDDEN' } }] }))
    let view = await mount()
    expect(view.querySelector('[role="tabpanel"]')?.textContent).toBe('You cannot view usage.')
    act(() => root!.unmount())
    root = undefined
    api.role = 'STUDENT'
    view = await mount()
    expect(view.textContent).toBe('You cannot view usage.')
    expect(queried().has(docs.AdminUsageGrowthDocument)).toBe(false)
  })
})
