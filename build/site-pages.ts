/* ============================================================
   SITE PAGES — every real address gets its own HTML file, so the
   host can answer anything else with a real 404 (404.html), not
   the app with a 200.

     /                      index.html (the home head)
     /about, /privacy, …    <path>/index.html
     /<subject>             one per catalog subject
     /<subject>/<topic>     one per topic (and Sheet 150 category)
     404.html               noindex; the app then shows "Page not found"
     robots.txt             production: allow + sitemap; other builds: Disallow /
     sitemap.xml            the indexable pages (production only)

   Each file is the built index.html with its own <title>,
   description, canonical link, robots and share tags. Routes come
   from content-build/catalog.json — the file `npm run
   content:seed` writes to Firestore — so a release that changes
   subjects or topics must seed and deploy the site together.
   ============================================================ */

import { readFileSync } from 'node:fs'
import type { Plugin } from 'vite'
import { LEGAL_PAGES } from '../src/features/legal/legal'
import { LEGAL } from '../src/config'

export interface CatalogFile {
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
  /** where search engines should send people (defaults to the page itself) */
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

export function sitePagesFor(catalog: CatalogFile): Page[] {
  const day = catalog.generatedAt.slice(0, 10)
  const pages: Page[] = [
    { path: '/', title: `${NAME} — interview-ready CS notes and coding problems`, description: HOME_DESCRIPTION, index: true, lastmod: day },
    { path: '/about', title: `About · ${NAME}`, description: `What ${NAME} is, the study tools it has and every subject it covers.`, index: true, lastmod: day },
    ...Object.values(LEGAL_PAGES).map((p) => ({ path: p.path, title: `${p.title} · ${NAME}`, description: p.description, index: true, lastmod: LEGAL.effective })),
    { path: '/login', title: `Log in · ${NAME}`, description: `Log in to ${NAME} to keep your streak and study history in sync.`, index: false },
    { path: '/signup', title: `Create your account · ${NAME}`, description: `Create a free ${NAME} account to keep your streak and study history in sync.`, index: false },
    { path: '/forgot-password', title: `Reset your password · ${NAME}`, description: `Reset your ${NAME} password.`, index: false },
    { path: '/history', title: `History · ${NAME}`, description: `Your ${NAME} study history.`, index: false },
    { path: '/settings', title: `Settings · ${NAME}`, description: `Your ${NAME} settings.`, index: false },
  ]
  for (const s of catalog.subjects) {
    const first = s.topics[0]
    pages.push({
      path: `/${s.id}`,
      title: s.kind === 'problems' ? `${s.title}: ${s.topics.reduce((n, t) => n + (t.problems?.length ?? 0), 0)} coding interview problems · ${NAME}` : `${s.title} notes · ${NAME}`,
      description: clip(s.description),
      // A notes subject opens its first topic, so that topic is the page to index.
      index: s.kind === 'problems',
      canonical: s.kind === 'notes' && first ? `/${s.id}/${first.id}` : undefined,
      lastmod: day,
    })
    for (const t of s.topics) {
      const detail = t.problems?.length
        ? `${t.problems.length} problems with solutions in Python, C++, Java and JavaScript: ${t.problems.map((p) => p.title).join(', ')}`
        : (t.headings ?? []).join(', ')
      pages.push({
        path: `/${s.id}/${t.id}`,
        title: `${t.title} — ${s.title} · ${NAME}`,
        description: clip(detail ? `${t.title}: ${detail}.` : `${t.title} — ${s.title} notes on ${NAME}.`),
        index: true,
        lastmod: day,
        breadcrumbs: [{ name: s.title, path: `/${s.id}` }, { name: t.title, path: `/${s.id}/${t.id}` }],
      })
    }
  }
  return pages
}

/* ── rendering ───────────────────────────────────────────── */

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
const jsonLd = (data: unknown) => `<script type="application/ld+json">${JSON.stringify(data).replace(/</g, '\\u003c')}</script>`

/** The base index.html with this page's head. `site` has no trailing slash. */
export function renderPage(html: string, page: Page, site: string, live: boolean): string {
  const url = site + (page.path === '/' ? '/' : page.path)
  const canonical = page.canonical ? site + page.canonical : url
  const tags = [
    `<link rel="canonical" href="${esc(canonical)}" />`,
    !page.index || !live ? '<meta name="robots" content="noindex" />' : '',
    `<meta property="og:type" content="website" />`,
    `<meta property="og:site_name" content="${NAME}" />`,
    `<meta property="og:title" content="${esc(page.title)}" />`,
    `<meta property="og:description" content="${esc(page.description)}" />`,
    `<meta property="og:url" content="${esc(url)}" />`,
    `<meta property="og:image" content="${esc(site)}/icons/icon-512.png" />`,
    `<meta name="twitter:card" content="summary" />`,
    page.path === '/'
      ? jsonLd([
          { '@context': 'https://schema.org', '@type': 'WebSite', name: NAME, url: `${site}/` },
          { '@context': 'https://schema.org', '@type': 'Organization', name: NAME, url: `${site}/`, logo: `${site}/icons/icon-512.png` },
        ])
      : '',
    page.breadcrumbs
      ? jsonLd({
          '@context': 'https://schema.org',
          '@type': 'BreadcrumbList',
          itemListElement: page.breadcrumbs.map((b, i) => ({ '@type': 'ListItem', position: i + 1, name: b.name, item: site + b.path })),
        })
      : '',
  ].filter(Boolean)
  return withHead(html, page.title, page.description, tags)
}

export function render404(html: string): string {
  return withHead(html, `Page not found · ${NAME}`, `This page doesn’t exist on ${NAME}.`, ['<meta name="robots" content="noindex" />'])
}

function withHead(html: string, title: string, description: string, tags: string[]): string {
  const out = html
    .replace(/<title>[^<]*<\/title>/, `<title>${esc(title)}</title>`)
    .replace(/<meta name="description" content="[^"]*"\s*\/?>/, `<meta name="description" content="${esc(description)}" />`)
    .replace('</head>', `\n    ${tags.join('\n    ')}\n  </head>`)
  if (!out.includes(`<title>${esc(title)}</title>`) || !out.includes(`content="${esc(description)}"`)) {
    throw new Error('site-pages: index.html has no <title> or <meta name="description"> to replace')
  }
  return out
}

export function robotsTxt(site: string, live: boolean): string {
  return live
    ? `User-agent: *\nAllow: /\n\nSitemap: ${site}/sitemap.xml\n`
    : '# Not the live site: keep it out of search engines.\nUser-agent: *\nDisallow: /\n'
}

export function sitemapXml(pages: Page[], site: string): string {
  const urls = pages
    .filter((p) => p.index && !p.canonical)
    .map((p) => `  <url><loc>${esc(site + (p.path === '/' ? '/' : p.path))}</loc>${p.lastmod ? `<lastmod>${p.lastmod}</lastmod>` : ''}</url>`)
  return `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>\n`
}

/* ── the Vite plugin ─────────────────────────────────────── */

export function sitePages({ catalogFile }: { catalogFile: string }): Plugin {
  let site = ''
  let live = false
  let base = ''
  return {
    name: 'lvn-site-pages',
    apply: 'build',
    enforce: 'post',
    configResolved(config) {
      site = String(config.env.VITE_SITE_URL ?? '').replace(/\/+$/, '')
      live = config.env.VITE_SITE_ENV === 'production'
      if (!/^https?:\/\/[^/]+$/.test(site)) throw new Error(`site-pages: VITE_SITE_URL must be the site's origin (got "${site}")`)
    },
    transformIndexHtml: {
      order: 'post',
      handler(html) {
        base = html
        const home = sitePagesFor(JSON.parse(readFileSync(catalogFile, 'utf8')) as CatalogFile)[0]
        return renderPage(html, home, site, live)
      },
    },
    generateBundle() {
      const pages = sitePagesFor(JSON.parse(readFileSync(catalogFile, 'utf8')) as CatalogFile)
      const seen = new Set<string>()
      for (const page of pages.slice(1)) {
        if (seen.has(page.path)) throw new Error(`site-pages: two pages at ${page.path}`)
        seen.add(page.path)
        this.emitFile({ type: 'asset', fileName: `${page.path.slice(1)}/index.html`, source: renderPage(base, page, site, live) })
      }
      this.emitFile({ type: 'asset', fileName: '404.html', source: render404(base) })
      this.emitFile({ type: 'asset', fileName: 'robots.txt', source: robotsTxt(site, live) })
      if (live) this.emitFile({ type: 'asset', fileName: 'sitemap.xml', source: sitemapXml(pages, site) })
    },
  }
}
