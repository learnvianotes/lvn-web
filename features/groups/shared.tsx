'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { Globe, Lock, Users } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import type { GroupCardFragment } from '@/graphql/generated/graphql'
import type { Doc } from '@/lib/contracts/validation'

/** What went wrong, in the API's words: refusals arrive as errors, invalid input as userErrors (lvn-backend §6.2). */
export function problemOf(error: unknown, userErrors: { message: string }[] | undefined, fallback: string): string | null {
  if (CombinedGraphQLErrors.is(error)) return error.errors[0]?.message ?? fallback
  if (error) return fallback
  return userErrors?.[0]?.message ?? null
}

/** Runs one change; returns the problem to show, or null. */
export async function attempt<T extends Record<string, { userErrors: { message: string }[] } | null | undefined>>(run: () => Promise<{ data?: T | null }>, fallback: string): Promise<string | null> {
  try {
    const res = await run()
    const payload = Object.values(res.data ?? {})[0]
    return problemOf(null, payload?.userErrors, fallback)
  } catch (e) {
    return problemOf(e, undefined, fallback)
  }
}

/** Plain text, one paragraph per line, as the rich-text document a post holds. */
export function textToDoc(text: string): Doc {
  const paragraphs = text.split(/\n+/).map((l) => l.trim()).filter(Boolean)
  return { type: 'doc', content: paragraphs.map((p) => ({ type: 'paragraph', content: [{ type: 'text', text: p }] })) } as Doc
}

export function GroupCardView({ group }: { group: GroupCardFragment }) {
  const t = useTranslations('groups')
  const Icon = group.privacy === 'PRIVATE' ? Lock : Globe
  return (
    <Link href={`/groups/${group.id}`} className="flex h-full flex-col gap-2 rounded-2xl border border-border bg-surface p-4 transition-colors hover:border-accent/50 hover:shadow-md">
      <span className="flex items-center gap-2 font-semibold">
        <Icon className="size-4 shrink-0 text-accent" aria-label={t(`privacy.${group.privacy}`)} />
        <span className="truncate">{group.name}</span>
        {group.type === 'PROJECT' ? <span className="ml-auto shrink-0 rounded-full bg-surface-2 px-2 py-0.5 text-xs font-semibold text-muted">{t('project')}</span> : null}
      </span>
      {group.description ? <span className="line-clamp-2 text-sm text-muted">{group.description}</span> : null}
      <span className="mt-auto flex items-center gap-1.5 text-xs text-muted">
        <Users className="size-3.5" aria-hidden />
        {t('members', { count: group.memberCount })}
        {group.viewerRole ? <span className="ml-auto rounded-[4px] bg-accent-soft px-2 py-0.5 font-semibold text-accent">{t(`role.${group.viewerRole}`)}</span> : null}
      </span>
    </Link>
  )
}
