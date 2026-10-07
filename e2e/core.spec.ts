import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

test('landing page leads to the notes', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await page.getByRole('main').getByRole('link', { name: /browse notes/i }).click()
  await expect(page).toHaveURL(/\/core$/)
  await expect(page.getByRole('link', { name: /DSA Basics/ }).first()).toBeVisible()
})

test('a topic renders highlighted code and working language tabs', async ({ page }) => {
  await page.goto('/core/dsa-advanced/binary_indexed_tree')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(page.locator('.lvn-prose .hljs-keyword').first()).toBeAttached()
  const tabs = page.locator('[data-tabs]').first()
  await tabs.getByRole('tab', { name: 'Java', exact: true }).click()
  await expect(tabs.getByRole('tab', { name: 'Java', exact: true })).toHaveAttribute('aria-selected', 'true')
  await expect(tabs.getByRole('tabpanel')).toHaveCount(1)
})

test('problem sheet lists problems with solutions', async ({ page }) => {
  await page.goto('/core/sheet-150/stack')
  await expect(page.locator('article#lc-20')).toContainText('Valid Parentheses')
})

test('old root URLs redirect into /core', async ({ page }) => {
  await page.goto('/dsa-basics/analysis')
  await expect(page).toHaveURL(/\/core\/dsa-basics\/analysis$/)
})

test('unknown pages 404', async ({ page }) => {
  const res = await page.goto('/core/nope/nothing')
  expect(res?.status()).toBe(404)
})

test('topic page has no serious accessibility violations', async ({ page }) => {
  await page.goto('/core/dsa-basics/analysis')
  const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
  expect(violations.filter((v) => v.impact === 'critical' || v.impact === 'serious')).toEqual([])
})
