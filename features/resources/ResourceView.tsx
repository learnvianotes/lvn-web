'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { ExternalLink, Send } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { Alert } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { Discussion } from '@/features/discussion/Discussion'
import { ReportButton } from '@/features/moderation/ReportDialog'
import { DeleteResourceDocument, MyResourcesDocument, ResourceDocument, type ResourceFieldsFragment } from '@/graphql/generated/graphql'
import { safeLinkHref } from '@/lib/http-url'
import { isNotThere } from '@/lib/query'
import { useSession } from '@/state/session'
import { SaveButton } from './Catalogue'
import { RecommendDialog } from './RecommendDialog'

/** A resource's page (lvn-backend ADR-0074): public once approved; its submitter sees it while it waits, with why if rejected. */
export function ResourcePage({ id }: { id: string }) {
  return (
    <AuthProvider>
      <Page id={id} />
    </AuthProvider>
  )
}

function Page({ id }: { id: string }) {
  const t = useTranslations('resources')
  const status = useSession((s) => s.status)
  const { data, loading, error, refetch } = useQuery(ResourceDocument, { variables: { id }, skip: status === 'unknown', fetchPolicy: 'cache-and-network' })
  const resource = data?.resource
  if (!resource) {
    if (status === 'unreachable' && !resource) {
      return (
        <div className="mx-auto max-w-md px-4 py-16">
          <LoadFailed onRetry={refetch} />
        </div>
      )
    }
    if (loading || status === 'unknown' || (!data && !error)) return <Loading className="mx-auto max-w-3xl px-4 py-10" />
    // Not there only when the API said so; a resource that could not be asked for is offered again.
    if (error && !isNotThere(error)) {
      return (
        <div className="mx-auto max-w-md px-4 py-16">
          <LoadFailed onRetry={refetch} />
        </div>
      )
    }
    return (
      <div className="mx-auto max-w-md px-4 py-16 text-center">
        <h1 className="text-2xl font-semibold">{t('notFound')}</h1>
        <p className="mt-2 text-sm text-muted">{t('notFoundLead')}</p>
      </div>
    )
  }
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 px-4 py-8">
      <ResourceDetails resource={resource} />
      {resource.status === 'APPROVED' ? <ResourceDiscussion id={resource.id} /> : null}
    </div>
  )
}

export function ResourceDetails({ resource: r }: { resource: ResourceFieldsFragment }) {
  const t = useTranslations('resources')
  const router = useRouter()
  const [remove, removing] = useMutation(DeleteResourceDocument, { refetchQueries: [MyResourcesDocument] })
  const [error, setError] = useState<string | null>(null)
  const [recommending, setRecommending] = useState(false)
  const signedIn = useSession((s) => s.status) === 'signed-in'
  const link = safeLinkHref(r.url)
  return (
    <article className="flex flex-col gap-5" aria-labelledby="resource-title">
      {r.status !== 'APPROVED' ? (
        <section role="note" className={`flex flex-col gap-1 rounded-2xl border p-4 text-sm ${r.status === 'REJECTED' ? 'border-bad/30 bg-bad/10' : 'border-border bg-surface-2'}`}>
          <p className="font-semibold">{t(`status.${r.status}`)}</p>
          {r.status === 'PENDING' ? <p className="text-muted">{t('pendingNote')}</p> : null}
          {r.status === 'REJECTED' && r.reason ? (
            <p>
              <span className="text-muted">{t('reasonTitle')}: </span>
              {r.reason}
            </p>
          ) : null}
        </section>
      ) : null}
      <div className="flex flex-col gap-5 sm:flex-row">
        {r.coverUrl ? (
          // eslint-disable-next-line @next/next/no-img-element -- a short-lived read URL from storage
          <img src={r.coverUrl} alt="" className="h-48 w-auto max-w-full self-start rounded-xl border border-border object-contain" />
        ) : null}
        <div className="flex min-w-0 flex-col gap-2">
          <span className="text-xs font-semibold text-accent">{t(`type.${r.type}`)}</span>
          <h1 id="resource-title" className="text-2xl font-semibold">
            {r.title}
          </h1>
          {r.author ? <p className="text-sm text-muted">{t('by', { author: r.author })}</p> : null}
          {/* A link people added: marked as user content and not followed by search engines (ADR-0074). */}
          {link ? (
            <a href={link} rel="ugc nofollow noopener" target="_blank" className="inline-flex items-center gap-1.5 self-start rounded-xl bg-accent px-4 py-2 text-sm font-semibold text-accent-fg hover:bg-accent/90">
              {t('open', { host: r.host })}
              <ExternalLink className="size-4" aria-hidden />
            </a>
          ) : (
            <span className="text-sm text-muted">{t('open', { host: r.host })}</span>
          )}
        </div>
      </div>
      {r.description ? <p className="whitespace-pre-line">{r.description}</p> : null}
      {r.topics.length ? (
        <ul className="flex flex-wrap gap-2" aria-label="Topics">
          {r.topics.map((topic) => (topic ? <li key={topic.id} className="rounded-full bg-surface-2 px-3 py-1 text-sm">{topic.title}</li> : null))}
        </ul>
      ) : null}
      <p className="text-sm text-muted">
        <Link href={`/u/${r.submittedBy.handle}`} className="hover:underline">
          {t('submittedBy', { name: r.submittedBy.displayName })}
        </Link>
      </p>
      {error ? <Alert tone="error">{error}</Alert> : null}
      {r.status === 'APPROVED' ? (
        <div className="flex flex-wrap items-center gap-3">
          <SaveButton resource={r} size="md" />
          <span className="text-sm text-muted">{t('saves', { count: r.saveCount })}</span>
          {signedIn ? (
            <Button variant="secondary" className="gap-1.5" onClick={() => setRecommending(true)}>
              <Send className="size-4" aria-hidden />
              {t('recommendButton')}
            </Button>
          ) : null}
          <RecommendDialog resourceId={r.id} open={recommending} onClose={() => setRecommending(false)} />
        </div>
      ) : null}
      <div className="flex flex-wrap gap-2">
        {r.viewerCan.edit ? (
          <Button asChild variant="secondary" size="sm">
            <Link href={`/resources/${r.id}/edit`}>{r.status === 'REJECTED' ? t('editAgain') : t('edit')}</Link>
          </Button>
        ) : null}
        {r.viewerCan.delete ? (
          <Button
            variant="ghost"
            size="sm"
            disabled={removing.loading}
            onClick={async () => {
              if (!window.confirm(t('deleteConfirm'))) return
              const res = await remove({ variables: { input: { id: r.id } } })
              const problem = res.data?.deleteResource.userErrors[0]?.message
              if (problem) setError(problem)
              else router.push('/resources/mine')
            }}
          >
            {t('delete')}
          </Button>
        ) : null}
        {r.viewerCan.report ? <ReportButton entityType="RESOURCE" entityId={r.id} look="text" /> : null}
      </div>
    </article>
  )
}

/** An approved resource's discussion (ADR-0075): for signed-in readers; visitors are asked to sign in. */
function ResourceDiscussion({ id }: { id: string }) {
  const t = useTranslations('discussion')
  const status = useSession((s) => s.status)
  if (status === 'signed-in') return <Discussion target={{ type: 'RESOURCE', id }} />
  if (status !== 'signed-out') return null
  return (
    <p className="rounded-3xl border border-border bg-surface px-5 py-4 text-sm text-muted">
      <Link href={`/sign-in?next=${encodeURIComponent(`/resources/${id}`)}`} className="font-semibold text-accent hover:underline">
        {t('signIn')}
      </Link>
    </p>
  )
}
