/* Bundles the TypeScript seeder (it reuses the app's React components to verify content) and runs it. */

import { build } from 'esbuild'
import { pathToFileURL } from 'node:url'
import path from 'node:path'

const root = path.resolve(import.meta.dirname, '../../..')
const outfile = path.join(root, 'node_modules/.cache/lvn-seed/main.mjs')

await build({
  entryPoints: [path.join(root, 'scripts/content/seed/main.ts')],
  outfile,
  bundle: true,
  platform: 'node',
  format: 'esm',
  target: 'node20',
  packages: 'external',
  tsconfig: path.join(root, 'tsconfig.app.json'),
  jsx: 'automatic',
  logLevel: 'warning',
  define: { 'import.meta.dirname': JSON.stringify(path.join(root, 'scripts/content/seed')) },
})

await import(pathToFileURL(outfile).href)
