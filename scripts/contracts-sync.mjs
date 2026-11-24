#!/usr/bin/env node
/**
 * Copies the parts of @lvn/contracts the web app runs (card content, rich text, card positions, note names, drawings, usage events, notification and
 * live-event shapes and the enums they use) from lvn-backend into lib/contracts/, until the package is published (lvn-backend ADR-0031) — as
 * graphql:sync does for the schema. The copies are committed and never edited here.
 *
 *   node scripts/contracts-sync.mjs           copy (LVN_CONTRACTS overrides ../lvn-backend/contracts)
 *   node scripts/contracts-sync.mjs --check   fail if a copy differs from lvn-backend (CI)
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import path from 'node:path'

const FILES = ['domain/enums.ts', 'domain/usage-events.ts', 'validation/index.ts', 'validation/drawing.ts', 'validation/usage-events.ts', 'validation/cards.ts', 'validation/rich-text.ts', 'validation/positions.ts', 'validation/notes.ts', 'validation/learning.ts', 'validation/resources.ts', 'notifications/index.ts']
const root = path.resolve(import.meta.dirname, '..')
const source = path.join(process.env.LVN_CONTRACTS ?? path.resolve(root, '../lvn-backend/contracts'), 'src')
const target = path.join(root, 'lib/contracts')
const check = process.argv.includes('--check')
const header = (file) => `// Copied from lvn-backend contracts/src/${file} by scripts/contracts-sync.mjs — do not edit here.\n`

if (!existsSync(source)) {
  console.error(`No contracts at ${source}. Check out lvn-backend next to lvn-web or set LVN_CONTRACTS.`)
  process.exit(1)
}
let stale = 0
for (const file of FILES) {
  const wanted = header(file) + readFileSync(path.join(source, file), 'utf8')
  const out = path.join(target, file)
  if (check) {
    if (!existsSync(out) || readFileSync(out, 'utf8') !== wanted) {
      console.error(`lib/contracts/${file} differs from lvn-backend; run pnpm contracts:sync`)
      stale++
    }
    continue
  }
  mkdirSync(path.dirname(out), { recursive: true })
  writeFileSync(out, wanted)
}
if (stale) process.exit(1)
console.log(check ? `lib/contracts matches lvn-backend (${FILES.length} files)` : `lib/contracts ← ${path.relative(root, source)} (${FILES.length} files)`)
