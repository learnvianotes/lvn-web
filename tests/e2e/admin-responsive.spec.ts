import { expect, test, type Page } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * Every admin page at the widths the product is used at, in both themes.
 * The document and the scrolling main must not be wider than the viewport, and the top bar stays above the title.
 */

const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const constraints = (over: Record<string, unknown> = {}) => ({ __typename: 'AdminSettingConstraints', min: null, max: null, maxLength: null, pattern: null, nullable: false, ...over })
const setting = (over: Record<string, unknown>) => ({
  __typename: 'AdminSetting',
  description: 'A platform setting.',
  value: 'true',
  overridden: false,
  updatedAt: '2026-10-01T00:00:00.000Z',
  constraints: constraints(),
  ...over,
})
const usage = (over: Record<string, unknown>) => ({ tasksRun: 0, failures: 0, promptTokens: '0', completionTokens: '0', costMicroUsd: '0', ...over })
const preset = (kind: string, name: string, over: Record<string, unknown> = {}) => ({
  __typename: 'AiProviderPreset',
  kind,
  name,
  defaultBaseUrl: null,
  needsKey: true,
  canEmbed: true,
  canHear: true,
  privateByDefault: false,
  chatModels: [] as string[],
  embedModels: [] as string[],
  ...over,
})

const VIEWPORTS = [
  { width: 320, height: 568 },
  { width: 375, height: 667 },
  { width: 390, height: 844 },
  { width: 412, height: 915 },
  { width: 768, height: 1024 },
  { width: 1024, height: 768 },
  { width: 1280, height: 800 },
  { width: 1440, height: 900 },
  { width: 1920, height: 1080 },
]
const PAGES: { path: string; heading: string; shot?: string; admin?: boolean }[] = [
  { path: '/admin', heading: 'Overview', shot: 'overview' },
  { path: '/admin/settings', heading: 'Configuration', shot: 'configuration' },
  { path: '/admin/plans', heading: 'Plans & pricing', shot: 'plans' },
  { path: '/admin/access', heading: 'Beta access', shot: 'access' },
  { path: '/admin/users', heading: 'Users' },
  { path: '/admin/errors', heading: 'Errors' },
  { path: '/admin/usage', heading: 'Usage' },
  { path: '/admin/roles', heading: 'Roles' },
  { path: '/admin/domains', heading: 'Institution domains' },
  { path: '/admin/student-id', heading: 'College ID cards' },
  { path: '/plans', heading: 'Plans', shot: 'user-plans', admin: false },
  { path: '/admin/ai', heading: 'AI providers' },
  { path: '/admin/verification', heading: 'Proof of study to review' },
  { path: '/admin/moderation', heading: 'Moderation queue' },
  { path: '/admin/contests', heading: 'Weekly contests' },
]
const SHOT_WIDTHS = new Set([320, 768, 1280, 1920])

async function adminApi(page: Page) {
  await mockApi(
    page,
    {
      AdminMetrics: () => ({
        adminMetrics: {
          __typename: 'AdminMetrics',
          generatedAt: '2026-10-23T18:00:00.000Z',
          users: { __typename: 'AdminUserMetrics', total: 12840, newLast7Days: 312, newLast30Days: 1402, active: 4201 },
          content: { __typename: 'AdminContentMetrics', notes: 58012, publicNotes: 6400, subjects: 18, topics: 940, groups: 126, classrooms: 84 },
          ai: {
            __typename: 'AdminAiMetrics',
            from: '2026-09-24T00:00:00.000Z',
            to: '2026-10-23T18:00:00.000Z',
            ...usage({ tasksRun: 18420, failures: 210, promptTokens: '84200120', completionTokens: '12004400', costMicroUsd: '18650000' }),
            byProvider: [{ __typename: 'AdminAiProviderUsage', provider: 'ANTHROPIC', ...usage({ tasksRun: 12000, failures: 80, promptTokens: '50000000', completionTokens: '8000000', costMicroUsd: '15000000' }) }],
            byModel: [{ __typename: 'AdminAiModelUsage', provider: 'ANTHROPIC', model: 'claude-sonnet-5-5', ...usage({ tasksRun: 12000, failures: 80, promptTokens: '50000000', completionTokens: '8000000', costMicroUsd: '15000000' }) }],
            byTask: [{ __typename: 'AdminAiTaskUsage', task: 'SUMMARIZE', ...usage({ tasksRun: 9000, failures: 40, promptTokens: '20000000', completionTokens: '4000000', costMicroUsd: '8000000' }) }],
          },
          storage: { __typename: 'AdminStorageMetrics', bytes: '12884901888', files: 40211 },
          verification: { __typename: 'AdminVerificationMetrics', studentIdQueue: 7, pendingRequests: 3, domainReviews: 2 },
          moderation: { __typename: 'AdminModerationMetrics', openReports: 4, openAppeals: 1 },
        },
      }),
      AdminSettings: () => ({
        adminSettings: [
          setting({ key: 'google_sign_in', type: 'BOOLEAN', category: 'auth', description: 'Let people sign in with Google.' }),
          setting({ key: 'access_allowlist_enabled', type: 'BOOLEAN', category: 'auth', description: 'Only listed emails can sign in.', value: 'true' }),
          setting({ key: 'uploads_enabled', type: 'BOOLEAN', category: 'uploads', description: 'Allow files to be uploaded.' }),
          setting({ key: 'search_timeout_ms', type: 'INTEGER', category: 'search', description: 'How long a search may take.', value: '1500', overridden: true, constraints: constraints({ min: 100, max: 10000 }) }),
          setting({ key: 'account_minimum_age', type: 'INTEGER', category: 'accounts', description: 'Youngest age that can register.', value: '18', constraints: constraints({ min: 0, max: 120 }) }),
        ],
      }),
      AdminAccessAllowlist: () => ({
        adminAccessAllowlist: [
          { __typename: 'AccessAllowlistEntry', id: '01920000-0000-7000-8000-000000000a01', email: 'asha@example.com', role: 'PLATFORM_ADMIN', note: 'Owner', hasAccount: true, addedByEmail: null, createdAt: '2026-10-01T00:00:00.000Z' },
          { __typename: 'AccessAllowlistEntry', id: '01920000-0000-7000-8000-000000000a02', email: 'student@college.edu', role: 'STUDENT', note: null, hasAccount: true, addedByEmail: 'asha@example.com', createdAt: '2026-10-02T00:00:00.000Z' },
        ],
      }),
      Plans: () => ({
        plans: [
          { __typename: 'PublicPlan', id: '01920000-0000-7000-8000-000000000f01', code: 'FREE', name: 'Free', priceMinor: 0, currency: 'INR', interval: 'NONE', features: ['Read public notes'], current: true, limits: [{ __typename: 'PlanLimit', key: 'NOTES_OWNED', label: 'Notes you can keep', limit: '20' }] },
          { __typename: 'PublicPlan', id: '01920000-0000-7000-8000-000000000f02', code: 'PLUS', name: 'Plus', priceMinor: 49900, currency: 'INR', interval: 'MONTH', features: ['AI on your notes'], current: false, limits: [{ __typename: 'PlanLimit', key: 'AI_REQUESTS_DAILY', label: 'AI asks a day', limit: null }] },
        ],
      }),
      MyPlan: () => ({
        myPlan: {
          __typename: 'MyPlan',
          plan: { __typename: 'PublicPlan', id: '01920000-0000-7000-8000-000000000f01', code: 'FREE', name: 'Free', priceMinor: 0, currency: 'INR', interval: 'NONE', features: ['Read public notes'], current: true, limits: [{ __typename: 'PlanLimit', key: 'NOTES_OWNED', label: 'Notes you can keep', limit: '20' }] },
          usage: [
            { __typename: 'PlanUsage', key: 'NOTES_OWNED', label: 'Notes you can keep', used: '12', limit: '20', resetsAt: null },
            { __typename: 'PlanUsage', key: 'AI_REQUESTS_DAILY', label: 'AI asks a day', used: '7', limit: '20', resetsAt: '2026-10-24T00:00:00.000Z' },
          ],
        },
      }),
      AdminPlans: () => ({
        adminPlans: [
          { __typename: 'AdminPlan', id: '01920000-0000-7000-8000-000000000f01', code: 'FREE', name: 'Free', priceMinor: 0, currency: 'INR', interval: 'NONE', features: ['Read public notes'], active: true, subscriberCount: 10000, entitlements: [{ __typename: 'AdminPlanEntitlement', key: 'AI_TOKENS_DAILY', limit: '20000', appliesToRole: 'STUDENT' }] },
          { __typename: 'AdminPlan', id: '01920000-0000-7000-8000-000000000f02', code: 'PLUS', name: 'Plus', priceMinor: 49900, currency: 'INR', interval: 'MONTH', features: ['AI on your notes'], active: true, subscriberCount: 42, entitlements: [{ __typename: 'AdminPlanEntitlement', key: 'STORAGE_BYTES', limit: '1073741824', appliesToRole: null }] },
        ],
      }),
      AiSettings: () => ({
        aiSettings: {
          __typename: 'AiSettings',
          connections: [],
          chatConnectionId: null,
          embedConnectionId: null,
          environment: { __typename: 'AiEnvironmentProvider', kind: 'OLLAMA', chatModel: 'gemma4', embedModel: 'embeddinggemma' },
          routes: [],
          tasks: ['SUMMARIZE', 'ASK'],
          presets: [preset('OLLAMA', 'Ollama', { needsKey: false, privateByDefault: true, chatModels: ['gemma4'] })],
          keysCanBeSaved: true,
          spentThisMonthMicroUsd: 0,
          monthlyBudgetMicroUsd: 50_000_000,
        },
      }),
      ModerationQueue: () => ({ moderationQueue: { __typename: 'ModerationCaseConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
      AdminContests: () => ({ adminContests: [] }),
      ContestSubjects: () => ({ subjects: [] }),
      VerificationRequestsToReview: () => ({ verificationRequestsToReview: [] }),
      StudentIdVerificationQueue: () => ({ studentIdVerificationQueue: [] }),
      AdminErrors: () => ({ adminErrors: [] }),
      AdminUsage: () => ({ adminUsage: { __typename: 'AdminUsageSummary', dau: 0, wau: 0, mau: 0, from: '2026-09-25T00:00:00.000Z', to: '2026-10-25T00:00:00.000Z', topFeatures: [], topEvents: [] } }),
      InstitutionDomains: () => ({ institutionDomains: [] }),
      AdminAccounts: () => ({ adminAccounts: [] }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
}

async function fits(page: Page, where: string) {
  const box = await page.evaluate(() => {
    const main = document.getElementById('main')
    return {
      scrollWidth: document.documentElement.scrollWidth,
      innerWidth: window.innerWidth,
      mainScroll: main?.scrollWidth ?? 0,
      mainClient: main?.clientWidth ?? 0,
    }
  })
  expect(box.scrollWidth, `${where}: document is ${box.scrollWidth}px in a ${box.innerWidth}px window`).toBeLessThanOrEqual(box.innerWidth)
  expect(box.mainScroll, `${where}: main is ${box.mainScroll}px in ${box.mainClient}px`).toBeLessThanOrEqual(box.mainClient + 1)
}

async function barAboveTitle(page: Page, heading: string) {
  // The app and visitor bars are the banner. A page may also use <header> for its own title.
  const header = await page.getByRole('banner').first().boundingBox()
  const title = await page.getByRole('heading', { level: 1, name: heading }).boundingBox()
  expect(header?.y ?? 99).toBeLessThanOrEqual(2)
  expect(title!.y).toBeGreaterThanOrEqual(header!.y + header!.height - 1)
}

test('admin pages fit the screen at every size, in light and dark', async ({ page }, info) => {
  test.setTimeout(300_000)
  test.skip(info.project.name !== 'desktop', 'the viewports below are set explicitly')
  const dir = process.env.ADMIN_SCREENSHOT_DIR
  await adminApi(page)
  for (const theme of ['light', 'dark'] as const) {
    await page.addInitScript((value) => localStorage.setItem('cnote:theme', JSON.stringify(value)), theme)
    for (const viewport of VIEWPORTS) {
      await page.setViewportSize(viewport)
      const wide = viewport.width >= 1024
      for (const entry of PAGES) {
        await page.goto(entry.path)
        await expect(page.getByRole('heading', { level: 1, name: entry.heading })).toBeVisible()
        await expect(page.locator('html')).toHaveAttribute('data-theme', theme)
        await barAboveTitle(page, entry.heading)
        await fits(page, `${theme} ${viewport.width} ${entry.path}`)
        const opener = page.getByRole('button', { name: 'Admin settings', exact: true })
        const nav = page.getByRole('navigation', { name: 'Admin settings' })
        if (entry.admin === false) {
          await expect(opener).toHaveCount(0)
          if (!wide) await expect(page.getByRole('button', { name: 'Menu', exact: true })).toBeVisible()
        } else if (wide) {
          await expect(opener).toBeHidden()
          await expect(nav.getByRole('link', { name: 'Overview' })).toBeVisible()
          await expect(nav.getByRole('link', { name: 'Beta access' })).toBeVisible()
          await expect(page.getByRole('button', { name: 'Menu', exact: true })).toBeHidden()
        } else {
          await expect(opener).toBeVisible()
          await expect(nav).toHaveCount(0)
          await expect(page.getByRole('button', { name: 'Menu', exact: true })).toBeVisible()
          await opener.click()
          const drawer = page.getByRole('dialog', { name: 'Admin settings' })
          await expect(drawer.getByRole('link', { name: 'Plans & pricing' })).toBeVisible()
          await expect(drawer.getByRole('link', { name: 'Beta access' })).toBeVisible()
          await fits(page, `${theme} ${viewport.width} ${entry.path} drawer`)
          await page.keyboard.press('Escape')
          await expect(drawer).toHaveCount(0)
        }
        if (dir && entry.shot && SHOT_WIDTHS.has(viewport.width) && (theme === 'light' || entry.shot === 'access' || entry.shot === 'user-plans')) {
          await page.screenshot({ path: `${dir}/${entry.shot}-${theme}-${viewport.width}.png` })
          if ((entry.shot === 'access' || entry.shot === 'user-plans') && (viewport.width === 320 || viewport.width === 1280)) {
            const row = page.getByRole('article').first()
            if (await row.count()) await row.scrollIntoViewIfNeeded()
            await page.screenshot({ path: `${dir}/${entry.shot}-list-${theme}-${viewport.width}.png` })
          }
        }
      }
    }
  }
})
