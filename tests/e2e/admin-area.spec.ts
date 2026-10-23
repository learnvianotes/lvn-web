import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * The admin overview, configuration and plans (lvn-backend contracts 0.68.0), with GraphQL mocked.
 * Screenshots are written when ADMIN_SCREENSHOT_DIR is set.
 */

const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
const none = { userErrors: [] }
const constraints = (over: Record<string, unknown> = {}) => ({ __typename: 'AdminSettingConstraints', min: null, max: null, maxLength: null, pattern: null, nullable: false, ...over })
const setting = (over: Record<string, unknown>): Record<string, unknown> => ({
  __typename: 'AdminSetting',
  description: 'A platform setting.',
  value: 'true',
  overridden: false,
  updatedAt: '2026-10-01T00:00:00.000Z',
  constraints: constraints(),
  ...over,
})

const usage = (over: Record<string, unknown>) => ({ tasksRun: 0, failures: 0, promptTokens: '0', completionTokens: '0', costMicroUsd: '0', ...over })
const metrics = {
  __typename: 'AdminMetrics',
  generatedAt: '2026-10-23T18:00:00.000Z',
  users: { __typename: 'AdminUserMetrics', total: 12840, newLast7Days: 312, newLast30Days: 1402, active: 4201 },
  content: { __typename: 'AdminContentMetrics', notes: 58012, publicNotes: 6400, subjects: 18, topics: 940, groups: 126, classrooms: 84 },
  ai: {
    __typename: 'AdminAiMetrics',
    from: '2026-09-24T00:00:00.000Z',
    to: '2026-10-23T18:00:00.000Z',
    ...usage({ tasksRun: 18420, failures: 210, promptTokens: '84200120', completionTokens: '12004400', costMicroUsd: '18650000' }),
    byProvider: [
      { __typename: 'AdminAiProviderUsage', provider: 'ANTHROPIC', ...usage({ tasksRun: 12000, failures: 80, promptTokens: '50000000', completionTokens: '8000000', costMicroUsd: '15000000' }) },
      { __typename: 'AdminAiProviderUsage', provider: 'GEMINI', ...usage({ tasksRun: 6420, failures: 130, promptTokens: '34200120', completionTokens: '4004400', costMicroUsd: '3650000' }) },
    ],
    byModel: [{ __typename: 'AdminAiModelUsage', provider: 'ANTHROPIC', model: 'claude-sonnet-5-5', ...usage({ tasksRun: 12000, failures: 80, promptTokens: '50000000', completionTokens: '8000000', costMicroUsd: '15000000' }) }],
    byTask: [{ __typename: 'AdminAiTaskUsage', task: 'SUMMARIZE', ...usage({ tasksRun: 9000, failures: 40, promptTokens: '20000000', completionTokens: '4000000', costMicroUsd: '8000000' }) }],
  },
  storage: { __typename: 'AdminStorageMetrics', bytes: '12884901888', files: 40211 },
  verification: { __typename: 'AdminVerificationMetrics', studentIdQueue: 7, pendingRequests: 3, domainReviews: 2 },
  moderation: { __typename: 'AdminModerationMetrics', openReports: 4, openAppeals: 1 },
}

const initialSettings = () => [
  setting({ key: 'google_sign_in', type: 'BOOLEAN', category: 'auth', description: 'Let people sign in with Google.' }),
  setting({ key: 'student_id_verification', type: 'BOOLEAN', category: 'verification', description: 'Review uploaded proof of study.' }),
  setting({ key: 'uploads_enabled', type: 'BOOLEAN', category: 'uploads', description: 'Allow files to be uploaded.' }),
  setting({ key: 'ai_public_pipeline', type: 'BOOLEAN', category: 'ai', description: 'Write study aids for public notes.' }),
  setting({ key: 'ai_monthly_budget_micro_usd', type: 'INTEGER', category: 'ai', description: 'Cap for the month, in micro-USD. Empty means no cap.', value: '', constraints: constraints({ nullable: true }) }),
  setting({ key: 'ai_timeout_ms', type: 'INTEGER', category: 'ai', description: 'How long an AI call may take.', value: '30000', constraints: constraints({ min: 1000, max: 120000 }) }),
  setting({ key: 'search_hybrid', type: 'BOOLEAN', category: 'search', description: 'Search by words and by meaning.' }),
  setting({ key: 'search_timeout_ms', type: 'INTEGER', category: 'search', description: 'How long a search may take.', value: '1500', overridden: true, constraints: constraints({ min: 100, max: 10000 }) }),
  setting({ key: 'account_minimum_age', type: 'INTEGER', category: 'accounts', description: 'Youngest age that can register.', value: '18', constraints: constraints({ min: 0, max: 120 }) }),
  setting({ key: 'digital_consent_age', type: 'INTEGER', category: 'accounts', description: 'Age of digital consent.', value: '18', constraints: constraints({ min: 13, max: 120 }) }),
]

const entitlement = (key: string, limit: string | null, role: string | null = null) => ({ __typename: 'AdminPlanEntitlement', key, limit, appliesToRole: role })
const plan = (over: Record<string, unknown>): Record<string, unknown> => ({
  __typename: 'AdminPlan',
  currency: 'INR',
  interval: 'MONTH',
  features: ['Notes'],
  active: true,
  entitlements: [entitlement('STORAGE_BYTES', null)],
  ...over,
})
const initialPlans = () => [
  plan({ id: '01920000-0000-7000-8000-000000000f01', code: 'FREE', name: 'Free', priceMinor: 0, interval: 'NONE', features: ['Read public notes'], subscriberCount: 10000, entitlements: [entitlement('AI_TOKENS_DAILY', '20000', 'STUDENT')] }),
  plan({ id: '01920000-0000-7000-8000-000000000f02', code: 'PLUS', name: 'Plus', priceMinor: 49900, features: ['AI on your notes', 'Uploads'], subscriberCount: 42, entitlements: [entitlement('STORAGE_BYTES', '1073741824'), entitlement('AI_TOKENS_DAILY', null)] }),
  plan({ id: '01920000-0000-7000-8000-000000000f03', code: 'CAMPUS', name: 'Campus', priceMinor: 499900, interval: 'YEAR', features: ['Seats for a class'], subscriberCount: 0, entitlements: [] }),
]
let settings: Record<string, unknown>[] = initialSettings()
let plans: Record<string, unknown>[] = initialPlans()

async function adminApi(page: Page) {
  settings = initialSettings()
  plans = initialPlans()
  return mockApi(
    page,
    {
      AdminMetrics: () => ({ adminMetrics: metrics }),
      AdminSettings: () => ({ adminSettings: settings }),
      UpdateAdminSetting: (v) => {
        const input = v.input as { key: string; value: string }
        if (input.key === 'search_timeout_ms' && input.value === '9999') {
          return { updateAdminSetting: { __typename: 'AdminSettingPayload', setting: null, userErrors: [{ __typename: 'UserError', code: 'VALIDATION', field: ['input', 'value'], message: 'That timeout is not allowed.' }] } }
        }
        settings = settings.map((item) => (item.key === input.key ? { ...item, value: input.value, overridden: true } : item))
        return { updateAdminSetting: { __typename: 'AdminSettingPayload', setting: settings.find((item) => item.key === input.key), ...none } }
      },
      ResetAdminSetting: (v) => {
        settings = settings.map((item) => (item.key === v.key ? { ...item, overridden: false, value: item.key === 'search_timeout_ms' ? '800' : item.value } : item))
        return { resetAdminSetting: { __typename: 'AdminSettingPayload', setting: settings.find((item) => item.key === v.key), ...none } }
      },
      AdminPlans: () => ({ adminPlans: plans }),
      CreateAdminPlan: (v) => {
        const input = v.input as Record<string, unknown>
        const created = plan({ id: '01920000-0000-7000-8000-000000000f04', subscriberCount: 0, ...input })
        plans = [...plans, created]
        return { createAdminPlan: { __typename: 'AdminPlanPayload', plan: created, ...none } }
      },
      UpdateAdminPlan: (v) => {
        const input = v.input as { id: string; active?: boolean }
        plans = plans.map((item) => (item.id === input.id ? { ...item, ...input } : item))
        return { updateAdminPlan: { __typename: 'AdminPlanPayload', plan: plans.find((item) => item.id === input.id), ...none } }
      },
      DeleteAdminPlan: (v) => {
        plans = plans.filter((item) => item.id !== v.id)
        return { deleteAdminPlan: { __typename: 'OkPayload', ok: true, ...none } }
      },
      ModerationQueue: () => ({ moderationQueue: { __typename: 'ModerationCaseConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
      VerificationRequestsToReview: () => ({ verificationRequestsToReview: [] }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
}

async function shot(page: Page, name: string, project: string) {
  const dir = process.env.ADMIN_SCREENSHOT_DIR
  if (!dir) return
  await page.screenshot({ path: `${dir}/${name}_${project}.png`, fullPage: true })
}

async function showCategory(page: Page, name: string) {
  const toggle = page.getByRole('heading', { level: 2, name }).getByRole('button')
  await expect(async () => {
    if ((await toggle.getAttribute('aria-expanded')) !== 'true') await toggle.click()
    await expect(toggle).toHaveAttribute('aria-expanded', 'true')
  }).toPass()
}

async function seriousViolations(page: Page) {
  const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']).analyze()
  return violations.filter((v) => v.impact === 'serious' || v.impact === 'critical').map((v) => `${v.id}: ${v.help}`)
}

test('overview shows the figures, rejects a window past 366 days, and links to the other admin pages', async ({ page }, info) => {
  const calls = await adminApi(page)
  await page.goto('/admin')
  await expect(page.getByRole('heading', { name: 'Overview', level: 1 })).toBeVisible()
  await expect(page.getByText(/Figures from/)).toBeVisible()
  await expect(page.getByText('12,840')).toBeVisible()
  await expect(page.getByText('312')).toBeVisible()
  await expect(page.getByText('1,402')).toBeVisible()
  await expect(page.getByText('4,201')).toBeVisible()
  await expect(page.getByText('58,012')).toBeVisible()
  await expect(page.getByText('12 GB')).toBeVisible()
  await expect(page.getByText('40,211 files')).toBeVisible()
  await expect(page.getByText('$18.65')).toBeVisible()
  await expect(page.getByText('1.1%')).toBeVisible()
  await expect(page.getByText('84,200,120')).toBeVisible()
  await expect(page.getByText(/claude-sonnet-5-5/).first()).toBeVisible()
  await expect(page.getByText('SUMMARIZE').first()).toBeVisible()
  await expect(page.getByRole('link', { name: 'Account rules' })).toHaveAttribute('href', '/admin/settings#accounts')
  await expect(page.getByRole('region', { name: 'Content' }).getByRole('link', { name: 'Moderation queue' })).toHaveAttribute('href', '/admin/moderation')
  await expect(page.getByRole('link', { name: 'Upload settings' })).toHaveAttribute('href', '/admin/settings#uploads')
  await expect(page.getByRole('link', { name: 'Review the queue' })).toHaveAttribute('href', '/admin/verification')
  await expect(page.getByRole('link', { name: 'Open the queue' })).toHaveAttribute('href', '/admin/moderation')
  await expect(page.getByRole('region', { name: 'AI usage' }).getByRole('link', { name: 'AI providers' })).toHaveAttribute('href', '/admin/ai')
  expect(await seriousViolations(page)).toEqual([])
  await shot(page, 'admin_overview', info.project.name)

  await page.getByLabel('Start date').fill('2024-01-01')
  await page.getByLabel('End date').fill('2025-01-01')
  await page.getByRole('button', { name: 'Apply' }).click()
  await expect(page.getByText('Choose 366 days or fewer.')).toBeVisible()
  expect(calls.filter((call) => call.op === 'AdminMetrics')).toHaveLength(1)

  await page.getByLabel('Start date').fill('2026-10-01')
  await page.getByLabel('End date').fill('2026-10-23')
  await page.getByRole('button', { name: 'Apply' }).click()
  await expect.poll(() => calls.filter((call) => call.op === 'AdminMetrics').at(-1)?.variables).toMatchObject({ from: '2026-10-01T00:00:00.000Z', to: '2026-10-23T23:59:59.999Z' })
  await page.getByRole('button', { name: 'Last 30 days' }).click()
  await expect.poll(() => calls.filter((call) => call.op === 'AdminMetrics').at(-1)?.variables.from).toBeUndefined()
})

test('configuration validates age, confirms a risky switch, shows a user error and resets a custom value', async ({ page }, info) => {
  const calls = await adminApi(page)
  await page.goto('/admin/settings')
  await expect(page.getByRole('heading', { name: 'Configuration', level: 1 })).toBeVisible()
  for (const name of ['Sign-in', 'Verification', 'Uploads', 'AI', 'Search', 'Accounts']) await expect(page.getByRole('heading', { name, level: 2 })).toBeVisible()
  await showCategory(page, 'Accounts')
  const age = page.getByRole('article', { name: 'Minimum account age' })
  await age.getByRole('spinbutton', { name: 'Minimum account age', exact: true }).fill('17')
  await expect(age.getByText('The minimum age cannot be below 18.')).toBeVisible()
  await expect(age.getByRole('button', { name: 'Save Minimum account age' })).toBeDisabled()
  expect(calls.some((call) => call.op === 'UpdateAdminSetting')).toBe(false)

  await age.getByRole('spinbutton', { name: 'Minimum account age', exact: true }).fill('21')
  await age.getByRole('button', { name: 'Save Minimum account age' }).click()
  const confirmAge = page.getByRole('dialog', { name: 'Confirm this change' })
  await expect(confirmAge).toContainText('never be below 18')
  await confirmAge.getByRole('button', { name: 'Cancel' }).click()
  expect(calls.some((call) => call.op === 'UpdateAdminSetting' && (call.variables.input as { key: string }).key === 'account_minimum_age')).toBe(false)
  await age.getByRole('button', { name: 'Save Minimum account age' }).click()
  await confirmAge.getByRole('button', { name: 'Confirm' }).click()
  await expect(confirmAge).toBeHidden()
  await expect.poll(() => calls.find((call) => call.op === 'UpdateAdminSetting' && (call.variables.input as { key: string }).key === 'account_minimum_age')?.variables.input).toEqual({ key: 'account_minimum_age', value: '21' })

  await showCategory(page, 'Uploads')
  const uploads = page.getByRole('article', { name: 'Uploads' })
  await uploads.getByRole('switch', { name: 'Uploads' }).click()
  await uploads.getByRole('button', { name: 'Save Uploads' }).click()
  const confirm = page.getByRole('dialog', { name: 'Confirm this change' })
  await expect(confirm).toContainText('Turn off uploads?')
  await confirm.getByRole('button', { name: 'Cancel' }).click()
  expect(calls.some((call) => call.op === 'UpdateAdminSetting' && (call.variables.input as { value: string }).value === 'false')).toBe(false)
  await uploads.getByRole('button', { name: 'Save Uploads' }).click()
  await confirm.getByRole('button', { name: 'Confirm' }).click()
  await expect(confirm).toBeHidden()
  await expect.poll(() => calls.find((call) => call.op === 'UpdateAdminSetting' && (call.variables.input as { key: string }).key === 'uploads_enabled')?.variables.input).toEqual({ key: 'uploads_enabled', value: 'false' })
  await expect(uploads.getByRole('switch', { name: 'Uploads' })).toHaveAttribute('aria-checked', 'false')

  await showCategory(page, 'Search')
  const timeout = page.getByRole('article', { name: 'Search timeout' })
  await expect(timeout.getByText('Custom', { exact: true })).toBeVisible()
  const timeoutInput = timeout.getByRole('spinbutton', { name: 'Search timeout', exact: true })
  await timeoutInput.fill('9999')
  await expect(timeoutInput).toHaveValue('9999')
  await timeout.getByRole('button', { name: 'Save Search timeout' }).click()
  await expect(timeout.getByText('That timeout is not allowed.')).toBeVisible()
  await timeout.getByRole('button', { name: 'Reset Search timeout to default' }).click()
  await expect.poll(() => calls.find((call) => call.op === 'ResetAdminSetting')?.variables).toEqual({ key: 'search_timeout_ms' })
  await expect(timeout.getByText('Default', { exact: true })).toBeVisible()
  expect(await seriousViolations(page)).toEqual([])
  await shot(page, 'admin_settings', info.project.name)
})

test('plans show prices, keep FREE, and deactivate a plan that has subscribers instead of deleting it', async ({ page }, info) => {
  const calls = await adminApi(page)
  await page.goto('/admin/plans')
  await expect(page.getByRole('heading', { name: 'Plans & pricing', level: 1 })).toBeVisible()
  await expect(page.getByText('Saving a price charges nobody.')).toBeVisible()
  const plus = page.getByRole('article', { name: 'Plus' })
  await expect(plus).toContainText(/₹\s?499\/month/)
  await expect(plus).toContainText('42 subscribers')
  await expect(plus).toContainText('Unlimited')
  await expect(plus).toContainText('1 GB')
  const free = page.getByRole('article', { name: 'Free' })
  await expect(free).toContainText('The free plan stays active')
  await expect(free.getByRole('button', { name: 'Delete Free' })).toHaveCount(0)

  await page.getByRole('button', { name: 'Edit Free' }).click()
  const edit = page.getByRole('dialog', { name: 'Edit Free' })
  await expect(edit.getByLabel('Code')).toBeDisabled()
  await expect(edit.getByLabel('Code')).toHaveValue('FREE')
  await expect(edit.getByRole('checkbox', { name: 'Active' })).toBeDisabled()
  await edit.getByRole('button', { name: 'Cancel' }).click()

  await expect(plus.getByRole('button', { name: 'Delete Plus' })).toBeDisabled()
  await expect(plus.getByRole('tooltip')).toContainText('Deactivate it instead')
  await plus.getByRole('button', { name: 'Deactivate Plus' }).click()
  const deactivate = page.getByRole('dialog', { name: 'Deactivate Plus' })
  await expect(deactivate).toContainText('cannot be deleted')
  await deactivate.getByRole('button', { name: 'Deactivate' }).click()
  await expect.poll(() => calls.find((call) => call.op === 'UpdateAdminPlan')?.variables.input).toEqual({ id: '01920000-0000-7000-8000-000000000f02', active: false })
  await expect(plus.getByText('Inactive', { exact: true })).toBeVisible()

  await page.getByRole('button', { name: 'Delete Campus' }).click()
  await page.getByRole('dialog', { name: 'Delete Campus' }).getByRole('button', { name: 'Delete' }).click()
  await expect(page.getByRole('article', { name: 'Campus' })).toHaveCount(0)
  expect(calls.some((call) => call.op === 'DeleteAdminPlan')).toBe(true)

  await page.getByRole('button', { name: 'New plan' }).click()
  const create = page.getByRole('dialog', { name: 'New plan' })
  await expect(create.getByText('Saving a price charges nobody.')).toBeVisible()
  await create.getByLabel('Code').fill('campus_2')
  await expect(create.getByLabel('Code')).toHaveValue('CAMPUS_2')
  await create.getByLabel('Name').fill('Campus 2')
  await create.getByLabel('Price').fill('99')
  await create.getByLabel('Currency').fill('INR')
  await create.getByLabel('Features').fill('Shared seats')
  await create.getByRole('button', { name: 'Add a limit' }).click()
  await create.getByLabel('Limit', { exact: true }).selectOption('AI_TOKENS_DAILY')
  await create.getByLabel('Amount').fill('100000')
  await create.getByRole('button', { name: 'Save' }).click()
  await expect.poll(() => calls.find((call) => call.op === 'CreateAdminPlan')?.variables.input).toMatchObject({
    code: 'CAMPUS_2',
    name: 'Campus 2',
    priceMinor: 9900,
    currency: 'INR',
    interval: 'MONTH',
    active: true,
    features: ['Shared seats'],
    entitlements: [{ key: 'AI_TOKENS_DAILY', limit: '100000', appliesToRole: null }],
  })
  await expect(page.getByRole('article', { name: 'Campus 2' })).toContainText(/₹\s?99\/month/)
  expect(await seriousViolations(page)).toEqual([])
  await shot(page, 'admin_plans', info.project.name)
})

test('overview follows the dark theme', async ({ page }, info) => {
  test.skip(info.project.name !== 'desktop', 'one dark screenshot is enough to show the theme')
  await page.addInitScript(() => localStorage.setItem('cnote:theme', JSON.stringify('dark')))
  await adminApi(page)
  await page.goto('/admin')
  await expect(page.getByRole('heading', { name: 'Overview', level: 1 })).toBeVisible()
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark')
  await shot(page, 'admin_overview_dark', info.project.name)
})
