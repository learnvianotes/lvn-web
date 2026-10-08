import type { Page, Route } from '@playwright/test'

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
  forkingEnabled: true,
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
    if (op === 'Viewer') return route.fulfill({ json: { data: { viewer: { __typename: 'User', id: USER, handle: 'asharao', displayName: 'Asha Rao', email: 'asha@example.com', emailVerified: true, registrationComplete: true, verified: true, verificationMethod: 'INSTITUTIONAL_EMAIL', globalRole: 'STUDENT', restrictedMinor: false, institutionalEmail: null, institutionalEmailStatus: 'NONE', institution: null, ...viewer } } } })
    if (op === 'TermsStatus' && !handlers[op]) return route.fulfill({ json: { data: { termsVersion: '2026-10-08', viewer: { __typename: 'User', id: USER, termsAccepted: true } } } })
    const handler = handlers[op]
    if (!handler) return route.fulfill({ status: 500, json: { errors: [{ message: `unmocked ${op}` }] } })
    return route.fulfill({ json: { data: handler(body.variables ?? {}) } })
  })
  return calls
}

