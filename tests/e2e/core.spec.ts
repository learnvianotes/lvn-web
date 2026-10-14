import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

/**
 * /core is the old site's app, unchanged for readers (lvn-backend ADR-0002): these tests drive it the
 * way a guest used learnvianotes.in, and check that none of its sign-in features came along.
 */

// The old notes are kept for later and off unless NEXT_PUBLIC_CORE_ENABLED=true (owner, 2026-10-14): these run then.
test.skip(process.env.NEXT_PUBLIC_CORE_ENABLED !== 'true', '/core is off (NEXT_PUBLIC_CORE_ENABLED)')

/** The launch splash goes once the catalog has loaded. */
async function ready(page: Page) {
  await expect(page.locator('#splash')).toHaveCount(0, { timeout: 15_000 })
}

test('home lists every subject for a guest, with no sign-in features', async ({ page }) => {
  await page.goto('/core')
  await ready(page)
  await expect(page.getByRole('heading', { level: 1, name: 'Interview-ready CS, one note at a time.' })).toBeVisible()
  await expect(page.getByRole('link', { name: /DSA Basics/ }).first()).toBeVisible()
  await expect(page.getByText(/sign in|log in|create account|track my progress/i)).toHaveCount(0)
  await expect(page).toHaveTitle('LearnViaNotes')
})

test('a topic renders highlighted code and working language tabs', async ({ page }) => {
  await page.goto('/core/dsa-advanced/binary_indexed_tree')
  await ready(page)
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(page.locator('.prose .hljs-keyword').first()).toBeAttached()
  const tabs = page.locator('.code-tabs-bar, .tab-bar').first()
  const java = tabs.getByRole('tab', { name: 'Java', exact: true })
  await java.click()
  await expect(java).toHaveAttribute('aria-selected', 'true')
})

test('the sidebar moves between topics without reloading and keeps the title in step', async ({ page, isMobile }) => {
  await page.goto('/core/python')
  await ready(page)
  await expect(page).toHaveURL(/\/core\/python\/[\w-]+$/)
  if (isMobile) await page.getByRole('button', { name: 'Show contents' }).click()
  const marker = await page.evaluate(() => ((window as unknown as { __spa: number }).__spa = Date.now()))
  const link = page.locator('.nav-list a.nav-item').nth(3)
  await expect(link).toBeVisible()
  const title = (await link.textContent())!.trim()
  await link.click()
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(title)
  await expect(page).toHaveTitle(`${title} · Python · LearnViaNotes`)
  expect(await page.evaluate(() => (window as unknown as { __spa?: number }).__spa)).toBe(marker)
})

test('a problem sheet category lists its problems with solutions', async ({ page }) => {
  await page.goto('/core/sheet-150/stack')
  await ready(page)
  await expect(page.getByRole('heading', { level: 1, name: 'Stack' })).toBeVisible()
  await expect(page.locator('article#lc-20')).toContainText('Valid Parentheses')
})

test('search finds a topic and opens it', async ({ page, isMobile }) => {
  test.skip(isMobile, 'search opens as a sheet on phones; covered on desktop')
  await page.goto('/core')
  await ready(page)
  const box = page.getByRole('combobox')
  await box.fill('binary indexed')
  await expect(page.getByRole('listbox').getByRole('option').first()).toBeVisible()
  await box.press('Enter')
  await expect(page).toHaveURL(/\/core\/dsa-advanced\/binary_indexed_tree/)
})

test('the theme choice is shared with the rest of the site', async ({ page }) => {
  await page.goto('/core')
  await ready(page)
  const before = await page.locator('html').getAttribute('data-theme')
  await page.getByRole('button', { name: /switch to (dark|light) mode/i }).click()
  const after = before === 'dark' ? 'light' : 'dark'
  await expect(page.locator('html')).toHaveAttribute('data-theme', after)
  await page.goto('/')
  await expect(page.locator('html')).toHaveAttribute('data-theme', after)
})

test('serves the content as static JSON', async ({ request }) => {
  const meta = await request.get('/core/data/meta.json')
  expect(meta.ok()).toBe(true)
  expect(await meta.json()).toMatchObject({ version: expect.stringMatching(/^[0-9a-f]{16}$/), schema: 1 })
  expect((await request.get('/core/data/topics/python/nope.json')).status()).toBe(404)
})

test('each page has its own title and canonical URL for search engines', async ({ request }) => {
  const html = await (await request.get('/core/dsa-advanced/binary_indexed_tree')).text()
  expect(html).toMatch(/<title>[^<]+ · DSA Advanced · LearnViaNotes<\/title>/)
  expect(html).toMatch(/<link rel="canonical" href="[^"]+\/core\/dsa-advanced\/binary_indexed_tree"/)
})

test('unknown pages are a 404 with the old "not found" page', async ({ page }) => {
  const res = await page.goto('/core/nope/nothing')
  expect(res?.status()).toBe(404)
  await expect(page.getByText('Page not found')).toBeVisible()
})

test('old root URLs redirect into /core', async ({ page }) => {
  await page.goto('/dsa-basics/analysis')
  await expect(page).toHaveURL(/\/core\/dsa-basics\/analysis$/)
  await page.goto('/about')
  await expect(page).toHaveURL(/\/core\/about$/)
})

/**
 * Findings the old site has too (checked against learnvianotes.in), kept so /core looks exactly as before:
 * code comments (4.24:1) and callout labels (4.39:1) are just under 4.5:1, and wide code blocks and tables
 * scroll without being focusable. Anything else fails the test.
 */
const KNOWN_OLD_SITE_FINDINGS: Record<string, RegExp> = {
  'color-contrast': /\.hljs-comment|\.callout-label/,
  'scrollable-region-focusable': /(\bpre|\.table-wrap)(:nth-child\(\d+\))?$/,
}

test('topic page has no serious accessibility violations beyond the old site\'s', async ({ page }) => {
  // Checked as it settles: fade-ins would be measured half-transparent.
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/core/dsa-basics/analysis')
  await ready(page)
  const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
  const findings = violations
    .filter((v) => v.impact === 'critical' || v.impact === 'serious')
    .flatMap((v) => v.nodes.map((n) => ({ rule: v.id, target: n.target.join(' ') })))
    .filter(({ rule, target }) => !KNOWN_OLD_SITE_FINDINGS[rule]?.test(target))
  expect(findings).toEqual([])
})
