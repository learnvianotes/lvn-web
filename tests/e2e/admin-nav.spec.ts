import { expect, test, type Page, type Route } from '@playwright/test'
import { mockApi } from './support/notes-api'

/**
 * The admin area's side navigation: every settings page, the open one marked, and on a phone a drawer.
 * Who may see a page is unchanged — a student is still turned away by the page itself, and sees no sidebar.
 */

const viewerExtras = { profile: null, legacyImport: { __typename: 'LegacyImport', status: 'NOT_FOUND', claimedAt: null, counts: null } }
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
const settings = {
  __typename: 'AiSettings',
  connections: [
    {
      __typename: 'AiConnection',
      id: '01920000-0000-7000-8000-0000000a1c01',
      kind: 'ANTHROPIC',
      label: 'Claude',
      baseUrl: null,
      hasKey: true,
      keyHint: '7777',
      mayReceivePrivate: false,
      enabled: true,
      chatModel: 'claude-sonnet-5-5',
      embedModel: null,
      inputMicroUsdPerMTok: 3_000_000,
      outputMicroUsdPerMTok: 15_000_000,
      embedMicroUsdPerMTok: 0,
      updatedAt: '2026-10-13T10:00:00.000Z',
    },
  ],
  chatConnectionId: '01920000-0000-7000-8000-0000000a1c01',
  embedConnectionId: null,
  environment: { __typename: 'AiEnvironmentProvider', kind: 'OLLAMA', chatModel: 'gemma4', embedModel: 'embeddinggemma' },
  routes: [],
  tasks: ['SUMMARIZE', 'QUIZ', 'TRANSCRIBE', 'ASK', 'EMBED'],
  presets: [
    preset('ANTHROPIC', 'Claude (Anthropic)', { defaultBaseUrl: 'https://api.anthropic.com', canEmbed: false, canHear: false, chatModels: ['claude-sonnet-5-5'] }),
    preset('OPENAI', 'ChatGPT (OpenAI)', { defaultBaseUrl: 'https://api.openai.com/v1' }),
    preset('GEMINI', 'Gemini (Google)'),
    preset('OPENAI_COMPATIBLE', 'Custom (OpenAI-compatible)', { needsKey: false }),
    preset('OLLAMA', 'Ollama', { needsKey: false, privateByDefault: true }),
  ],
  keysCanBeSaved: true,
  spentThisMonthMicroUsd: 1_250_000,
  monthlyBudgetMicroUsd: 50_000_000,
}

const SECTIONS: [label: string, href: string][] = [
  ['Proof of study to review', '/admin/verification'],
  ['Google sign-in', '/admin/sign-in'],
  ['Moderation queue', '/admin/moderation'],
  ['Weekly contests', '/admin/contests'],
  ['AI providers', '/admin/ai'],
]

async function adminApi(page: Page) {
  await mockApi(
    page,
    {
      AiSettings: () => ({ aiSettings: settings }),
      ModerationQueue: () => ({ moderationQueue: { __typename: 'ModerationCaseConnection', edges: [], pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } } }),
      AdminContests: () => ({ adminContests: [] }),
      VerificationRequestsToReview: () => ({ verificationRequestsToReview: [] }),
    },
    { ...viewerExtras, globalRole: 'PLATFORM_ADMIN' },
  )
}

async function shot(page: Page, name: string) {
  const dir = process.env.ADMIN_NAV_SCREENSHOT_DIR
  if (!dir) return
  await page.screenshot({ path: `${dir}/${name}.png` })
}

test('a platform admin sees every settings section, with the open one marked', async ({ page }, info) => {
  test.skip(info.project.name === 'phone', 'a phone opens the same list from Admin settings')
  await adminApi(page)
  await page.goto('/admin/ai')
  const nav = page.getByRole('navigation', { name: 'Admin settings' })
  await expect(nav.getByRole('link')).toHaveText(SECTIONS.map(([label]) => label))
  for (const [label, href] of SECTIONS) await expect(nav.getByRole('link', { name: label, exact: true })).toHaveAttribute('href', href)
  await expect(nav.getByText('People', { exact: true })).toBeVisible()
  await expect(nav.getByText('Content', { exact: true })).toBeVisible()
  await expect(nav.getByText('AI', { exact: true })).toBeVisible()
  await expect(nav.getByRole('link', { name: 'AI providers' })).toHaveAttribute('aria-current', 'page')
  await expect(nav.getByRole('link', { name: 'Moderation queue' })).not.toHaveAttribute('aria-current', 'page')
  await expect(page.getByRole('button', { name: 'Admin settings' })).toBeHidden()
  await expect(page.getByRole('heading', { name: 'AI providers', level: 1 })).toBeVisible()
  await shot(page, 'admin_sidebar_desktop')

  await nav.getByRole('link', { name: 'Moderation queue' }).click()
  await expect(page).toHaveURL(/\/admin\/moderation$/)
  await expect(nav.getByRole('link', { name: 'Moderation queue' })).toHaveAttribute('aria-current', 'page')
  await expect(nav.getByRole('link', { name: 'AI providers' })).not.toHaveAttribute('aria-current', 'page')
  await expect(page.getByRole('heading', { name: 'Moderation queue', level: 1 })).toBeVisible()
  await shot(page, 'admin_sidebar_desktop_moderation')
})

test('on a phone the sections sit in a drawer that closes when one is chosen', async ({ page }, info) => {
  test.skip(info.project.name !== 'phone', 'the drawer is the phone layout')
  await adminApi(page)
  await page.goto('/admin/ai')
  await expect(page.getByRole('navigation', { name: 'Admin settings' })).toBeHidden()
  await expect(page.getByRole('heading', { name: 'AI providers', level: 1 })).toBeVisible()
  const opener = page.getByRole('button', { name: 'Admin settings', exact: true })
  await expect(opener).toHaveAttribute('aria-expanded', 'false')
  await opener.click()
  const drawer = page.getByRole('dialog', { name: 'Admin settings' })
  await expect(drawer.getByRole('link')).toHaveText(SECTIONS.map(([label]) => label))
  await expect(drawer.getByRole('link', { name: 'AI providers' })).toHaveAttribute('aria-current', 'page')
  await expect(opener).toHaveAttribute('aria-expanded', 'true')
  await shot(page, 'admin_sidebar_mobile')

  await page.keyboard.press('Escape')
  await expect(drawer).toHaveCount(0)
  await expect(opener).toHaveAttribute('aria-expanded', 'false')

  await opener.click()
  await drawer.getByRole('link', { name: 'Weekly contests' }).click()
  await expect(page).toHaveURL(/\/admin\/contests$/)
  await expect(drawer).toHaveCount(0)
  await opener.click()
  await expect(page.getByRole('dialog', { name: 'Admin settings' }).getByRole('link', { name: 'Weekly contests' })).toHaveAttribute('aria-current', 'page')
  await page.getByRole('dialog', { name: 'Admin settings' }).getByRole('button', { name: 'Close admin settings' }).last().click()
  await expect(page.getByRole('dialog', { name: 'Admin settings' })).toHaveCount(0)
})

test('someone who is not a platform admin still cannot open the settings, and is not shown the sidebar', async ({ page }) => {
  await mockApi(page, {}, viewerExtras)
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { operationName?: string }
    if (body.operationName !== 'AiSettings') return route.fallback()
    return route.fulfill({ json: { data: null, errors: [{ message: 'Only platform admins choose AI providers.', extensions: { code: 'FORBIDDEN' } }] } })
  })
  await page.goto('/admin/ai')
  await expect(page.getByText('Only platform admins choose AI providers.')).toBeVisible()
  await expect(page.getByRole('navigation', { name: 'Admin settings' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Admin settings' })).toHaveCount(0)
})
