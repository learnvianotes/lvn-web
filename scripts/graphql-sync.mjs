#!/usr/bin/env node
/**
 * Copies the API's client-facing schema (lvn-backend contracts/graphql/schema.graphql, written by its
 * export-supergraph script) into graphql/schema.graphql, the input of `pnpm codegen`. Until @lvn/contracts is
 * published (lvn-backend ADR-0031) it is read from a sibling checkout; LVN_SCHEMA overrides the path.
 */
import { copyFileSync, existsSync } from 'node:fs'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '..')
const source = process.env.LVN_SCHEMA ?? path.resolve(root, '../lvn-backend/contracts/graphql/schema.graphql')
if (!existsSync(source)) {
  console.error(`No schema at ${source}. Check out lvn-backend next to lvn-web or set LVN_SCHEMA.`)
  process.exit(1)
}
copyFileSync(source, path.join(root, 'graphql/schema.graphql'))
console.log(`graphql/schema.graphql ← ${path.relative(root, source)}`)
