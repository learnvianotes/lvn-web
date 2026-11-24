#!/usr/bin/env node
/**
 * Every operation document under graphql/operations must validate against the vendored
 * schema, and application code must not keep a second, unchecked copy of a request.
 */
import { readdirSync, readFileSync, statSync } from 'node:fs'
import path from 'node:path'
import { buildSchema, parse, validate } from 'graphql'

const root = path.resolve(import.meta.dirname, '..')
const schema = buildSchema(readFileSync(path.join(root, 'graphql/schema.graphql'), 'utf8'))
const operationsDir = path.join(root, 'graphql/operations')
const files = readdirSync(operationsDir).filter((name) => name.endsWith('.graphql')).sort()
if (!files.length) {
  console.error('graphql/operations is empty')
  process.exit(1)
}

const source = files.map((name) => readFileSync(path.join(operationsDir, name), 'utf8')).join('\n')
let document
try {
  document = parse(source)
} catch (error) {
  console.error(error instanceof Error ? error.message : error)
  process.exit(1)
}
const errors = validate(schema, document)
if (errors.length) {
  for (const error of errors) console.error(error.message)
  process.exit(1)
}

// The live socket is a graphql-ws subscription. This schema has no Subscription type
// (see graphql/operations/notifications.graphql), so that one string cannot move here.
const allowed = new Set(['features/notifications/live.ts'])
const operation = /(?:query|mutation|subscription)\s+[A-Z][A-Za-z0-9_]*\s*(?:\([^)]*\))?\s*\{/
const handwritten = []
for (const file of walk(root)) {
  const rel = path.relative(root, file)
  if (allowed.has(rel) || rel === 'scripts/graphql-check.mjs') continue
  const text = readFileSync(file, 'utf8')
  if (operation.test(text) || /import\s*\{[^}]*\bparse\b[^}]*\}\s*from\s*['"]graphql['"]/.test(text)) handwritten.push(rel)
}
if (handwritten.length) {
  console.error('GraphQL operations belong in graphql/operations so codegen checks them:')
  for (const file of handwritten) console.error(`  ${file}`)
  process.exit(1)
}

console.log(`graphql:check ok (${files.length} files)`)

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    // .next and .next-e2e hold build output (bundled copies of the operations), not sources.
    if (name === 'node_modules' || name === '.git' || name.startsWith('.next') || name === 'graphql' || name === 'tests' || name === 'content-src' || name === 'content-build' || name === 'core-app') continue
    const full = path.join(dir, name)
    if (statSync(full).isDirectory()) walk(full, out)
    else if (/\.(ts|tsx|js|mjs|cjs)$/.test(name)) out.push(full)
  }
  return out
}
