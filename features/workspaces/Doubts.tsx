'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { CircleHelp, MessageSquare } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { attempt, textToDoc } from '@/features/groups/shared'
import { ago } from '@/features/notes/look'
import { AskDoubtDocument, WorkspaceDoubtsDocument, type DoubtStatus, type GroupDetailFragment } from '@/graphql/generated/graphql'

const FILTERS: (DoubtStatus | null)[] = [null, 'OPEN', 'ANSWERED', 'RESOLVED']

export function StatusChip({ status }: { status: DoubtStatus }) {
  const t = useTranslations('workspaces')
  const tone = status === 'RESOLVED' ? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/40 dark:text-emerald-100' : status === 'ANSWERED' ? 'bg-accent-soft text-accent' : 'bg-amber-100 text-amber-900 dark:bg-amber-950/40 dark:text-amber-100'
  return <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${tone}`}>{t(`status.${status}`)}</span>
}

/** Doubts for the mentor and team (lvn-backend ADR-0048): ask one, filter by status, open one to answer. */
export function Doubts({ group }: { group: GroupDetailFragment }) {
  const t = useTranslations('workspaces')
  const router = useRouter()
  const [status, setStatus] = useState<DoubtStatus | null>(null)
  const { data } = useQuery(WorkspaceDoubtsDocument, { variables: { id: group.id, status }, fetchPolicy: 'cache-and-network' })
  const [ask, asking] = useMutation(AskDoubtDocument)
  const [open, setOpen] = useState(false)
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [repoRef, setRepoRef] = useState('')
  const [error, setError] = useState<string | null>(null)
  const doubts = data?.group?.doubts?.edges.map((e) => e.node) ?? []
  const submit = async () => {
    let id: string | undefined
    const problem = await attempt(async () => {
      const res = await ask({ variables: { input: { groupId: group.id, title, body: textToDoc(body), repoRef: repoRef.trim() || null } } })
      id = res.data?.askDoubt.doubt?.id
      return res
    }, t('failed'))
    if (problem) return setError(problem)
    if (id) router.push(`/groups/${group.id}/doubts/${id}`)
  }
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <div role="group" aria-label={t('filter')} className="flex flex-wrap gap-1">
          {FILTERS.map((f) => (
            <button key={f ?? 'ALL'} type="button" aria-pressed={status === f} onClick={() => setStatus(f)} className={`rounded-full px-3 py-1 text-xs font-semibold ${status === f ? 'bg-accent text-white' : 'border border-border text-muted hover:text-fg'}`}>
              {f ? t(`status.${f}`) : t('all')}
            </button>
          ))}
        </div>
        {group.viewerCan.askDoubt && !open ? (
          <Button size="sm" className="ml-auto gap-1.5" onClick={() => setOpen(true)}>
            <CircleHelp className="size-4" aria-hidden />
            {t('ask')}
          </Button>
        ) : null}
      </div>
      {open ? (
        <form
          className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4"
          onSubmit={(e) => {
            e.preventDefault()
            void submit()
          }}
        >
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold">{t('doubtTitle')}</span>
            <input value={title} maxLength={200} required onChange={(e) => setTitle(e.target.value)} className="h-10 rounded-xl border border-border bg-bg px-3 text-sm" />
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold">{t('doubtBody')}</span>
            <textarea value={body} rows={4} onChange={(e) => setBody(e.target.value)} className="rounded-xl border border-border bg-bg px-3 py-2 text-sm" />
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold">{t('repoRef')}</span>
            <input value={repoRef} maxLength={300} onChange={(e) => setRepoRef(e.target.value)} placeholder="src/heap.ts:42" className="h-10 rounded-xl border border-border bg-bg px-3 font-mono text-sm" />
          </label>
          {error ? (
            <p role="alert" className="text-sm text-red-600 dark:text-red-400">
              {error}
            </p>
          ) : null}
          <div className="flex justify-end gap-2">
            <Button type="button" variant="secondary" size="sm" onClick={() => setOpen(false)}>
              {t('cancel')}
            </Button>
            <Button type="submit" size="sm" disabled={asking.loading || !title.trim() || !body.trim()}>
              {t('askSend')}
            </Button>
          </div>
        </form>
      ) : null}
      {doubts.length ? (
        <ul className="flex flex-col gap-2">
          {doubts.map((d) => (
            <li key={d.id}>
              <Link href={`/groups/${group.id}/doubts/${d.id}`} className="flex flex-col gap-1 rounded-2xl border border-border bg-surface px-4 py-3 hover:border-accent/50">
                <span className="flex flex-wrap items-center gap-2">
                  <span className="font-semibold">{d.title}</span>
                  <StatusChip status={d.status} />
                </span>
                <span className="flex flex-wrap items-center gap-2 text-xs text-muted">
                  {d.author.displayName} · {ago(d.createdAt)}
                  <span className="inline-flex items-center gap-1">
                    <MessageSquare className="size-3" aria-hidden />
                    {t('answers', { count: d.answerCount })}
                  </span>
                  {d.repoRef ? <code className="rounded bg-surface-2 px-1.5">{d.repoRef}</code> : null}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : data ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noDoubts')}</p>
      ) : null}
    </div>
  )
}
