'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Plus, Search } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { QueryState } from '@/components/ui/query-state'
import { AnswerMentorInviteDocument, CreateGroupDocument, DiscoverGroupsDocument, MyGroupsDocument, MyMentorInvitesDocument } from '@/graphql/generated/graphql'
import { attempt, GroupCardView } from './shared'

/** /groups (lvn-backend ADR-0045): your groups, public groups to find, and starting one. */
export function GroupsHome() {
  const t = useTranslations('groups')
  const mine = useQuery(MyGroupsDocument, { fetchPolicy: 'cache-and-network' })
  const [query, setQuery] = useState('')
  const [settled, setSettled] = useState('')
  useEffect(() => {
    const timer = setTimeout(() => setSettled(query.trim()), 250)
    return () => clearTimeout(timer)
  }, [query])
  const found = useQuery(DiscoverGroupsDocument, { variables: { query: settled || null }, fetchPolicy: 'cache-and-network' })
  const [creating, setCreating] = useState(false)
  const myIds = new Set(mine.data?.myGroups.map((g) => g.id))
  const discover = (found.data?.discoverGroups ?? []).filter((g) => !myIds.has(g.id))

  return (
    <div className="mx-auto flex max-w-4xl flex-col gap-8">
      <header className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-semibold">{t('title')}</h1>
        <Button className="gap-1.5" onClick={() => setCreating(true)}>
          <Plus className="size-4" aria-hidden />
          {t('new')}
        </Button>
      </header>
      <MentorInvites onAnswered={() => void mine.refetch()} />
      <section aria-labelledby="my-groups" className="flex flex-col gap-3">
        <h2 id="my-groups" className="text-sm font-semibold text-muted">
          {t('mine')}
        </h2>
        {mine.data?.myGroups.length ? (
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {mine.data.myGroups.map((g) => (
              <li key={g.id}>
                <GroupCardView group={g} />
              </li>
            ))}
          </ul>
        ) : mine.data ? (
          <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noneYet')}</p>
        ) : (
          <QueryState loading={mine.loading} error={mine.error} onRetry={mine.refetch} />
        )}
      </section>
      <section aria-labelledby="find-groups" className="flex flex-col gap-3">
        <h2 id="find-groups" className="text-sm font-semibold text-muted">
          {t('find')}
        </h2>
        <label className="flex items-center gap-2 rounded-xl border border-border bg-surface px-3">
          <Search className="size-4 text-muted" aria-hidden />
          <span className="sr-only">{t('searchLabel')}</span>
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={t('searchPlaceholder')} className="h-11 flex-1 bg-transparent focus:outline-none" />
        </label>
        {discover.length ? (
          <ul className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {discover.map((g) => (
              <li key={g.id}>
                <GroupCardView group={g} />
              </li>
            ))}
          </ul>
        ) : found.data ? (
          <p className="text-sm text-muted">{t('nothingFound')}</p>
        ) : (
          <QueryState loading={found.loading} error={found.error} onRetry={found.refetch} />
        )}
      </section>
      <CreateGroupDialog open={creating} onClose={() => setCreating(false)} />
    </div>
  )
}

function CreateGroupDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const t = useTranslations('groups')
  const router = useRouter()
  const [create, creating] = useMutation(CreateGroupDocument)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [privacy, setPrivacy] = useState<'PUBLIC' | 'PRIVATE'>('PUBLIC')
  const [type, setType] = useState<'COMMUNITY' | 'PROJECT'>('COMMUNITY')
  const [open_, setOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const submit = async () => {
    let id: string | undefined
    const problem = await attempt(async () => {
      const res = await create({ variables: { input: { name, description: description || null, privacy, joinPolicy: privacy === 'PUBLIC' && open_ ? 'OPEN' : 'APPROVAL', type } } })
      id = res.data?.createGroup.group?.id
      return res
    }, t('failed'))
    if (problem) return setError(problem)
    if (id) router.push(`/groups/${id}`)
  }
  return (
    <Dialog open={open} onClose={onClose} title={t('new')}>
      <form
        className="flex flex-col gap-4"
        onSubmit={(e) => {
          e.preventDefault()
          void submit()
        }}
      >
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-semibold">{t('name')}</span>
          <input value={name} maxLength={80} required onChange={(e) => setName(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
        </label>
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-semibold">{t('description')}</span>
          <textarea value={description} maxLength={2000} rows={3} onChange={(e) => setDescription(e.target.value)} className="rounded-xl border border-border bg-surface px-3 py-2" />
        </label>
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-sm font-semibold">{t('kind')}</legend>
          {(['COMMUNITY', 'PROJECT'] as const).map((k) => (
            <label key={k} className="flex items-start gap-2 text-sm">
              <input type="radio" name="type" checked={type === k} onChange={() => setType(k)} className="mt-1" />
              <span>
                <span className="font-medium">{t(`type.${k}`)}</span>
                <span className="block text-xs text-muted">{t(`typeHint.${k}`)}</span>
              </span>
            </label>
          ))}
        </fieldset>
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-sm font-semibold">{t('who')}</legend>
          {(['PUBLIC', 'PRIVATE'] as const).map((p) => (
            <label key={p} className="flex items-start gap-2 text-sm">
              <input type="radio" name="privacy" checked={privacy === p} onChange={() => setPrivacy(p)} className="mt-1" />
              <span>
                <span className="font-medium">{t(`privacy.${p}`)}</span>
                <span className="block text-xs text-muted">{t(`privacyHint.${p}`)}</span>
              </span>
            </label>
          ))}
        </fieldset>
        {privacy === 'PUBLIC' ? (
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={open_} onChange={(e) => setOpen(e.target.checked)} />
            {t('openJoin')}
          </label>
        ) : null}
        {error ? (
          <p role="alert" className="text-sm text-bad">
            {error}
          </p>
        ) : null}
        <div className="flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            {t('cancel')}
          </Button>
          <Button type="submit" disabled={creating.loading}>
            {t('create')}
          </Button>
        </div>
      </form>
    </Dialog>
  )
}

/** Teachers asked to mentor a project workspace (lvn-backend ADR-0048). */
function MentorInvites({ onAnswered }: { onAnswered: () => void }) {
  const t = useTranslations('groups')
  const { data, refetch } = useQuery(MyMentorInvitesDocument, { fetchPolicy: 'cache-and-network' })
  const [answer] = useMutation(AnswerMentorInviteDocument)
  const invites = data?.myMentorInvites ?? []
  if (!invites.length) return null
  const reply = async (inviteId: string, accept: boolean) => {
    await attempt(() => answer({ variables: { inviteId, accept } }), t('failed'))
    await refetch()
    onAnswered()
  }
  return (
    <section aria-labelledby="mentor-invites" className="flex flex-col gap-3">
      <h2 id="mentor-invites" className="text-sm font-semibold text-muted">
        {t('mentorInvites')}
      </h2>
      <ul className="flex flex-col gap-2">
        {invites.map((i) => (
          <li key={i.id} className="flex flex-wrap items-center gap-3 rounded-2xl border border-accent/40 bg-accent-soft/40 px-4 py-3">
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="font-semibold">{i.group.name}</span>
              <span className="text-sm text-muted">{t('mentorInvitedBy', { name: i.invitedBy.displayName })}</span>
            </span>
            <Button size="sm" onClick={() => void reply(i.id, true)}>
              {t('accept')}
            </Button>
            <Button variant="secondary" size="sm" onClick={() => void reply(i.id, false)}>
              {t('decline')}
            </Button>
          </li>
        ))}
      </ul>
    </section>
  )
}
