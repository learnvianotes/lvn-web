import 'server-only'
import { cache } from 'react'
import { PAGE_REVALIDATE_SECONDS } from '@/features/public-notes/data'
import { serverEnv } from '@/lib/server-env'

/** LearnViaNotes' own subjects and topics (curated, lvn-backend ADR-0012 catalogue): titles, never the old /core pages. */
export interface SubjectSummary {
  id: string
  slug: string
  title: string
  topics: TopicNode[]
}
export interface TopicNode {
  id: string
  slug: string
  title: string
  children: { id: string; slug: string; title: string }[]
}
export interface TopicNote {
  id: string
  title: string
  slug: string
  kind: string
  publishedAt: string | null
  owner: { displayName: string }
}
export interface TopicResource {
  id: string
  type: string
  title: string
  host: string
  author: string | null
}

async function query<T>(source: string, variables: Record<string, unknown>): Promise<T> {
  const res = await fetch(serverEnv.apiUrl, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: source, variables }),
    next: { revalidate: PAGE_REVALIDATE_SECONDS, tags: ['subjects'] },
    signal: AbortSignal.timeout(5_000),
  })
  if (!res.ok) throw new Error(`API answered HTTP ${res.status}`)
  const body = (await res.json()) as { data?: T; errors?: { message: string }[] }
  if (body.errors?.length || !body.data) throw new Error(`API error: ${body.errors?.[0]?.message ?? 'no data'}`)
  return body.data
}

const TOPICS = 'topics { id slug title children { id slug title } }'

/** Every subject with its topics, in the catalogue's order; empty when the API cannot answer. */
export const listSubjects = cache(async (): Promise<SubjectSummary[]> => (await query<{ subjects: SubjectSummary[] }>(`query Subjects { subjects { id slug title ${TOPICS} } }`, {})).subjects)

/** A subject, or why it is not on the page: missing is a real 404; down is an API failure. */
export async function loadSubject(slug: string): Promise<{ status: 'ok'; subject: SubjectSummary } | { status: 'missing' } | { status: 'down' }> {
  try {
    const subject = await getSubject(slug)
    return subject ? { status: 'ok', subject } : { status: 'missing' }
  } catch {
    return { status: 'down' }
  }
}

export const getSubject = cache(
  async (slug: string): Promise<SubjectSummary | null> => (await query<{ subject: SubjectSummary | null }>(`query Subject($slug: String!) { subject(slug: $slug) { id slug title ${TOPICS} } }`, { slug })).subject,
)

/** Public notes and approved resources on a subject or one of its topics, newest first. */
export const getShelf = cache(async (on: { subjectId?: string; topicId?: string }): Promise<{ notes: TopicNote[]; resources: TopicResource[] }> => {
  const data = await query<{ search: { notes: { note: TopicNote }[] } }>(
    `query SubjectShelf($filters: SearchFilters, $scopes: [SearchScope!]) { search(query: "", scopes: $scopes, filters: $filters, first: 20) { notes { note { id title slug kind publishedAt owner { displayName } } } } }`,
    { filters: on, scopes: ['NOTES'] },
  )
  const resources = on.topicId
    ? ((
        await query<{ resources: { edges: { node: TopicResource }[] } }>(`query TopicResources($topicId: UUID!) { resources(filter: { topicId: $topicId }, first: 10) { edges { node { id type title host author } } } }`, {
          topicId: on.topicId,
        }).catch(() => null)
      )?.resources.edges.map((e) => e.node) ?? [])
    : []
  return { notes: data.search.notes.map((h) => h.note), resources }
})
