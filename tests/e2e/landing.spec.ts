import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

test('landing page leads to the subjects, the app’s own (no /core)', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await page.getByRole('main').getByRole('link', { name: 'Browse subjects' }).click()
  await expect(page).toHaveURL(/\/subjects$/)
  await expect(page.getByRole('heading', { level: 1, name: 'Subjects' })).toBeVisible()
  await expect(page.getByRole('link', { name: /Operating Systems/ })).toHaveAttribute('href', '/subjects/os')
})

test('a subject card opens the subject; a topic lists its public notes, with the way back', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('main').getByRole('link', { name: /Data Structures and Algorithms/ }).click()
  await expect(page).toHaveURL(/\/subjects\/dsa$/)
  await expect(page.getByRole('heading', { level: 1, name: 'Data Structures and Algorithms' })).toBeVisible()
  await page.getByRole('link', { name: 'Graphs', exact: true }).click()
  await expect(page).toHaveURL(/\/subjects\/dsa\/graphs$/)
  await expect(page.getByRole('region', { name: 'Public notes' }).getByRole('link').first()).toHaveAttribute('href', /^\/n\//)
  await expect(page.getByRole('link', { name: 'Shortest paths' })).toHaveAttribute('href', '/subjects/dsa/shortest-paths')
  await page.getByRole('navigation', { name: 'Where you are' }).getByRole('link', { name: 'Subjects' }).click()
  await expect(page).toHaveURL(/\/subjects$/)
})

test('old /core and root subject addresses lead to the subjects while /core is off', async ({ page }) => {
  await page.goto('/core')
  await expect(page).toHaveURL(/\/subjects$/)
  await page.goto('/core/dsa/heaps')
  await expect(page).toHaveURL(/\/subjects\/dsa$/)
  // The old site's root subject addresses too (python was one).
  await page.goto('/python/variables')
  await expect(page).toHaveURL(/\/subjects\/python$/)
  // A topic with nothing on it yet says so, and leads to writing one.
  await page.goto('/subjects/os/paging')
  await expect(page.getByText('No public notes on Paging yet.')).toBeVisible()
  expect((await page.goto('/subjects/nope'))?.status()).toBe(404)
})

test('unknown URLs get the site 404', async ({ page }) => {
  const res = await page.goto('/definitely-not-here')
  expect(res?.status()).toBe(404)
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
})

test('sitemap lists the subjects and their topics, resources and the legal pages, not /core', async ({ request }) => {
  const xml = await (await request.get('/sitemap.xml')).text()
  expect(xml).toContain('/subjects/dsa</loc>')
  expect(xml).toContain('/subjects/dsa/shortest-paths</loc>')
  expect(xml).toContain('/resources</loc>')
  for (const path of ['/legal/terms', '/legal/privacy', '/legal/content-licence', '/legal/grievance']) expect(xml).toContain(`${path}</loc>`)
  expect(xml).not.toContain('/core')
  // Every listed address is a real page.
  const paths = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => new URL(m[1]!).pathname).slice(0, 25)
  for (const path of paths) expect((await request.get(path)).status(), path).toBe(200)
})

test('every kind of public address answers a real 404 when there is nothing there', async ({ request }) => {
  for (const path of ['/no-such-page', '/subjects/nope', '/subjects/dsa/nope', '/n/nothing-01920000-0000-7000-8000-0000000000ff', '/u/nobody-here', '/legal/nope', '/subjects/dsa/graphs/extra']) {
    expect((await request.get(path)).status(), path).toBe(404)
  }
})

test('outside production, robots.txt keeps the whole site out of search engines', async ({ request }) => {
  // The e2e build is a development build (production: allow and the sitemap, app/robots.ts).
  expect(await (await request.get('/robots.txt')).text()).toMatch(/User-Agent: \*\s+Disallow: \//)
})

test('landing page has no serious accessibility violations', async ({ page }) => {
  // Checked as it settles: fade-ins would be measured half-transparent.
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto('/')
  const { violations } = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
  expect(violations.filter((v) => v.impact === 'critical' || v.impact === 'serious').map((v) => v.id)).toEqual([])
})
