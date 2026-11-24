'use client'

import { useMutation } from '@apollo/client/react'
import { ExternalLink, GitBranch, Star } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useState, type ReactNode } from 'react'
import { Button } from '@/components/ui/button'
import { attempt } from '@/features/groups/shared'
import { ago } from '@/features/notes/look'
import { DisconnectRepositoryAppDocument, SetGroupRepositoryDocument, type RepositoryCardFragment } from '@/graphql/generated/graphql'
import { safeLinkHref } from '@/lib/http-url'

/**
 * A workspace's repository (lvn-backend ADR-0048): public details from GitHub or GitLab when the provider shows them,
 * else the link. LVN never hosts git. Admins link or change it. With the GitHub App set up (ADR-0078), members see its
 * activity and admins connect or disconnect it.
 */
export function RepositoryCard({ groupId, repository, canManage, onChanged }: { groupId: string; repository: RepositoryCardFragment | null; canManage: boolean; onChanged: () => void }) {
  const t = useTranslations('workspaces')
  const [save, saving] = useMutation(SetGroupRepositoryDocument)
  const [editing, setEditing] = useState(false)
  const [url, setUrl] = useState(repository?.url ?? '')
  const [error, setError] = useState<string | null>(null)
  const submit = async (value: string | null) => {
    const problem = await attempt(() => save({ variables: { groupId, url: value } }), t('failed'))
    setError(problem)
    if (!problem) setEditing(false)
    onChanged()
  }
  if (!repository && !canManage) return null
  return (
    <div className="flex flex-col gap-2 rounded-2xl border border-border bg-bg p-4">
      {repository && !editing ? (
        <div className="flex flex-col gap-1.5">
          <RepositoryLink url={repository.url} rel="noopener noreferrer nofollow ugc" className="inline-flex w-fit items-center gap-2 font-semibold hover:text-accent">
            <GitBranch className="size-4 text-accent" aria-hidden />
            {repository.name ?? repository.url.replace(/^https:\/\//, '')}
            <ExternalLink className="size-3.5 text-muted" aria-hidden />
          </RepositoryLink>
          {repository.available ? (
            <>
              {repository.description ? <p className="text-sm text-muted">{repository.description}</p> : null}
              <p className="flex flex-wrap items-center gap-3 text-xs text-muted">
                {repository.language ? <span>{repository.language}</span> : null}
                <span className="inline-flex items-center gap-1">
                  <Star className="size-3.5" aria-hidden />
                  {t('stars', { count: repository.stars ?? 0 })}
                </span>
                {repository.pushedAt ? <span>{t('pushed', { when: ago(repository.pushedAt) })}</span> : null}
              </p>
            </>
          ) : (
            <p className="text-xs text-muted">{t(`linkOnly.${repository.provider}`)}</p>
          )}
        </div>
      ) : null}
      {repository?.app && !editing ? <RepositoryApp groupId={groupId} app={repository.app} events={repository.events ?? []} canManage={canManage} onChanged={onChanged} /> : null}
      {!repository && !editing ? <p className="text-sm text-muted">{t('noRepository')}</p> : null}
      {canManage && !editing ? (
        <Button variant="secondary" size="sm" className="w-fit" onClick={() => setEditing(true)}>
          {repository ? t('changeRepository') : t('linkRepository')}
        </Button>
      ) : null}
      {editing ? (
        <form
          className="flex flex-col gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            void submit(url.trim() || null)
          }}
        >
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold">{t('repositoryLabel')}</span>
            <input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://github.com/owner/project" inputMode="url" autoComplete="off" className="h-10 rounded-xl border border-border bg-surface px-3 text-sm" />
          </label>
          <p className="text-xs text-muted">{t('repositoryHint')}</p>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" size="sm" disabled={saving.loading}>
              {t('save')}
            </Button>
            {repository ? (
              <Button type="button" variant="secondary" size="sm" onClick={() => void submit(null)}>
                {t('unlink')}
              </Button>
            ) : null}
            <Button type="button" variant="ghost" size="sm" onClick={() => setEditing(false)}>
              {t('cancel')}
            </Button>
          </div>
        </form>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </div>
  )
}

/** The GitHub App on a workspace's repository (lvn-backend ADR-0078): its activity, and connecting or disconnecting it. */
function RepositoryApp({ groupId, app, events, canManage, onChanged }: { groupId: string; app: NonNullable<RepositoryCardFragment['app']>; events: NonNullable<RepositoryCardFragment['events']>; canManage: boolean; onChanged: () => void }) {
  const t = useTranslations('workspaces.app')
  const [disconnect, disconnecting] = useMutation(DisconnectRepositoryAppDocument)
  const [error, setError] = useState<string | null>(null)
  if (!app.connected) {
    const installUrl = safeLinkHref(app.installUrl)
    if (!installUrl) return <p className="text-xs text-muted">{t('notConnected')}</p>
    return (
      <div className="flex flex-col gap-1.5 border-t border-border pt-2">
        <p className="text-xs text-muted">{t('connectHint')}</p>
        <Button asChild size="sm" className="w-fit">
          <a href={installUrl}>{t('connect')}</a>
        </Button>
      </div>
    )
  }
  return (
    <section aria-labelledby={`repo-activity-${groupId}`} className="flex flex-col gap-2 border-t border-border pt-2">
      <h3 id={`repo-activity-${groupId}`} className="text-sm font-semibold">
        {t('title')}
      </h3>
      {events.length ? (
        <ul className="flex flex-col gap-1.5">
          {events.map((e) => (
            <li key={e.id} className="flex flex-col text-sm">
              <RepositoryLink url={e.url} rel="noopener noreferrer nofollow" className="font-medium hover:text-accent">
                {e.number ? `#${e.number} ` : ''}
                {e.title}
              </RepositoryLink>
              <span className="text-xs text-muted">
                {t(`kind.${e.kind}`)} {t(`action.${e.action}`)}
                {e.authorLogin ? ` ${t('by', { login: e.authorLogin })}` : ''} · {ago(e.at)}
              </span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-xs text-muted">{t('none')}</p>
      )}
      {canManage ? (
        <Button
          variant="ghost"
          size="sm"
          className="w-fit"
          disabled={disconnecting.loading}
          onClick={() => {
            if (!window.confirm(t('disconnectConfirm'))) return
            void attempt(() => disconnect({ variables: { groupId } }), t('disconnect')).then((problem) => {
              setError(problem)
              onChanged()
            })
          }}
        >
          {t('disconnect')}
        </Button>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-bad">
          {error}
        </p>
      ) : null}
    </section>
  )
}

/** A repository or event URL people typed or a provider sent. Anything other than http(s) stays text. */
function RepositoryLink({ url, className, rel, children }: { url: string; className: string; rel: string; children: ReactNode }) {
  const href = safeLinkHref(url)
  if (!href) return <span className={className}>{children}</span>
  return (
    <a href={href} target="_blank" rel={rel} className={className}>
      {children}
    </a>
  )
}
