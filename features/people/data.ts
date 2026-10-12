import 'server-only'
import { cache } from 'react'
import { serverEnv } from '@/lib/server-env'

/**
 * Profiles as anyone sees them (lvn-backend ADR-0043), read anonymously on the server and cached for a few minutes:
 * what a person made public, never anything about the viewer. Restricted minors have no profile (null).
 */

export const PROFILE_REVALIDATE_SECONDS = 300

export interface PublicProfile {
  id: string
  handle: string
  displayName: string
  globalRole: 'STUDENT' | 'TEACHER' | 'PLATFORM_ADMIN'
  verified: boolean
  createdAt: string
  followerMilestone: number | null
  profile: { department: string | null; yearOfStudy: string | null } | null
  notes: { id: string; title: string; slug: string; kind: 'NOTE' | 'BLOG' | 'POST' | 'PROJECT'; publishedAt: string | null }[]
  /** Teachers' Skills tab (ADR-0012); null for everyone else */
  teacherProfile: { headline: string | null; bio: string | null; skills: { id: string; kind: 'SKILL' | 'QUALIFICATION' | 'EXPERIENCE'; name: string; detail: string | null }[] } | null
}

const PROFILE = `query PublicProfile($handle: String!) {
  userByHandle(handle: $handle) {
    id handle displayName globalRole verified createdAt followerMilestone
    profile { department yearOfStudy }
    teacherProfile { headline bio skills { id kind name detail } }
    publicNotes(first: 60) { edges { node { id title slug kind publishedAt } } }
  }
}`

type Answer = { userByHandle: (Omit<PublicProfile, 'notes'> & { publicNotes: { edges: { node: PublicProfile['notes'][number] }[] } }) | null }

/** A profile by handle or id; null when there is none to show. */
export const getProfile = cache(async (handle: string): Promise<PublicProfile | null> => {
  const res = await fetch(serverEnv.apiUrl, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: PROFILE, variables: { handle } }),
    next: { revalidate: PROFILE_REVALIDATE_SECONDS, tags: [`profile:${handle.toLowerCase()}`] },
    signal: AbortSignal.timeout(5_000),
  })
  if (!res.ok) throw new Error(`API answered HTTP ${res.status}`)
  const body = (await res.json()) as { data?: Answer; errors?: { message: string }[] }
  if (body.errors?.length || !body.data) throw new Error(`API error: ${body.errors?.[0]?.message ?? 'no data'}`)
  const u = body.data.userByHandle
  if (!u) return null
  const { publicNotes, ...rest } = u
  return { ...rest, notes: publicNotes.edges.map((e) => e.node) }
})
