import 'server-only'
import { readFileSync } from 'node:fs'
import path from 'node:path'
import { cache } from 'react'
import { catalog, type Catalog } from './schema'

/**
 * Reads the catalog of the existing study content from content-build/ at build time, for the landing page
 * and sitemap.xml (the /core pages read the same files through core-app/server/content.ts). When the
 * `notes` context owns Subjects and Topics (Phase 2), this module is the one place that switches to GraphQL.
 */

const CATALOG = path.join(process.cwd(), 'content-build', 'catalog.json')

export const getCatalog = cache((): Catalog => {
  const data = catalog.parse(JSON.parse(readFileSync(CATALOG, 'utf8')))
  data.subjects.sort((a, b) => a.order - b.order)
  return data
})
