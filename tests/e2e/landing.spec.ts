import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

test('landing page leads to the notes', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await page.getByRole('main').getByRole('link', { name: /browse notes/i }).click()
  await expect(page).toHaveURL(/\/core$/)
  await expect(page.locator('#splash')).toHaveCount(0, { timeout: 15_000 })
  await expect(page.getByRole('link', { name: /DSA Basics/ }).first()).toBeVisible()
})

test('a subject card opens that subject in /core', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('main').getByRole('link', { name: /Python/ }).first().click()
  await expect(page).toHaveURL(/\/core\/python/)
})

test('unknown URLs get the site 404', async ({ page }) => {
  const res = await page.goto('/definitely-not-here')
  expect(res?.status()).toBe(404)
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
})

test('sitemap lists /core pages', async ({ request }) => {
  const xml = await (await request.get('/sitemap.xml')).text()
  expect(xml).toContain('/core/about</loc>')
  expect(xml).toContain('/core/dsa-advanced/binary_indexed_tree</loc>')
})

test('landing page has no serious accessibility violations', async ({ page }) => {
  await page.goto('/')
  const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
  expect(violations.filter((v) => v.impact === 'critical' || v.impact === 'serious').map((v) => v.id)).toEqual([])
})
