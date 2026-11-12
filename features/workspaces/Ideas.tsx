'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Lightbulb } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { QueryState } from '@/components/ui/query-state'
import { PostComments } from '@/features/discussion/PostComments'
import { attempt, textToDoc } from '@/features/groups/shared'
import { ago } from '@/features/notes/look'
import { RichDoc } from '@/features/notes/render/RichText'
import { CreateIdeaDocument, DeleteGroupPostDocument, WorkspaceIdeasDocument, type GroupDetailFragment } from '@/graphql/generated/graphql'
import type { Doc } from '@/lib/contracts/validation'
import { ContentModeration } from '@/features/moderation/ModerationBanner'
import { ReportButton } from '@/features/moderation/ReportDialog'

/** The ideas board (lvn-backend ADR-0048): ideas ranked by the team's reactions; react and discuss under each. */
export function Ideas({ group }: { group: GroupDetailFragment }) {
  const t = useTranslations('workspaces')
  const { data, loading, error: queryError, refetch } = useQuery(WorkspaceIdeasDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const [create, creating] = useMutation(CreateIdeaDocument)
  const [remove] = useMutation(DeleteGroupPostDocument)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const ideas = data?.group?.ideas ?? []
  return (
    <div className="flex flex-col gap-4">
      {group.viewerCan.post ? (
        <form
          className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-3 focus-within:border-accent"
          onSubmit={(e) => {
            e.preventDefault()
            void attempt(async () => {
              const res = await create({ variables: { groupId: group.id, body: textToDoc(text) } })
              if (res.data?.createGroupPost.post) setText('')
              return res
            }, t('failed')).then((p) => {
              setError(p)
              void refetch()
            })
          }}
        >
          <label className="sr-only" htmlFor="new-idea">
            {t('ideaLabel')}
          </label>
          <textarea id="new-idea" value={text} rows={2} onChange={(e) => setText(e.target.value)} placeholder={t('ideaPlaceholder')} className="resize-y border-0 bg-transparent text-sm focus:outline-none" />
          <Button type="submit" size="sm" className="self-end" disabled={creating.loading || !text.trim()}>
            {t('shareIdea')}
          </Button>
        </form>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <p className="text-xs text-muted">{t('ideasHint')}</p>
      {ideas.length ? (
        <ol className="flex flex-col gap-3">
          {ideas.map((idea, i) => (
            <li key={idea.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
              <div className="flex items-center gap-2 text-sm">
                <span className="grid size-6 place-items-center rounded-full bg-accent-soft text-xs font-bold text-accent" aria-label={t('rank', { n: i + 1 })}>
                  {i + 1}
                </span>
                <Lightbulb className="size-4 text-amber-500" aria-hidden />
                <Link href={`/u/${idea.author.handle}`} className="font-semibold hover:text-accent">
                  {idea.author.displayName}
                </Link>
                <span className="text-xs text-muted">{ago(idea.createdAt)}</span>
                <span className="ml-auto flex items-center gap-3 text-xs font-semibold text-muted">
                  {idea.viewerCan.delete ? (
                    <button type="button" className="hover:text-red-600" onClick={() => void remove({ variables: { postId: idea.id } }).then(() => refetch())}>
                      {t('delete')}
                    </button>
                  ) : null}
                  <ReportButton look="text" entityType="GROUP_POST" entityId={idea.id} authorId={idea.author.id} />
                </span>
              </div>
              <ContentModeration entityType="GROUP_POST" item={idea} onAppealed={() => void refetch()} />
              <RichDoc doc={idea.body as Doc} className="text-sm" mentions />
              <PostComments type="GROUP_POST" id={idea.id} count={idea.discussion.commentCount} />
            </li>
          ))}
        </ol>
      ) : data ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noIdeas')}</p>
      ) : (
        <QueryState loading={loading} error={queryError} onRetry={refetch} />
      )}
    </div>
  )
}
