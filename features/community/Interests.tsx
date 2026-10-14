'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Plus, X } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { Input } from '@/components/ui/input'
import { FindTopicsDocument, MyInterestsDocument, SetInterestsDocument } from '@/graphql/generated/graphql'

/**
 * The topics a person chose (lvn-backend ADR-0076): Community's For You shows public notes on them, with those of their
 * exams and recent reading. Private: only they see what they chose. Each change is saved at once.
 */
export function Interests() {
  const t = useTranslations('community.interests')
  const { data } = useQuery(MyInterestsDocument, { fetchPolicy: 'cache-and-network' })
  // The profile comes back without the viewer around it: the list is asked for again.
  const [save, saving] = useMutation(SetInterestsDocument, { refetchQueries: [MyInterestsDocument], awaitRefetchQueries: true })
  const [query, setQuery] = useState('')
  const [settled, setSettled] = useState('')
  const [error, setError] = useState<string | null>(null)
  useEffect(() => {
    const timer = setTimeout(() => setSettled(query.trim()), 250)
    return () => clearTimeout(timer)
  }, [query])
  const found = useQuery(FindTopicsDocument, { variables: { query: settled }, skip: settled.length < 2 }).data?.findTopics ?? []
  const chosen = (data?.viewer?.profile?.interests ?? []).flatMap((x) => (x ? [x] : []))
  const ids = chosen.map((x) => x.id)
  const set = async (next: string[]) => {
    setError(null)
    const res = await save({ variables: { ids: next } }).catch(() => null)
    setError(res?.data?.updateProfile.userErrors[0]?.message ?? (res ? null : t('failed')))
  }
  return (
    <section id="interests" aria-labelledby="interests-title" className="flex scroll-mt-24 flex-col gap-3 rounded-2xl border border-border bg-surface p-5">
      <h2 id="interests-title" className="text-lg font-semibold">
        {t('title')}
      </h2>
      <p className="text-sm text-muted">{t('lead')}</p>
      {chosen.length ? (
        <ul aria-label={t('chosen')} className="flex flex-wrap gap-2">
          {chosen.map((topic) => (
            <li key={topic.id} className="inline-flex items-center gap-1 rounded-full bg-accent-soft py-1 pl-3 pr-1 text-sm text-accent">
              {topic.title}
              <button type="button" aria-label={t('remove', { topic: topic.title })} disabled={saving.loading} onClick={() => void set(ids.filter((id) => id !== topic.id))} className="rounded-full p-0.5 hover:bg-accent/15">
                <X className="size-3.5" aria-hidden />
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted">{t('none')}</p>
      )}
      <label className="flex flex-col gap-1 text-sm font-medium">
        {t('find')}
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t('placeholder')} />
      </label>
      {found.length ? (
        <ul aria-label={t('results')} className="flex flex-wrap gap-2">
          {found
            .filter((topic) => !ids.includes(topic.id))
            .slice(0, 12)
            .map((topic) => (
              <li key={topic.id}>
                <button type="button" disabled={saving.loading} onClick={() => void set([...ids, topic.id]).then(() => setQuery(''))} className="inline-flex items-center gap-1 rounded-full border border-border px-3 py-1 text-sm hover:border-accent hover:text-accent">
                  <Plus className="size-3.5" aria-hidden />
                  {topic.title}
                  <span className="text-xs text-muted">· {topic.subject.title}</span>
                </button>
              </li>
            ))}
        </ul>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
    </section>
  )
}
