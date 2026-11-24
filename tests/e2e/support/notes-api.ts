import type { Page, Route, WebSocketRoute } from '@playwright/test'
import { LIVE_URL } from './constants'

/** The mocked API of the notes app's Playwright tests: a signed-in session and GraphQL answered by operation name. */

export const NOTE_ID = '01920000-0000-7000-8000-00000000a001'
export const CARD_A = '01920000-0000-7000-8000-00000000c001'
export const CARD_B = '01920000-0000-7000-8000-00000000c002'
export const USER = '01920000-0000-7000-8000-00000000aaaa'

export const p = (text: string) => ({ type: 'paragraph', content: [{ type: 'text', text }] })
export const cards = [
  { __typename: 'Card', id: CARD_A, type: 'heading', position: 'a0', revision: 3, content: { level: 1, content: [{ type: 'text', text: 'Binary search' }] } },
  { __typename: 'Card', id: CARD_B, type: 'text', position: 'a1', revision: 5, content: { doc: { type: 'doc', content: [p('Halve the range each step.')] } } },
]
export const meta = (over: Record<string, unknown> = {}) => ({
  __typename: 'Note',
  id: NOTE_ID,
  title: 'Searching',
  slug: 'searching',
  kind: 'NOTE',
  visibility: 'PRIVATE',
  viewerAccess: 'OWNER',
  viewerCan: { __typename: 'NotePermissions', edit: true, publish: true, changeVisibility: true, delete: true, share: true, fork: true },
  owner: { __typename: 'User', id: USER, displayName: 'Asha Rao', handle: 'asharao' },
  folder: null,
  tags: [],
  topics: [],
  draftRevision: 8,
  draftUpdatedAt: new Date().toISOString(),
  publishedAt: null,
  publishedVersion: null,
  allowForks: true,
  forkCount: 0,
  moderation: null,
  forkedFrom: null,
  cardCount: 2,
  deletedAt: null,
  ...over,
})
export const page1 = (list: unknown[]) => ({ edges: list.map((node) => ({ __typename: 'CardEdge', node })), pageInfo: { __typename: 'PageInfo', hasNextPage: false, endCursor: null } })

export type Handler = (variables: Record<string, unknown>) => unknown

/** A signed-in session (refresh answered) and GraphQL by operation name; calls are recorded. `viewer` overrides the viewer. */
export async function mockApi(page: Page, handlers: Record<string, Handler>, viewer: Record<string, unknown> = {}) {
  const calls: { op: string; variables: Record<string, unknown> }[] = []
  await page.route('**/graphql', async (route: Route) => {
    const body = route.request().postDataJSON() as { query: string; operationName?: string; variables?: Record<string, unknown> }
    const op = body.operationName ?? (body.query.includes('refreshSession') ? 'Refresh' : 'unknown')
    calls.push({ op, variables: body.variables ?? {} })
    if (op === 'Refresh') {
      return route.fulfill({ json: { data: { refreshSession: { session: { accessToken: 'h.p.s', accessTokenExpiresAt: new Date(Date.now() + 900_000).toISOString() } } } } })
    }
    if (op === 'Viewer') return route.fulfill({ json: { data: { viewer: { __typename: 'User', id: USER, handle: 'asharao', displayName: 'Asha Rao', email: 'asha@example.com', emailVerified: true, registrationComplete: true, verified: true, verificationMethod: 'INSTITUTIONAL_EMAIL', globalRole: 'STUDENT', teacherStatus: 'NONE', restrictedMinor: false, institutionalEmail: null, institutionalEmailStatus: 'NONE', institution: null, deletionScheduledFor: null, ...viewer } } } })
    // The header's bell asks on every signed-in page (lvn-backend ADR-0042).
    if (op === 'UnreadNotificationCount' && !handlers[op]) return route.fulfill({ json: { data: { unreadNotificationCount: 0 } } })
    // The account page asks for the viewer's standing (lvn-backend ADR-0053): nothing to tell unless a test says so.
    if (op === 'MyStanding' && !handlers[op]) return route.fulfill({ json: { data: { myStanding: { __typename: 'AccountStanding', suspendedUntil: null, suspensionReason: null, canAppeal: false, warnings: [] } } } })
    // Every signed-in page tells the API the browser's time zone once (lvn-backend ADR-0070).
    if (op === 'SetLearningTimeZone' && !handlers[op]) return route.fulfill({ json: { data: { setLearningTimeZone: { __typename: 'OkPayload', ok: true, userErrors: [] } } } })
    // Uploads are on in development and in these tests unless a test says otherwise (lvn-backend ADR-0097).
    if (op === 'UploadsEnabled' && !handlers[op]) return route.fulfill({ json: { data: { uploadsEnabled: true } } })
    // College ID checks are off unless a test turns them on (lvn-backend ADR-0099), so the option stays hidden.
    if (op === 'StudentIdVerificationEnabled' && !handlers[op]) return route.fulfill({ json: { data: { studentIdVerificationEnabled: false } } })
    // First-party usage and the profile opt-out. Tests that do not care about them still answer.
    if (op === 'AnalyticsOptOut' && !handlers[op]) return route.fulfill({ json: { data: { viewer: { __typename: 'User', id: USER, analyticsOptOut: false } } } })
    if (op === 'IngestAnalytics' && !handlers[op]) return route.fulfill({ json: { data: { ingestAnalytics: { __typename: 'OkPayload', ok: true, userErrors: [] } } } })
    if (op === 'TermsStatus' && !handlers[op]) return route.fulfill({ json: { data: { termsVersion: '2026-10-08', viewer: { __typename: 'User', id: USER, termsAccepted: true } } } })
    // Public list of actions closed until the sign-in email is confirmed. The backend default, unless a test names some.
    if (op === 'UnverifiedGatedActions' && !handlers[op]) return route.fulfill({ json: { data: { unverifiedGatedActions: ['note.publish', 'note.share', 'contest.enter', 'payout.request', 'ai.bulk', 'resource.submit'] } } })
    // Admin pages ask whether this session still needs an emailed code (lvn-backend PR #92). Satisfied unless a test says otherwise.
    if (op === 'MfaStatus' && !handlers[op]) return route.fulfill({ json: { data: { mfaStatus: { __typename: 'MfaStatus', required: false, satisfied: true, verifiedAt: null, factors: [], allowedFactors: [] } } } })
    // Setting public_notes_require_verification. Off unless a test turns it on.
    if (op === 'PublicNotesRequireVerification' && !handlers[op]) return route.fulfill({ json: { data: { publicNotesRequireVerification: false } } })
    const handler = handlers[op]
    if (!handler) return route.fulfill({ status: 500, json: { errors: [{ message: `unmocked ${op}` }] } })
    return route.fulfill({ json: { data: handler(body.variables ?? {}) } })
  })
  return calls
}


/**
 * Live updates (lvn-backend ADR-0042) in place of the API's graphql-ws endpoint: acknowledges connections, records
 * their `connection_init` payloads and subscriptions, and sends events to every subscription on demand.
 */
export async function mockLive(page: Page) {
  const inits: Record<string, unknown>[] = []
  const subscriptions: { ws: WebSocketRoute; id: string }[] = []
  await page.routeWebSocket(LIVE_URL, (ws) => {
    ws.onMessage((raw) => {
      const msg = JSON.parse(String(raw)) as { type: string; id?: string; payload?: Record<string, unknown> }
      if (msg.type === 'connection_init') {
        inits.push(msg.payload ?? {})
        ws.send(JSON.stringify({ type: 'connection_ack' }))
      }
      if (msg.type === 'ping') ws.send(JSON.stringify({ type: 'pong' }))
      if (msg.type === 'subscribe' && msg.id) subscriptions.push({ ws, id: msg.id })
    })
  })
  return {
    inits,
    subscriptions,
    send(event: { kind: string; id: string }) {
      for (const s of subscriptions) s.ws.send(JSON.stringify({ id: s.id, type: 'next', payload: { data: { live: { ...event, at: new Date().toISOString() } } } }))
    },
  }
}
