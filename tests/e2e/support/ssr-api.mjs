// A stand-in for lvn-backend that server rendering talks to in Playwright runs (API_INTERNAL_URL): public notes from
// public-notes.json, profiles from profiles.json (by handle, any case, or id), anything else unknown. The browser's own GraphQL calls are mocked per test with page.route.
import { readFileSync } from 'node:fs'
import { createServer } from 'node:http'

const { notes } = JSON.parse(readFileSync(new URL('./public-notes.json', import.meta.url), 'utf8'))
const { profiles } = JSON.parse(readFileSync(new URL('./profiles.json', import.meta.url), 'utf8'))
const { subjects } = JSON.parse(readFileSync(new URL('./subjects.json', import.meta.url), 'utf8'))
const port = Number(process.env.SSR_API_PORT ?? 3199)

const answer = (query, variables) => {
  if (query.includes('query PublicNotes(')) {
    return { publicNotes: { edges: notes.map((n) => ({ node: { id: n.id, slug: n.slug, publishedAt: n.publishedAt } })), pageInfo: { hasNextPage: false, endCursor: null } } }
  }
  if (query.includes('query PublicProfile(')) {
    const h = String(variables.handle).replace(/^@/, '').toLowerCase()
    return { userByHandle: profiles.find((p) => p.handle === h || p.id === h) ?? null }
  }
  if (query.includes('query PublicNote(')) {
    const n = notes.find((x) => x.id === variables.id)
    if (!n) return { note: null }
    const { cards, ...rest } = n
    return { note: { ...rest, cards: { edges: cards.map((node) => ({ node })), pageInfo: { hasNextPage: false, endCursor: null } } } }
  }
  // Subjects (no /core, owner 2026-10-14): the catalogue, one subject, and the public notes on a subject or topic.
  if (query.includes('query Subjects ')) return { subjects }
  if (query.includes('query Subject(')) return { subject: subjects.find((s) => s.slug === variables.slug) ?? null }
  if (query.includes('query SubjectShelf(')) {
    const graphs = variables.filters?.topicId === '01920000-0000-7000-8000-00000000c511'
    return { search: { notes: graphs ? notes.slice(0, 1).map((n) => ({ note: { id: n.id, title: n.title, slug: n.slug, kind: n.kind ?? 'NOTE', publishedAt: n.publishedAt, owner: { displayName: n.owner?.displayName ?? 'Ravi Kumar' } } })) : [] } }
  }
  if (query.includes('query TopicResources(')) return { resources: { edges: [] } }
  if (query.includes('query SitemapResources(')) return { resources: { edges: [], pageInfo: { hasNextPage: false, endCursor: null } } }
  // The terms version an admin chose (lvn-backend ADR-0103): an older published one, so the legal pages' label is
  // seen to come from the API rather than this build's newest version (tests/e2e/legal.spec.ts).
  if (query.includes('query LegalTermsVersion')) return { termsVersion: '2026-10-08' }
  // One-click unsubscribe (lvn-backend ADR-0050): the token "good" turns off class emails; anything else is refused.
  if (query.includes('unsubscribeEmail(')) {
    return { unsubscribeEmail: variables.token === 'good' ? { kind: 'CLASSROOM_POST', userErrors: [] } : { kind: null, userErrors: [{ message: 'This unsubscribe link is not valid.' }] } }
  }
  return null
}

// The browser's own calls (Lighthouse runs, scripts/lighthouse.mjs) come from the web app's origin.
// Sign-in checks send cookies, so the origin is echoed rather than '*'.
const cors = (req) => ({ 'access-control-allow-origin': req.headers.origin ?? '*', 'access-control-allow-credentials': 'true', 'access-control-allow-headers': req.headers['access-control-request-headers'] ?? '*', 'access-control-allow-methods': 'POST, GET, OPTIONS' })

createServer((req, res) => {
  if (req.method === 'OPTIONS') return res.writeHead(204, cors(req)).end()
  if (req.method === 'GET') return res.writeHead(200).end('ok')
  let raw = ''
  req.on('data', (c) => (raw += c))
  req.on('end', () => {
    const { query, variables } = JSON.parse(raw)
    const data = answer(query, variables ?? {})
    res.writeHead(200, { 'content-type': 'application/json', ...cors(req) })
    res.end(JSON.stringify(data ? { data } : { errors: [{ message: 'not mocked' }] }))
  })
}).listen(port, '127.0.0.1')
