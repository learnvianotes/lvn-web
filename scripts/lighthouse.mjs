#!/usr/bin/env node
/**
 * Lighthouse on the public note page and the home page (lvn-backend spec §18, Phase 2 exit: ≥ 90 on the public note):
 * a production build of its own (.next-lighthouse: production app settings, so pages may be indexed, and the stand-in
 * API of the Playwright runs, tests/e2e/support/ssr-api.mjs, for server and browser), Playwright's Chromium, phone and
 * desktop. Reports go to lighthouse-report/. Without TLS here, the HTTPS audit is the only one not counted.
 *
 *   node scripts/lighthouse.mjs [--min 0.9] [--rebuild]
 */
import { spawn, spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'
import { chromium } from '@playwright/test'
import * as chromeLauncher from 'chrome-launcher'
import lighthouse, { desktopConfig } from 'lighthouse'

const root = path.resolve(import.meta.dirname, '..')
const min = Number(process.argv[process.argv.indexOf('--min') + 1] || 0.9) || 0.9
const port = 3102
const apiPort = 3198
const dist = '.next-lighthouse'
const api = `http://localhost:${apiPort}/graphql`
const env = {
  ...process.env,
  NEXT_DIST_DIR: dist,
  NEXT_PUBLIC_APP_ENV: 'production',
  NEXT_PUBLIC_SITE_URL: `http://localhost:${port}`,
  NEXT_PUBLIC_API_URL: api,
  API_INTERNAL_URL: api,
  SSR_API_PORT: String(apiPort),
  PORT: String(port),
}
const { notes } = JSON.parse(readFileSync(path.join(root, 'tests/e2e/support/public-notes.json'), 'utf8'))
const note = notes[0]
const pages = [
  { name: 'public-note', path: `/n/${note.slug}-${note.id}` },
  { name: 'home', path: '/' },
]

if (process.argv.includes('--rebuild') || !existsSync(path.join(root, dist, 'BUILD_ID'))) {
  console.log(`building into ${dist}…`)
  if (spawnSync('pnpm', ['build'], { cwd: root, env, stdio: 'inherit' }).status !== 0) process.exit(1)
}
const servers = [spawn('node', ['tests/e2e/support/ssr-api.mjs'], { cwd: root, env, stdio: 'ignore' }), spawn('pnpm', ['start', '-p', String(port)], { cwd: root, env, stdio: 'ignore' })]
const stop = () => servers.forEach((s) => s.kill('SIGTERM'))
process.on('exit', stop)

const base = `http://localhost:${port}`
for (let i = 0; ; i++) {
  try {
    if ((await fetch(base)).ok) break
  } catch {}
  if (i > 120) throw new Error('the web app did not start')
  await new Promise((r) => setTimeout(r, 500))
}

const chrome = await chromeLauncher.launch({ chromePath: chromium.executablePath(), chromeFlags: ['--headless=new', '--no-sandbox'] })
const out = path.join(root, 'lighthouse-report')
mkdirSync(out, { recursive: true })
const results = []
try {
  for (const page of pages) {
    for (const device of ['mobile', 'desktop']) {
      // Served over plain HTTP here; the deployed sites are HTTPS only.
      const run = await lighthouse(`${base}${page.path}`, { port: chrome.port, output: 'html', logLevel: 'error', skipAudits: ['is-on-https', 'redirects-http'] }, device === 'desktop' ? desktopConfig : undefined)
      writeFileSync(path.join(out, `${page.name}-${device}.html`), run.report)
      writeFileSync(path.join(out, `${page.name}-${device}.json`), JSON.stringify(run.lhr))
      const scores = Object.fromEntries(Object.entries(run.lhr.categories).map(([k, c]) => [k, c.score]))
      // What costs points: weighted audits below full marks, by category.
      const misses = Object.entries(run.lhr.categories).flatMap(([k, c]) =>
        c.auditRefs.filter((a) => a.weight > 0 && (run.lhr.audits[a.id]?.score ?? 1) < 1).map((a) => `${k}: ${a.id} (${run.lhr.audits[a.id].displayValue ?? Math.round((run.lhr.audits[a.id].score ?? 0) * 100)})`),
      )
      results.push({ page: page.name, device, scores, misses })
    }
  }
} finally {
  await chrome.kill()
  stop()
}

let failed = false
for (const r of results) {
  const line = Object.entries(r.scores).map(([k, v]) => `${k} ${Math.round((v ?? 0) * 100)}`).join('  ')
  const low = Object.entries(r.scores).filter(([, v]) => (v ?? 0) < min)
  if (r.page === 'public-note' && low.length) failed = true
  console.log(`${low.length ? '✗' : '✓'} ${r.page} (${r.device}): ${line}`)
  if (low.length) for (const m of r.misses) console.log(`    ${m}`)
}
writeFileSync(path.join(out, 'summary.json'), JSON.stringify({ min, results }, null, 2))
if (failed) {
  console.error(`The public note page scores below ${min * 100} (lighthouse-report/).`)
  process.exit(1)
}
