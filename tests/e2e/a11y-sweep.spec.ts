import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

/**
 * Phase 9's accessibility audit (lvn-backend docs/plans/phase-9.md, P9e): axe's WCAG 2.2 A and AA rules on every web
 * route of a deployed environment, signed out and as a new learner, at desktop and phone widths. Serious and critical
 * violations fail, as does any request the Content Security Policy refuses (lvn-backend ADR-0090). Admin pages are left
 * out (no API makes an admin). Skipped unless E2E_LIVE is set:
 *
 *   E2E_LIVE=1 E2E_BASE_URL=http://100.70.234.41:8080 pnpm test:e2e tests/e2e/a11y-sweep.spec.ts
 */
test.skip(!process.env.E2E_LIVE || !process.env.E2E_BASE_URL, 'needs a deployed environment: E2E_LIVE=1 E2E_BASE_URL=<public url>')
test.describe.configure({ timeout: 600_000 })

const TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']

type Finding = { path: string; rule: string; impact: string; help: string; targets: string[] }

/** Every Content Security Policy refusal the browser reports, by page. */
function watchCsp(page: Page, findings: Finding[]) {
  page.on('console', (msg) => {
    if (/Content Security Policy/i.test(msg.text())) findings.push({ path: new URL(page.url()).pathname, rule: 'csp', impact: 'serious', help: msg.text().slice(0, 300), targets: [] })
  })
}

async function audit(page: Page, path: string): Promise<Finding[]> {
  if (path) await page.goto(path)
  await page.waitForLoadState('networkidle').catch(() => undefined)
  await expect(page.locator('main').first()).toBeVisible()
  const { violations } = await new AxeBuilder({ page }).withTags(TAGS).analyze()
  return violations
    .filter((v) => v.impact === 'serious' || v.impact === 'critical')
    .map((v) => ({ path: path || page.url(), rule: v.id, impact: v.impact!, help: v.help, targets: v.nodes.slice(0, 3).map((n) => n.target.join(' ')) }))
}

async function report(findings: Finding[], info: { attach: (name: string, o: { body: string; contentType: string }) => Promise<void> }) {
  await info.attach('axe-findings.json', { body: JSON.stringify(findings, null, 2), contentType: 'application/json' })
  for (const f of findings) console.log(`${f.impact} ${f.rule} on ${f.path}: ${f.help} — ${f.targets.join(' | ')}`)
}

test('every public page has no serious or critical WCAG 2.2 AA violation', async ({ page }, info) => {
  const paths = ['/', '/sign-in', '/sign-up', '/reset', '/subjects', '/plans', '/legal/terms', '/legal/privacy', '/legal/content-licence', '/legal/grievance']
  const findings: Finding[] = []
  watchCsp(page, findings)
  for (const path of paths) findings.push(...(await audit(page, path)))
  // A subject and one of its topics, as a visitor reaches them.
  await page.goto('/subjects')
  const subject = page.getByRole('main').locator('a[href^="/subjects/"]').first()
  if (await subject.count()) {
    const href = (await subject.getAttribute('href'))!
    findings.push(...(await audit(page, href)))
    const topic = page.getByRole('main').locator(`a[href^="${href}/"]`).first()
    if (await topic.count()) findings.push(...(await audit(page, (await topic.getAttribute('href'))!)))
  }
  await report(findings, info)
  expect(findings).toEqual([])
})

test('every page a learner uses has no serious or critical WCAG 2.2 AA violation', async ({ page }, info) => {
  const findings: Finding[] = []
  watchCsp(page, findings)
  const email = `a11y-${Date.now()}-${Math.random().toString(36).slice(2, 8)}-${info.project.name}@example.com`
  await page.goto('/sign-up')
  await page.getByLabel('Your name').fill('Axe Learner')
  await page.getByLabel('Email', { exact: true }).fill(email)
  await page.getByLabel('Password').fill(`a11y passphrase ${Date.now()}`)
  await page.getByLabel('Date of birth').fill('2000-01-01')
  await page.getByRole('checkbox').check()
  await page.getByRole('button', { name: 'Create account' }).click()
  // Every date of birth is confirmed in words before it is sent (lvn-backend ADR-0091).
  await page.getByRole('dialog', { name: 'Is this right?' }).getByRole('button', { name: 'Yes, that’s right' }).click()
  await expect(page).toHaveURL(/\/profile$/)

  const paths = [
    '/profile', '/profile/notifications', '/profile/people', '/profile/skills', '/home', '/notes', '/saved', '/search?q=graphs',
    '/ask', '/review', '/rhythm', '/exams', '/history', '/achievements', '/quizzes', '/contests', '/community', '/groups', '/classes',
    '/resources', '/resources/new', '/resources/mine', '/resources/saved', '/notifications', '/teach', '/verify', '/subjects',
  ]
  // Client-side navigation keeps the in-memory session; a full load brings it back from the refresh cookie.
  for (const path of paths) findings.push(...(await audit(page, path)))

  // A note of their own, open in the editor.
  await page.goto('/notes')
  await page.getByRole('button', { name: 'New note' }).first().click()
  await expect(page).toHaveURL(/\/notes\/[0-9a-f-]{36}/)
  await page.waitForTimeout(1_000)
  findings.push(...(await audit(page, '')))

  // Their public profile.
  await page.goto('/profile')
  const own = page.getByRole('main').locator('a[href^="/u/"]').first()
  if (await own.count()) findings.push(...(await audit(page, (await own.getAttribute('href'))!)))

  await report(findings, info)
  expect(findings).toEqual([])
})
