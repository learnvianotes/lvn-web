/* ============================================================
   Page titles and descriptions for a /core path. Used by the
   server for the first paint (and search engines) and by the
   router on every navigation, so the two always agree.
   ============================================================ */

import { APP_NAME } from '@core/config'
import type { Catalog } from '@core/features/catalog/types'

export const SITE_DESCRIPTION = `${APP_NAME} — quick, focused notes for CS interview preparation. Nothing required, just learn.`

export interface PageInfo {
  title: string
  description: string
}

/** `segments` is the path below /core, e.g. ['python', 'variables']. */
export function pageInfo(catalog: Catalog | undefined, segments: string[]): PageInfo {
  const [first, second] = segments
  if (!first) return { title: APP_NAME, description: SITE_DESCRIPTION }
  if (first === 'about' && !second) return { title: `About · ${APP_NAME}`, description: SITE_DESCRIPTION }
  const subject = catalog?.subjects.find((s) => s.id === first)
  if (!subject) return { title: APP_NAME, description: SITE_DESCRIPTION }
  if (!second) return { title: `${subject.title} · ${APP_NAME}`, description: subject.description }
  const topic = subject.topics.find((t) => t.id === second)
  if (!topic) return { title: `${subject.title} · ${APP_NAME}`, description: subject.description }
  const description = subject.kind === 'problems'
    ? `${topic.title}: ${topic.problems?.length ?? 0} interview problems from ${subject.title}, each with a naive and an optimal solution in Python, C++, Java and JavaScript.`
    : `${topic.title} — ${subject.title} notes on ${APP_NAME}.${topic.headings?.length ? ` Covers ${topic.headings.slice(0, 4).join(', ')}.` : ''}`
  return { title: `${topic.title} · ${subject.title} · ${APP_NAME}`, description }
}
