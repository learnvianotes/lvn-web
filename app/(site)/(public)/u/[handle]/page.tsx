import type { Metadata } from 'next'
import { notFound, permanentRedirect } from 'next/navigation'
import { env } from '@/lib/env'
import { getProfile } from '@/features/people/data'
import { ProfileView } from '@/features/people/ProfileView'
import { templated } from '@/lib/page-title'

/**
 * A person's profile (lvn-backend ADR-0043): rendered on the server from what they made public, cached a few minutes;
 * the viewer's own buttons load in the browser. Teachers' profiles are indexed (ADR-0014), students' are not.
 */
export const revalidate = 300

type Props = { params: Promise<{ handle: string }> }

const handleOf = async (params: Props['params']) => decodeURIComponent((await params).handle)

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const person = await getProfile(await handleOf(params))
  if (!person) return { title: 'Not found', robots: { index: false } }
  const url = `${env.NEXT_PUBLIC_SITE_URL}/u/${person.handle}`
  const teacher = person.globalRole === 'TEACHER'
  return {
    title: templated(`${person.displayName} (@${person.handle})`),
    description: teacher ? `Notes and writing by ${person.displayName}, a teacher on LearnViaNotes.` : `What ${person.displayName} shares on LearnViaNotes.`,
    alternates: { canonical: url },
    robots: { index: teacher, follow: teacher },
    openGraph: { type: 'profile', url, title: person.displayName, siteName: 'LearnViaNotes' },
  }
}

export default async function ProfilePage({ params }: Props) {
  const asked = await handleOf(params)
  const person = await getProfile(asked)
  if (!person) notFound()
  // One address per person: an id (from a notification) or another spelling moves to the handle.
  if (asked !== person.handle) permanentRedirect(`/u/${person.handle}`)
  return <ProfileView person={person} />
}
