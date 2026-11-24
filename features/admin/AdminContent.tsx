'use client'

import { useQuery } from '@apollo/client/react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useFormatter, useTranslations } from 'next-intl'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { LoadFailed, Loading } from '@/components/ui/query-state'
import { canSeeSection } from '@/features/admin/AdminNav'
import { moderationFor } from '@/features/admin/content-actions'
import { CONTENT_TYPES, CONTENT_VISIBILITIES, countVariables, listVariables, readFilters, writeFilters, type ContentFilters } from '@/features/admin/content-query'
import { useViewerRole } from '@/features/admin/useViewerRole'
import { ModerationActions } from '@/features/moderation/ModerationActions'
import { AdminContentCountsDocument, AdminContentDocument, type AdminContentQuery } from '@/graphql/generated/graphql'

type Item = AdminContentQuery['adminContent']['edges'][number]['node']

const MODERATION_STATES = ['OK', 'PENDING_REVIEW', 'HIDDEN', 'REMOVED', 'PENDING', 'APPROVED', 'REJECTED', 'DRAFT', 'PUBLISHED'] as const

/** A path on this site. Anything else is not offered as a link. */
function internalPath(path: string): string | null {
  if (!path.startsWith('/') || path.startsWith('//')) return null
  return path
}

/**
 * /admin/content: one page of content that is not private, with counts for the chosen days. Filters stay in the URL.
 * Taking something down still goes through moderateContent, and only for the kinds that mutation accepts.
 */
export function AdminContent() {
  const t = useTranslations('adminContent')
  const format = useFormatter()
  const router = useRouter()
  const filters = readFilters(useSearchParams())
  const { role, ready } = useViewerRole()
  const allowed = ready && canSeeSection(role, 'content')
  const list = useQuery(AdminContentDocument, { variables: listVariables(filters), skip: !allowed, fetchPolicy: 'cache-and-network' })
  const counts = useQuery(AdminContentCountsDocument, { variables: countVariables(filters), skip: !allowed, fetchPolicy: 'cache-and-network' })

  if (!ready) return <Loading label={t('loading')} />
  if (!allowed) return <p className="text-muted">{t('notAllowed')}</p>

  const setFilters = (patch: Partial<ContentFilters>) => {
    const next = { ...filters, ...patch, ...('after' in patch ? {} : { after: '' }) }
    const search = writeFilters(next)
    router.replace(search ? `/admin/content?${search}` : '/admin/content', { scroll: false })
  }

  const rows = list.data?.adminContent.edges.map((edge) => edge.node) ?? []
  const page = list.data?.adminContent.pageInfo
  const when = (value: string) => format.dateTime(new Date(value), { dateStyle: 'medium', timeStyle: 'short' })
  const labelOf = (item: Item) => item.title || item.excerpt || t('untitled')

  return (
    <div className="flex flex-col gap-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold tracking-tight">{t('title')}</h1>
        <p className="max-w-3xl text-sm text-muted">{t('lead')}</p>
        <p className="text-sm text-muted">{t('privateHidden')}</p>
      </header>

      {counts.data ? (
        <ul aria-label={t('counts')} className="flex flex-wrap gap-2">
          {counts.data.adminContentCounts.counts.map((row) => (
            <li key={row.type} className="rounded-full bg-surface-2 px-3 py-1 text-sm">
              <span className="text-muted">{t(`kind.${row.type}`)}</span> <strong className="font-semibold">{row.count}</strong>
            </li>
          ))}
        </ul>
      ) : null}

      <div role="group" aria-label={t('filters')} className="flex flex-col gap-3 rounded-2xl border border-border bg-surface p-4">
        <div className="flex flex-wrap items-end gap-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('type')}</span>
            <select name="type" value={filters.type} onChange={(e) => setFilters({ type: e.target.value as ContentFilters['type'] })} className="h-11 rounded-xl border border-border bg-surface px-3">
              <option value="">{t('anyType')}</option>
              {CONTENT_TYPES.map((type) => (
                <option key={type} value={type}>
                  {t(`kind.${type}`)}
                </option>
              ))}
            </select>
          </label>
          <label className="flex min-w-48 flex-1 flex-col gap-1 text-sm">
            <span className="font-medium">{t('user')}</span>
            <Input name="user" value={filters.user} placeholder={t('userHint')} onChange={(e) => setFilters({ user: e.target.value })} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('from')}</span>
            <Input type="date" name="from" value={filters.from} onChange={(e) => setFilters({ from: e.target.value })} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('to')}</span>
            <Input type="date" name="to" value={filters.to} onChange={(e) => setFilters({ to: e.target.value })} />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium">{t('visibility')}</span>
            <select name="visibility" value={filters.visibility} onChange={(e) => setFilters({ visibility: e.target.value as ContentFilters['visibility'] })} className="h-11 rounded-xl border border-border bg-surface px-3">
              <option value="">{t('anyVisibility')}</option>
              {CONTENT_VISIBILITIES.map((visibility) => (
                <option key={visibility} value={visibility}>
                  {t(`visibilityValue.${visibility}`)}
                </option>
              ))}
            </select>
          </label>
        </div>
        <p className="text-xs text-muted">{t('datesHint')}</p>
      </div>

      {list.error && !list.data ? <LoadFailed onRetry={() => void list.refetch()} /> : null}
      {list.loading && !list.data ? <Loading label={t('loading')} /> : null}
      {list.data && !rows.length ? (
        <div className="flex flex-col items-center gap-1 rounded-3xl border border-dashed border-border px-6 py-12 text-center">
          <p className="font-semibold">{t('empty')}</p>
          <p className="text-sm text-muted">{t('emptyLead')}</p>
        </div>
      ) : null}
      {rows.length ? (
        <div className="overflow-x-auto rounded-2xl border border-border">
          <table className="w-full min-w-[64rem] text-left text-sm">
            <caption className="sr-only">{t('table')}</caption>
            <thead className="bg-surface-2 text-xs text-muted">
              <tr>
                <th className="px-3 py-2 font-semibold">{t('columns.type')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.text')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.author')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.visibility')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.moderation')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.created')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.updated')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.open')}</th>
                <th className="px-3 py-2 font-semibold">{t('columns.actions')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {rows.map((item) => {
                const href = internalPath(item.deepLink)
                const actions = moderationFor(item)
                const state = item.moderation
                const known = MODERATION_STATES.find((value) => value === state)
                return (
                  <tr key={`${item.type}:${item.id}`} className="align-top">
                    <td className="px-3 py-3 font-medium">{t(`kind.${item.type}`)}</td>
                    <td className="max-w-xs px-3 py-3">
                      <p className="line-clamp-3">{labelOf(item)}</p>
                    </td>
                    <td className="px-3 py-3">
                      <p>@{item.author.handle}</p>
                      <p className="text-muted">{item.author.email}</p>
                    </td>
                    <td className="px-3 py-3">{t(`visibilityValue.${item.visibility}`)}</td>
                    <td className="px-3 py-3">{known ? t(`moderation.${known}`) : (state ?? t('moderation.none'))}</td>
                    <td className="whitespace-nowrap px-3 py-3">{when(item.createdAt)}</td>
                    <td className="whitespace-nowrap px-3 py-3">{when(item.updatedAt)}</td>
                    <td className="px-3 py-3">
                      {href ? (
                        <Link href={href} className="font-semibold text-accent hover:underline">
                          {t('open')}
                        </Link>
                      ) : (
                        <span className="text-muted">{t('open')}</span>
                      )}
                    </td>
                    <td className="min-w-64 px-3 py-3">
                      {actions ? (
                        <ModerationActions entityType={actions.entityType} entityId={item.id} actions={actions.actions} onDone={() => void list.refetch()} />
                      ) : (
                        <span className="text-xs text-muted">{t('noActions')}</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      ) : null}
      {page && (filters.after || page.hasNextPage) ? (
        <div className="flex flex-wrap gap-2">
          {filters.after ? (
            <Button type="button" variant="secondary" onClick={() => setFilters({ after: '' })}>
              {t('first')}
            </Button>
          ) : null}
          {page.hasNextPage && page.endCursor ? (
            <Button type="button" variant="secondary" onClick={() => setFilters({ after: page.endCursor ?? '' })}>
              {t('next')}
            </Button>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}
