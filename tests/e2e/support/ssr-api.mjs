// A stand-in for lvn-backend that server rendering talks to in Playwright runs (API_INTERNAL_URL): public notes from
// public-notes.json, profiles from profiles.json (by handle, any case, or id), anything else unknown. The browser's own GraphQL calls are mocked per test with page.route.
import { readFileSync } from 'node:fs'
import { createServer } from 'node:http'

const { notes } = JSON.parse(readFileSync(new URL('./public-notes.json', import.meta.url), 'utf8'))
const { profiles } = JSON.parse(readFileSync(new URL('./profiles.json', import.meta.url), 'utf8'))
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
