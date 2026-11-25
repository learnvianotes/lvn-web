'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { ArrowLeft, GraduationCap } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { attempt, textToDoc } from '@/features/groups/shared'
import { ago } from '@/features/notes/look'
import { ContentModeration } from '@/features/moderation/ModerationBanner'
import { ReportButton } from '@/features/moderation/ReportDialog'
import { RichDoc } from '@/features/notes/render/RichText'
import { AnswerDoubtDocument, DeleteDoubtDocument, DoubtDocument, ReopenDoubtDocument, ResolveDoubtDocument } from '@/graphql/generated/graphql'
import type { Doc } from '@/lib/contracts/validation'
import { isNotThere } from '@/lib/query'
import { StatusChip } from './Doubts'
import { AnswerList, AskForm } from '@/features/ai/AskAi'

/** One doubt (lvn-backend ADR-0048): the question, its answers (the mentor's marked), answering, resolving, reopening. */
export function DoubtPage({ groupId, id }: { groupId: string; id: string }) {
  const t = useTranslations('workspaces')
  const tAi = useTranslations('ai.ask')
  const router = useRouter()
  const { data, loading, error: queryError, refetch } = useQuery(DoubtDocument, { variables: { id }, fetchPolicy: 'cache-and-network' })
  const [answer, answering] = useMutation(AnswerDoubtDocument)
  const [resolve] = useMutation(ResolveDoubtDocument)
  const [reopen] = useMutation(ReopenDoubtDocument)
  const [remove] = useMutation(DeleteDoubtDocument)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const d = data?.doubt
  if (!d) {
    if (loading) return <Loading label={t('loading')} />
    // Gone only when the API said so; a doubt that could not be asked for is offered again.
    return queryError && !isNotThere(queryError) ? <LoadFailed onRetry={refetch} /> : <p className="text-muted">{t('doubtGone')}</p>
  }
  const run = async (fn: () => Promise<{ data?: Record<string, { userErrors: { message: string }[] } | null> | null }>) => {
    setError(await attempt(fn, t('failed')))
    void refetch()
  }
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-5">
      <Link href={`/groups/${groupId}`} className="inline-flex w-fit items-center gap-1.5 text-sm text-muted hover:text-fg">
        <ArrowLeft className="size-4" aria-hidden />
        {t('backToWorkspace')}
      </Link>
      <article className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-6">
        <div className="flex flex-wrap items-center gap-2">
          <StatusChip status={d.status} />
          <span className="text-sm text-muted">
            {d.author.displayName} · {ago(d.createdAt)}
          </span>
        </div>
        <ContentModeration entityType="DOUBT" item={d} onAppealed={() => void refetch()} />
        <h1 className="text-2xl font-semibold">{d.title}</h1>
        {d.repoRef ? <code className="w-fit rounded bg-surface-2 px-2 py-1 text-sm">{d.repoRef}</code> : null}
        <RichDoc doc={d.body as Doc} className="text-sm" />
        <div className="flex flex-wrap gap-2">
          {d.viewerCan.resolve ? (
            <Button size="sm" onClick={() => void run(() => resolve({ variables: { doubtId: id } }))}>
              {t('resolve')}
            </Button>
          ) : null}
          {d.viewerCan.reopen ? (
            <Button variant="secondary" size="sm" onClick={() => void run(() => reopen({ variables: { doubtId: id } }))}>
              {t('reopen')}
            </Button>
          ) : null}
          <ReportButton entityType="DOUBT" entityId={d.id} authorId={d.author.id} className="order-last ml-auto" />
          {d.viewerCan.delete ? (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                if (window.confirm(t('deleteDoubtConfirm'))) void attempt(() => remove({ variables: { doubtId: id } }), t('failed')).then(() => router.push(`/groups/${groupId}`))
              }}
            >
              {t('delete')}
            </Button>
          ) : null}
        </div>
      </article>
      {/* Ask AI on a doubt (lvn-backend ADR-0015, ADR-0060): over the notes shared with the workspace; the answer is the asker's. */}
      <section aria-label={tAi('aboutDoubtTitle')} className="flex flex-col gap-3 rounded-2xl border border-dashed border-accent/40 p-4">
        <p className="text-sm text-muted">{tAi('aboutDoubtLead')}</p>
        <AskForm scope="WORKSPACE" doubtId={id} />
        <AnswerList doubtId={id} compact />
      </section>
      <section aria-label={t('answersTitle')} className="flex flex-col gap-3">
        <h2 className="text-lg font-semibold">{t('answers', { count: d.answers.length })}</h2>
        {d.answers.map((a) => (
          <article key={a.id} className={`flex flex-col gap-1.5 rounded-2xl border bg-surface px-4 py-3 ${a.byMentor ? 'border-accent/50' : 'border-border'}`}>
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <Link href={`/u/${a.author.handle}`} className="font-semibold hover:text-accent">
                {a.author.displayName}
              </Link>
              {a.byMentor ? (
                <span className="inline-flex items-center gap-1 rounded-[4px] bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">
                  <GraduationCap className="size-3" aria-hidden />
                  {t('mentor')}
                </span>
              ) : null}
              <span className="text-xs text-muted">{ago(a.createdAt)}</span>
            </div>
            <RichDoc doc={a.body as Doc} className="text-sm" />
          </article>
        ))}
        {d.viewerCan.answer ? (
          <form
            className="flex flex-col gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              void run(async () => {
                const res = await answer({ variables: { doubtId: id, body: textToDoc(text) } })
                if (res.data?.answerDoubt.doubt) setText('')
                return res
              })
            }}
          >
            <label className="sr-only" htmlFor="answer">
              {t('answerLabel')}
            </label>
            <textarea id="answer" value={text} rows={3} onChange={(e) => setText(e.target.value)} placeholder={t('answerPlaceholder')} className="rounded-xl border border-border bg-bg px-3 py-2 text-sm" />
            <Button type="submit" size="sm" className="self-end" disabled={answering.loading || !text.trim()}>
              {t('answerSend')}
            </Button>
          </form>
        ) : d.status === 'RESOLVED' ? (
          <p className="text-sm text-muted">{t('resolvedHint')}</p>
        ) : null}
        {error ? (
          <p role="alert" className="text-sm text-bad">
            {error}
          </p>
        ) : null}
      </section>
    </div>
  )
}
