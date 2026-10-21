import { expect, test, type Page } from '@playwright/test'

/**
 * Google Analytics only after consent (lvn-backend ADR-0092). The usual e2e build has no measurement id: nothing shows
 * and nothing loads. With E2E_GA_ID set to the id a build was made with (NEXT_PUBLIC_GA_MEASUREMENT_ID), the banner and
 * the choice are checked too; Google is stubbed, nothing leaves the machine.
 */

const id = process.env.E2E_GA_ID

/** Every request to Google's tag or collection hosts, answered locally. */
async function stubGoogle(page: Page) {
  const hits: string[] = []
  await page.route(/googletagmanager\.com|google-analytics\.com|analytics\.google\.com/, (route) => {
    hits.push(route.request().url())
    return route.fulfill({ contentType: 'text/javascript', body: '' })
  })
  return hits
}

test('without a measurement id there is no banner, no choice in the footer and nothing from Google', async ({ page }) => {
  test.skip(!!id, 'this build has Google Analytics')
  const hits = await stubGoogle(page)
  await page.goto('/subjects')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(page.getByRole('region', { name: 'Analytics cookies' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Analytics choice' })).toHaveCount(0)
  expect(hits).toEqual([])
})

test.describe('with Google Analytics configured', () => {
  test.skip(!id, 'set E2E_GA_ID to the id of a build made with NEXT_PUBLIC_GA_MEASUREMENT_ID')

  test('asks once; nothing loads until Allow; the choice reaches every open tab and can be changed', async ({ page, context }) => {
    const hits = await stubGoogle(page)
    await page.goto('/subjects')
    const banner = page.getByRole('region', { name: 'Analytics cookies' })
    await expect(banner).toBeVisible()
    await expect(banner.getByRole('link', { name: 'Privacy Policy' })).toHaveAttribute('href', '/legal/privacy')
    expect(hits).toEqual([])

    const other = await context.newPage()
    const otherHits = await stubGoogle(other)
    await other.goto('/legal/terms')
    await expect(other.getByRole('region', { name: 'Analytics cookies' })).toBeVisible()

    await banner.getByRole('button', { name: 'Allow', exact: true }).click()
    await expect(banner).toBeHidden()
    await expect.poll(() => hits.some((u) => u.includes(`gtag/js?id=${id}`))).toBe(true)
    // The other tab follows without a reload.
    await expect(other.getByRole('region', { name: 'Analytics cookies' })).toBeHidden()
    await expect.poll(() => otherHits.some((u) => u.includes('gtag/js'))).toBe(true)

    // Page views carry the path only.
    await page.goto('/reset?token=secret-token')
    const sent = await page.evaluate(() => JSON.stringify((window as unknown as { dataLayer: ArrayLike<unknown>[] }).dataLayer.map((a) => Array.from(a))))
    expect(sent).toContain('/reset')
    expect(sent).not.toContain('secret-token')

    // Withdrawing is as easy: the footer's choice asks again.
    await page.getByRole('button', { name: 'Analytics choice' }).click()
    await page.getByRole('region', { name: 'Analytics cookies' }).getByRole('button', { name: 'Don’t allow' }).click()
    expect(await page.evaluate((gaId) => (window as unknown as Record<string, unknown>)[`ga-disable-${gaId}`], id)).toBe(true)
  })
})
