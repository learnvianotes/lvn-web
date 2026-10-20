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
   description, canonical link, robots and share tags (titles and
   descriptions: src/shared/lib/pages.ts). Routes come
   from content-build/catalog.json — the file `npm run
   content:seed` writes to Firestore — so a release that changes
   subjects or topics must seed and deploy the site together.
   ============================================================ */

import { readFileSync } from 'node:fs'
import type { Plugin } from 'vite'
import { sitePagesFor, type CatalogLike, type Page } from '../src/shared/lib/pages'

export { sitePagesFor }
export type { Page }
export type CatalogFile = CatalogLike

const NAME = 'LearnViaNotes'

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
