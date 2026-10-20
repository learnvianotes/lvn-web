import { describe, expect, it } from 'vitest'
import { readFileSync } from 'node:fs'
import { clip, render404, renderPage, robotsTxt, sitemapXml, sitePagesFor, type CatalogFile } from './site-pages'

const catalog = JSON.parse(readFileSync(new URL('../content-build/catalog.json', import.meta.url), 'utf8')) as CatalogFile
const pages = sitePagesFor(catalog)
const SITE = 'https://www.learnvianotes.in'
const BASE = '<html><head>\n<meta name="description" content="old" />\n<title>LearnViaNotes</title>\n</head><body></body></html>'

describe('sitePagesFor', () => {
  it('has one page per subject and topic, plus the fixed pages, all distinct', () => {
    const topics = catalog.subjects.reduce((n, s) => n + s.topics.length, 0)
    expect(pages).toHaveLength(10 + catalog.subjects.length + topics)
    expect(new Set(pages.map((p) => p.path)).size).toBe(pages.length)
    for (const p of pages) expect(p.path === '/' || /^(\/[a-z0-9_-]+)+$/.test(p.path)).toBe(true)
  })
  it('keeps sign-in and personal pages out of search', () => {
    for (const path of ['/login', '/signup', '/forgot-password', '/history', '/settings']) {
      expect(pages.find((p) => p.path === path)?.index).toBe(false)
    }
  })
  it('points a notes subject at its first topic, and indexes the problem sheet itself', () => {
    const dsa = pages.find((p) => p.path === '/dsa-basics')!
    expect(dsa.canonical).toBe(`/dsa-basics/${catalog.subjects.find((s) => s.id === 'dsa-basics')!.topics[0].id}`)
    expect(pages.find((p) => p.path === '/sheet-150')).toMatchObject({ index: true, canonical: undefined })
  })
  it('writes descriptions of at most 155 characters', () => {
    for (const p of pages) expect(p.description.length).toBeLessThanOrEqual(155)
  })
})

describe('rendering', () => {
  it('sets the title, description, canonical and share tags, escaped', () => {
    const page = { path: '/a/b', title: 'Arrays & "Hashing"', description: 'x < y', index: true }
    const html = renderPage(BASE, page, SITE, true)
    expect(html).toContain('<title>Arrays &amp; &quot;Hashing&quot;</title>')
    expect(html).toContain('<meta name="description" content="x &lt; y" />')
    expect(html).toContain(`<link rel="canonical" href="${SITE}/a/b" />`)
    expect(html).toContain(`<meta property="og:url" content="${SITE}/a/b" />`)
    expect(html).not.toContain('noindex')
  })
  it('marks every page noindex outside production', () => {
    expect(renderPage(BASE, pages[0], 'https://test.web.app', false)).toContain('<meta name="robots" content="noindex" />')
  })
  it('404.html is noindex with no canonical', () => {
    const html = render404(BASE)
    expect(html).toContain('noindex')
    expect(html).not.toContain('canonical')
  })
  it('refuses an index.html it cannot fill', () => {
    expect(() => renderPage('<html><head></head></html>', pages[0], SITE, true)).toThrow()
  })
})

describe('robots.txt and sitemap.xml', () => {
  it('production allows crawling and names the sitemap; other builds disallow everything', () => {
    expect(robotsTxt(SITE, true)).toBe(`User-agent: *\nAllow: /\n\nSitemap: ${SITE}/sitemap.xml\n`)
    expect(robotsTxt('https://test.web.app', false)).toContain('Disallow: /\n')
  })
  it('lists only indexable pages that are their own canonical', () => {
    const xml = sitemapXml(pages, SITE)
    expect(xml).toContain(`<loc>${SITE}/</loc>`)
    expect(xml).toContain(`<loc>${SITE}/privacy</loc>`)
    expect(xml).toContain(`<loc>${SITE}/sheet-150</loc>`)
    expect(xml).not.toContain(`<loc>${SITE}/login</loc>`)
    expect(xml).not.toContain(`<loc>${SITE}/dsa-basics</loc>`)
    expect(xml.match(/<url>/g)).toHaveLength(pages.filter((p) => p.index && !p.canonical).length)
  })
})

describe('clip', () => {
  it('cuts at a word and adds an ellipsis', () => {
    expect(clip('one two three', 9)).toBe('one two…')
    expect(clip('short', 9)).toBe('short')
  })
})
