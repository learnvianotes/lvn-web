/* ============================================================
   PAGES — the title, description and canonical address of every
   page, in one place: the build writes them into each page's HTML
   (build/site-pages.ts) and the app sets them as you move around
   (app/shell/AppShell.tsx → usePageMeta).
   Relative imports: the build bundles this file without the @/ alias.
   ============================================================ */

import { LEGAL } from '../../config'
import { LEGAL_PAGES } from '../../features/legal/legal'

/** The catalog fields pages need (content-build/catalog.json, or the app's Catalog). */
export interface CatalogLike {
  generatedAt: string
  subjects: {
    id: string
    title: string
    description: string
    kind: 'notes' | 'problems'
    topics: { id: string; title: string; headings?: string[]; problems?: { title: string }[] }[]
  }[]
}

export interface Page {
  /** "/" or "/a/b" — no trailing slash */
  path: string
  title: string
  description: string
  /** false: noindex, and left out of the sitemap */
  index: boolean
  /** the page search engines should send people to, when it isn't this one */
  canonical?: string
  lastmod?: string
  breadcrumbs?: { name: string; path: string }[]
}

const NAME = 'LearnViaNotes'
const HOME_DESCRIPTION =
  'Free notes for CS interviews: DSA, 150 coding problems solved in Python, C++, Java and JavaScript, system design, DBMS, OS, networks, AI and more.'

/** At most `max` characters, cut at a word, with an ellipsis when cut. */
export function clip(text: string, max = 155): string {
  const t = text.replace(/\s+/g, ' ').trim()
  if (t.length <= max) return t
  return `${t.slice(0, max - 1).replace(/[\s,;:—-]+\S*$/, '')}…`
}

/** Pages that exist whatever the catalog holds. */
export function fixedPages(lastmod?: string): Page[] {
  return [
    { path: '/', title: `${NAME} — interview-ready CS notes and coding problems`, description: HOME_DESCRIPTION, index: true, lastmod },
    { path: '/about', title: `About · ${NAME}`, description: `What ${NAME} is, the study tools it has and every subject it covers.`, index: true, lastmod },
    ...Object.values(LEGAL_PAGES).map((p) => ({ path: p.path, title: `${p.title} · ${NAME}`, description: p.description, index: true, lastmod: LEGAL.effective })),
    { path: '/login', title: `Log in · ${NAME}`, description: `Log in to ${NAME} to keep your streak and study history in sync.`, index: false },
    { path: '/signup', title: `Create your account · ${NAME}`, description: `Create a free ${NAME} account to keep your streak and study history in sync.`, index: false },
    { path: '/forgot-password', title: `Reset your password · ${NAME}`, description: `Reset your ${NAME} password.`, index: false },
    { path: '/history', title: `History · ${NAME}`, description: `Your ${NAME} study history.`, index: false },
    { path: '/settings', title: `Settings · ${NAME}`, description: `Your ${NAME} settings.`, index: false },
  ]
}

type Subject = CatalogLike['subjects'][number]

function subjectPage(s: Subject, lastmod?: string): Page {
  const first = s.topics[0]
  const problems = s.topics.reduce((n, t) => n + (t.problems?.length ?? 0), 0)
  return {
    path: `/${s.id}`,
    title: s.kind === 'problems' ? `${s.title}: ${problems} coding interview problems · ${NAME}` : `${s.title} notes · ${NAME}`,
    description: clip(s.description),
    // A notes subject opens its first topic, so that topic is the page to index.
    index: s.kind === 'problems',
    canonical: s.kind === 'notes' && first ? `/${s.id}/${first.id}` : undefined,
    lastmod,
  }
}

function topicPage(s: Subject, t: Subject['topics'][number], lastmod?: string): Page {
  const detail = t.problems?.length
    ? `${t.problems.length} problems with solutions in Python, C++, Java and JavaScript: ${t.problems.map((p) => p.title).join(', ')}`
    : (t.headings ?? []).join(', ')
  return {
    path: `/${s.id}/${t.id}`,
    title: `${t.title} — ${s.title} · ${NAME}`,
    description: clip(detail ? `${t.title}: ${detail}.` : `${t.title} — ${s.title} notes on ${NAME}.`),
    index: true,
    lastmod,
    breadcrumbs: [{ name: s.title, path: `/${s.id}` }, { name: t.title, path: `/${s.id}/${t.id}` }],
  }
}

/** Every page of the site. */
export function sitePagesFor(catalog: CatalogLike): Page[] {
  const day = catalog.generatedAt.slice(0, 10)
  const pages = fixedPages(day)
  for (const s of catalog.subjects) {
    pages.push(subjectPage(s, day))
    for (const t of s.topics) pages.push(topicPage(s, t, day))
  }
  return pages
}

/** The page at `path` (no trailing slash), or undefined if there is none. */
export function pageFor(path: string, catalog?: CatalogLike | null): Page | undefined {
  const fixed = fixedPages().find((p) => p.path === path)
  if (fixed || !catalog) return fixed
  const [, sid, tid, extra] = path.split('/')
  const s = catalog.subjects.find((x) => x.id === sid)
  if (!s || extra !== undefined) return undefined
  if (tid === undefined) return subjectPage(s)
  const t = s.topics.find((x) => x.id === tid)
  return t && topicPage(s, t)
}
