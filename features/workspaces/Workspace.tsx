'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Award } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { QueryState } from '@/components/ui/query-state'
import { attempt } from '@/features/groups/shared'
import { AnswerMentorInviteDocument, GroupNotesDocument, InviteMentorDocument, SetProjectShowcaseDocument, WorkspaceDocument, type GroupDetailFragment } from '@/graphql/generated/graphql'
import { RepositoryCard } from './Repository'

/** A workspace's header parts (lvn-backend ADR-0048): a mentor invite to answer, the repository card, the showcase. */
export function WorkspaceHeader({ group, onChanged }: { group: GroupDetailFragment; onChanged: () => void }) {
  const t = useTranslations('workspaces')
  const { data, loading, error: queryError, refetch } = useQuery(WorkspaceDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const [answer] = useMutation(AnswerMentorInviteDocument)
  const [error, setError] = useState<string | null>(null)
  const reply = async (accept: boolean) => {
    setError(await attempt(() => answer({ variables: { inviteId: group.viewerMentorInviteId!, accept } }), t('failed')))
    onChanged()
  }
  const showcase = data?.group?.showcase
  return (
    <div className="flex flex-col gap-3">
      {group.viewerMentorInviteId ? (
        <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-accent/40 bg-accent-soft/40 px-4 py-3">
          <span className="flex-1 text-sm">{t('mentorInvited')}</span>
          <Button size="sm" onClick={() => void reply(true)}>
            {t('accept')}
          </Button>
          <Button variant="secondary" size="sm" onClick={() => void reply(false)}>
            {t('decline')}
          </Button>
        </div>
      ) : null}
      {data?.group ? <RepositoryCard groupId={group.id} repository={data.group.repository} canManage={group.viewerCan.manage} onChanged={() => void refetch()} /> : !data ? <QueryState loading={loading} error={queryError} onRetry={refetch} /> : null}
      {showcase ? (
        <Link href={`/notes/${showcase.id}`} className="inline-flex w-fit items-center gap-1.5 text-sm font-semibold text-accent hover:underline">
          <Award className="size-4" aria-hidden />
          {t('showcaseLink', { title: showcase.title || t('untitled') })}
        </Link>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </div>
  )
}

/** Admins invite a teacher to mentor the workspace (14 days to accept). */
export function InviteMentor({ groupId }: { groupId: string }) {
  const t = useTranslations('workspaces')
  const [invite, inviting] = useMutation(InviteMentorDocument)
  const [person, setPerson] = useState('')
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  return (
    <form
      className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-3"
      onSubmit={(e) => {
        e.preventDefault()
        void attempt(() => invite({ variables: { groupId, person: person.trim() } }), t('failed')).then((problem) => {
          setMessage(problem ? { ok: false, text: problem } : { ok: true, text: t('mentorInviteSent') })
          if (!problem) setPerson('')
        })
      }}
    >
      <span className="text-sm font-semibold">{t('inviteMentor')}</span>
      <div className="flex flex-wrap gap-2">
        <label className="min-w-0 flex-1">
          <span className="sr-only">{t('mentorLabel')}</span>
          <input value={person} onChange={(e) => setPerson(e.target.value)} placeholder={t('mentorLabel')} autoComplete="off" className="h-10 w-full rounded-xl border border-border bg-bg px-3 text-sm" />
        </label>
        <Button type="submit" size="sm" className="h-10" disabled={inviting.loading || !person.trim()}>
          {t('invite')}
        </Button>
      </div>
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-bad'}>
          {message.text}
        </p>
      ) : null}
    </form>
  )
}

/** Admins choose the showcase: a PUBLIC project note shared to the workspace, which credits the team. */
export function ShowcaseSetting({ group }: { group: GroupDetailFragment }) {
  const t = useTranslations('workspaces')
  const notes = useQuery(GroupNotesDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const current = useQuery(WorkspaceDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const [save, saving] = useMutation(SetProjectShowcaseDocument)
  const [chosen, setChosen] = useState<string | null>(null)
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  const choices = (notes.data?.group?.sharedNotes?.edges.map((e) => e.node) ?? []).filter((n) => n.kind === 'PROJECT' && n.visibility === 'PUBLIC')
  const value = chosen ?? current.data?.group?.showcase?.id ?? ''
  return (
    <form
      className="flex flex-col gap-3"
      onSubmit={(e) => {
        e.preventDefault()
        void attempt(() => save({ variables: { groupId: group.id, noteId: value || null } }), t('failed')).then((problem) => {
          setMessage(problem ? { ok: false, text: problem } : { ok: true, text: t('saved') })
          void current.refetch()
        })
      }}
    >
      <h3 className="font-semibold">{t('showcase')}</h3>
      <p className="text-sm text-muted">{t('showcaseHint')}</p>
      <label className="flex flex-col gap-1.5">
        <span className="sr-only">{t('showcase')}</span>
        <select value={value} onChange={(e) => setChosen(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3 text-sm">
          <option value="">{t('noShowcase')}</option>
          {choices.map((n) => (
            <option key={n.id} value={n.id}>
              {n.title || t('untitled')}
            </option>
          ))}
        </select>
      </label>
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-bad'}>
          {message.text}
        </p>
      ) : null}
      <Button type="submit" className="w-fit" disabled={saving.loading}>
        {t('saveShowcase')}
      </Button>
    </form>
  )
}
