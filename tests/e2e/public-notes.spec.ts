import { readFileSync } from 'node:fs'
import { expect, test } from '@playwright/test'
import { E2E_REVALIDATE_SECRET } from './support/constants'

/**
 * Public note pages (P2d): rendered on the server from the API (here tests/e2e/support/ssr-api.mjs), one address per
 * note, metadata for sharing and search, and refreshes the API asks for.
 */

type Fixture = { id: string; slug: string; cards: { media: { id: string } | null }[] }
const note = (JSON.parse(readFileSync(new URL('./support/public-notes.json', import.meta.url), 'utf8')) as { notes: Fixture[] }).notes[0]!
const path = `/n/${note.slug}-${note.id}`
const PNG = Buffer.from('89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360f8cfc0f01f0005000201a1d0f3a50000000049454e44ae426082', 'hex')

test('anyone reads a public note without an account', async ({ page }) => {
  // In the browser the API answers that nobody is signed in.
  await page.route('**/graphql', (route) => route.fulfill({ json: { data: { refreshSession: null } } }))
  const res = await page.goto(path)
  expect(res?.status()).toBe(200)
  await expect(page.getByRole('heading', { level: 1, name: "Dijkstra's algorithm" })).toBeVisible()
  await expect(page.getByText('Ravi Kumar')).toBeVisible()
  await expect(page.getByText('Always settle the closest unvisited vertex next.')).toBeVisible()
  await expect(page.getByText('Shortest paths · Algorithms')).toBeVisible()
  await expect(page.getByRole('link', { name: 'Start writing' })).toHaveAttribute('href', '/sign-up')
  // The discussion is for signed-in readers (lvn-backend ADR-0047).
  await expect(page.getByRole('link', { name: 'Sign in to join the discussion.' })).toHaveAttribute('href', `/sign-in?next=${encodeURIComponent(path)}`)
  // For sharing and search engines.
  await expect(page.locator('link[rel="canonical"]')).toHaveAttribute('href', new RegExp(`${path}$`))
  await expect(page.locator('meta[property="og:title"]')).toHaveAttribute('content', "Dijkstra's algorithm")
  await expect(page.locator('meta[property="og:image"]')).toHaveAttribute('content', /opengraph-image/)
  const ld = JSON.parse((await page.locator('script[type="application/ld+json"]').textContent())!) as Record<string, unknown>
  expect(ld).toMatchObject({ '@type': 'Article', headline: "Dijkstra's algorithm", author: { name: 'Ravi Kumar' } })
})

test('one address per note: a missing or old slug moves to the current one', async ({ page }) => {
  await page.goto(`/n/${note.id}`)
  await expect(page).toHaveURL(new RegExp(`${path}$`))
  await page.goto(`/n/an-old-title-${note.id}`)
  await expect(page).toHaveURL(new RegExp(`${path}$`))
})

test('a note nobody may read is not found', async ({ page }) => {
  const res = await page.goto('/n/secret-01920000-0000-7000-8000-00000000dfff')
  expect(res?.status()).toBe(404)
})

test('pictures get fresh read URLs in the browser', async ({ page }) => {
  await page.route('**/graphql', (route) =>
    route.fulfill({ json: { data: { note: { cards: { edges: [{ node: { media: null } }, { node: { media: null } }, { node: { media: { id: note.cards[2]!.media!.id, url: 'http://storage.test/get/graph.png', mimeType: 'image/png', fileName: 'graph.png', sizeBytes: PNG.length } } }] } } } } }),
  )
  await page.route('http://storage.test/**', (route) => route.fulfill({ status: 200, headers: { 'content-type': 'image/png' }, body: PNG }))
  await page.goto(path)
  await expect(page.getByRole('img', { name: 'A small weighted graph' })).toHaveAttribute('src', 'http://storage.test/get/graph.png')
})

test('the sitemap lists public notes, and the share picture renders', async ({ page, request }) => {
  const sitemap = await (await request.get('/sitemap.xml')).text()
  expect(sitemap).toContain(path)
  // The address Next gives the picture (with a content hash), as link previews find it.
  await page.goto(path)
  const og = new URL((await page.locator('meta[property="og:image"]').getAttribute('content'))!)
  const image = await request.get(`${og.pathname}${og.search}`)
  expect(image.status()).toBe(200)
  expect(image.headers()['content-type']).toBe('image/png')
})

test('refreshes need the shared secret and known tags', async ({ request }) => {
  const post = (secret: string, tags: unknown) => request.post('/api/revalidate', { headers: { 'x-revalidate-secret': secret }, data: { tags } })
  expect((await post('wrong', [`note:${note.id}`])).status()).toBe(401)
  expect((await post(E2E_REVALIDATE_SECRET, ['../../etc'])).status()).toBe(400)
  const ok = await post(E2E_REVALIDATE_SECRET, [`note:${note.id}`, 'public-notes'])
  expect(ok.status()).toBe(200)
  expect(await ok.json()).toEqual({ revalidated: [`note:${note.id}`, 'public-notes'] })
})

test('a public note shows its study aids, rendered by the server; saving their cards leads into the app (lvn-backend ADR-0061)', async ({ page }) => {
  await page.goto(path)
  const aids = page.getByRole('region', { name: 'Study aids' })
  await expect(aids.getByRole('tab', { name: 'Summarise' })).toHaveAttribute('aria-selected', 'true')
  await expect(aids.locator('strong')).toHaveText('shortest paths')
  await aids.getByRole('tab', { name: 'Flashcards' }).click()
  await expect(aids.getByText('What must edge weights be?')).toBeVisible()
  await expect(aids.getByRole('link', { name: 'Save these cards in your notes' })).toHaveAttribute('href', `/notes/${note.id}`)
  // Server-rendered: the summary is in the page's HTML for readers and search engines.
  expect(await (await page.request.get(path)).text()).toContain('shortest paths')
})
