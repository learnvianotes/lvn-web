'use client'

import { useQuery } from '@apollo/client/react'
import { Users } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { NoteContributorsDocument } from '@/graphql/generated/graphql'

export type Credit = { role: 'CONTRIBUTOR' | 'MENTOR'; user: { id: string; displayName: string; handle: string } }

/** Who a project workspace's showcase credits (lvn-backend ADR-0048): the team, then the mentors. */
export function CreditsLine({ credits }: { credits: Credit[] }) {
  const t = useTranslations('workspaces')
  if (!credits.length) return null
  const names = (role: Credit['role']) =>
    credits
      .filter((c) => c.role === role)
      .map((c, i, all) => (
        <span key={c.user.id}>
          <Link href={`/u/${c.user.handle}`} className="font-semibold hover:text-accent">
            {c.user.displayName}
          </Link>
          {i < all.length - 1 ? ', ' : ''}
        </span>
      ))
  const mentors = credits.filter((c) => c.role === 'MENTOR')
  return (
    <p className="inline-flex flex-wrap items-center gap-1 text-sm text-muted">
      <Users className="size-4" aria-hidden />
      {t('builtBy')} {names('CONTRIBUTOR')}
      {mentors.length ? (
        <>
          {' '}
          <span aria-hidden>·</span> {t('mentoredBy')} {names('MENTOR')}
        </>
      ) : null}
    </p>
  )
}

/** The credits of a note, read on their own (signed-in pages). */
export function NoteCredits({ noteId }: { noteId: string }) {
  const { data } = useQuery(NoteContributorsDocument, { variables: { id: noteId }, fetchPolicy: 'cache-and-network' })
  return <CreditsLine credits={(data?.note?.contributors ?? []) as Credit[]} />
}
