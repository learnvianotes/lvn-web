'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Lock, MessageSquare } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { attempt, textToDoc } from '@/features/groups/shared'
import { ago } from '@/features/notes/look'
import { RichDoc } from '@/features/notes/render/RichText'
import { ContentModeration } from '@/features/moderation/ModerationBanner'
import { ReportButton } from '@/features/moderation/ReportDialog'
import { AddCommentDocument, ApproveCommentDocument, DeleteCommentDocument, DiscussionDocument, EditCommentDocument, type CommentFieldsFragment, type CommentTargetType } from '@/graphql/generated/graphql'
import type { Doc } from '@/lib/contracts/validation'
import { ReactionBar } from './Reactions'

type Run = () => Promise<{ data?: Record<string, { userErrors: { message: string }[] } | null> | null }>

/** Plain text of a comment's document, for editing it again. */
const plain = (doc: unknown) => ((doc as Doc | null)?.content ?? []).map((p) => ((p as { content?: { text?: string }[] }).content ?? []).map((n) => n.text ?? '').join('')).join('\n')

/**
 * The discussion of a note, group post, class announcement or resource (lvn-backend ADR-0047, ADR-0075): reactions, comments with one
 * level of replies, and what the viewer may do with each. Read with its own query, so threads stay in the depth limit.
 */
export function Discussion({ target, title, compact }: { target: { type: CommentTargetType; id: string }; title?: string; compact?: boolean }) {
  const t = useTranslations('discussion')
  const { data, loading, error: queryError, refetch, fetchMore } = useQuery(DiscussionDocument, { variables: { target }, fetchPolicy: 'cache-and-network' })
  const [add, adding] = useMutation(AddCommentDocument)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const d = data?.discussion
  if (!d) return loading ? <Loading label={t('loading')} /> : queryError && !data ? <LoadFailed onRetry={refetch} /> : null
  const refresh = () => void refetch()
  const send = async () => {
    const problem = await attempt(() => add({ variables: { input: { target, body: textToDoc(text) } } }), t('failed'))
    setError(problem)
    if (!problem) setText('')
    refresh()
  }
  const comments = d.comments.edges.map((e) => e.node)
  // Resources are saved rather than liked (lvn-backend ADR-0075): their discussion has comments only.
  const reactionTarget = target.type === 'RESOURCE' ? null : { type: target.type, id: target.id }
  return (
    <section aria-label={title ?? t('title')} className={`flex flex-col gap-4 ${compact ? '' : 'rounded-3xl border border-border bg-surface p-5'}`}>
      {compact ? (
        reactionTarget ? <ReactionBar target={reactionTarget} reactions={d.reactions} disabled={!d.viewerCanComment} onChanged={refresh} size="sm" /> : null
      ) : (
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <MessageSquare className="size-5 text-accent" aria-hidden />
            {title ?? t('title')}
            <span className="text-sm font-normal text-muted">{t('count', { count: d.commentCount })}</span>
          </h2>
          {reactionTarget ? <ReactionBar target={reactionTarget} reactions={d.reactions} disabled={!d.viewerCanComment} onChanged={refresh} /> : null}
        </div>
      )}
      {comments.length ? (
        <ul className="flex flex-col gap-3">
          {comments.map((c) => (
            <li key={c.id} className="flex flex-col gap-2">
              <CommentView comment={c} onChanged={refresh} />
              {c.replies.length ? (
                <ul className="ml-5 flex flex-col gap-2 border-l-2 border-border pl-4">
                  {c.replies.map((r) => (
                    <li key={r.id}>
                      <CommentView comment={r} onChanged={refresh} />
                    </li>
                  ))}
                </ul>
              ) : null}
              {c.viewerCan.reply ? <ReplyBox target={target} parentId={c.id} onSent={refresh} /> : null}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted">{t('none')}</p>
      )}
      {d.comments.pageInfo.hasNextPage ? (
        <Button variant="secondary" size="sm" className="self-start" onClick={() =>
            void fetchMore({
              variables: { after: d.comments.pageInfo.endCursor },
              updateQuery: (prev, { fetchMoreResult }) =>
                prev.discussion && fetchMoreResult.discussion ? { discussion: { ...fetchMoreResult.discussion, comments: { ...fetchMoreResult.discussion.comments, edges: [...prev.discussion.comments.edges, ...fetchMoreResult.discussion.comments.edges] } } } : fetchMoreResult,
            })
          }>
          {t('more')}
        </Button>
      ) : null}
      {d.viewerCanComment ? (
        <form
          className="flex flex-col gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            void send()
          }}
        >
          <label className="sr-only" htmlFor={`comment-${target.id}`}>
            {t('write')}
          </label>
          <textarea id={`comment-${target.id}`} value={text} rows={2} maxLength={5000} onChange={(e) => setText(e.target.value)} placeholder={target.type === 'CLASSROOM_POST' ? t('askStaff') : t('placeholder')} aria-describedby={`mention-hint-${target.id}`} className="resize-y rounded-xl border border-border bg-bg px-3 py-2 text-sm" />
          <div className="flex items-center justify-between gap-2">
            <span id={`mention-hint-${target.id}`} className="text-xs text-muted">
              {t('mentionHint')}
            </span>
            <Button type="submit" size="sm" disabled={adding.loading || !text.trim()}>
              {t('send')}
            </Button>
          </div>
        </form>
      ) : d.whyNot ? (
        <p className="text-sm text-muted">{d.whyNot}</p>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </section>
  )
}

function ReplyBox({ target, parentId, onSent }: { target: { type: CommentTargetType; id: string }; parentId: string; onSent: () => void }) {
  const t = useTranslations('discussion')
  const [add] = useMutation(AddCommentDocument)
  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  if (!open) {
    return (
      <button type="button" onClick={() => setOpen(true)} className="ml-5 self-start text-xs font-semibold text-muted hover:text-accent">
        {t('reply')}
      </button>
    )
  }
  return (
    <form
      className="ml-5 flex flex-col gap-2"
      onSubmit={(e) => {
        e.preventDefault()
        void attempt(() => add({ variables: { input: { target, parentId, body: textToDoc(text) } } }), t('failed')).then((problem) => {
          setError(problem)
          if (!problem) {
            setText('')
            setOpen(false)
          }
          onSent()
        })
      }}
    >
      <label className="sr-only" htmlFor={`reply-${parentId}`}>
        {t('writeReply')}
      </label>
      <textarea id={`reply-${parentId}`} autoFocus value={text} rows={2} maxLength={5000} onChange={(e) => setText(e.target.value)} className="resize-y rounded-xl border border-border bg-bg px-3 py-2 text-sm" />
      <div className="flex gap-2 self-end">
        <Button type="button" variant="secondary" size="sm" onClick={() => setOpen(false)}>
          {t('cancel')}
        </Button>
        <Button type="submit" size="sm" disabled={!text.trim()}>
          {t('sendReply')}
        </Button>
      </div>
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </form>
  )
}

function CommentView({ comment: c, onChanged }: { comment: CommentFieldsFragment; onChanged: () => void }) {
  const t = useTranslations('discussion')
  const [edit] = useMutation(EditCommentDocument)
  const [remove] = useMutation(DeleteCommentDocument)
  const [approve] = useMutation(ApproveCommentDocument)
  const [editing, setEditing] = useState(false)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const run = async (fn: Run) => {
    const problem = await attempt(fn, t('failed'))
    setError(problem)
    onChanged()
    return problem
  }
  if (c.removed) return <p className="rounded-2xl bg-surface-2 px-4 py-2 text-sm italic text-muted">{t('removed')}</p>
  return (
    <article className={`flex flex-col gap-1.5 rounded-2xl border px-4 py-3 ${c.pendingApproval ? 'border-dashed border-warn/60' : 'border-border'} bg-bg`}>
      <div className="flex flex-wrap items-center gap-2 text-sm">
        {c.author ? (
          <Link href={`/u/${c.author.handle}`} className="font-semibold hover:text-accent">
            {c.author.displayName}
          </Link>
        ) : null}
        <span className="text-xs text-muted">
          {ago(c.createdAt)}
          {c.editedAt ? ` · ${t('edited')}` : ''}
        </span>
        {c.private ? (
          <span className="inline-flex items-center gap-1 rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">
            <Lock className="size-3" aria-hidden />
            {t('private')}
          </span>
        ) : null}
        {c.pendingApproval ? <span className="rounded-full bg-warn/10 px-2 py-0.5 text-xs text-warn">{t('waiting')}</span> : null}
      </div>
      <ContentModeration entityType="COMMENT" item={c} onAppealed={onChanged} />
      {editing ? (
        <form
          className="flex flex-col gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            void run(() => edit({ variables: { commentId: c.id, body: textToDoc(text) } })).then((problem) => !problem && setEditing(false))
          }}
        >
          <label className="sr-only" htmlFor={`edit-${c.id}`}>
            {t('editLabel')}
          </label>
          <textarea id={`edit-${c.id}`} value={text} rows={2} maxLength={5000} onChange={(e) => setText(e.target.value)} className="resize-y rounded-xl border border-border bg-surface px-3 py-2 text-sm" />
          <div className="flex gap-2 self-end">
            <Button type="button" variant="secondary" size="sm" onClick={() => setEditing(false)}>
              {t('cancel')}
            </Button>
            <Button type="submit" size="sm" disabled={!text.trim()}>
              {t('save')}
            </Button>
          </div>
        </form>
      ) : (
        <RichDoc doc={c.body as Doc} className="text-sm" mentions />
      )}
      <div className="flex flex-wrap items-center gap-3">
        <ReactionBar size="sm" target={{ type: 'COMMENT', id: c.id }} reactions={c.reactions} disabled={c.pendingApproval} onChanged={onChanged} />
        <span className="ml-auto flex gap-3 text-xs font-semibold text-muted">
          {c.viewerCan.approve ? (
            <button type="button" className="text-accent hover:underline" onClick={() => void run(() => approve({ variables: { commentId: c.id } }))}>
              {t('approve')}
            </button>
          ) : null}
          {c.viewerCan.edit && !editing ? (
            <button
              type="button"
              className="hover:text-fg"
              onClick={() => {
                setText(plain(c.body))
                setEditing(true)
              }}
            >
              {t('edit')}
            </button>
          ) : null}
          {c.viewerCan.delete ? (
            <button
              type="button"
              className="hover:text-bad"
              onClick={() => {
                if (window.confirm(t('deleteConfirm'))) void run(() => remove({ variables: { commentId: c.id } }))
              }}
            >
              {t('delete')}
            </button>
          ) : null}
          {c.author ? <ReportButton look="text" entityType="COMMENT" entityId={c.id} authorId={c.author.id} /> : null}
        </span>
      </div>
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </article>
  )
}
