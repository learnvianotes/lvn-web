'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { BadgeCheck, Bell, CheckCheck, Download, FileInput, Share2 } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { MarkNotificationsReadDocument, NotificationsDocument, type NotificationFieldsFragment } from '@/graphql/generated/graphql'
import { ago } from '@/features/notes/look'
import { describeNotification } from './describe'

const PAGE = 20

const ICONS: Partial<Record<NotificationFieldsFragment['category'], typeof Bell>> = {
  SHARE: Share2,
  VERIFICATION: BadgeCheck,
  DATA_EXPORT: Download,
  NOTES_IMPORT: FileInput,
}

/** The viewer's notifications, newest first (lvn-backend ADR-0042); opening one marks it read. */
export function NotificationsList() {
  const t = useTranslations('notifications')
  const router = useRouter()
  const { data, loading, fetchMore } = useQuery(NotificationsDocument, { variables: { first: PAGE }, fetchPolicy: 'cache-and-network' })
  const [mark] = useMutation(MarkNotificationsReadDocument)
  const [more, setMore] = useState(false)
  const items = data?.notifications.edges.map((e) => e.node) ?? []
  const unread = data?.unreadNotificationCount ?? 0

  const markRead = async (input: { ids?: string[]; all?: boolean }) => {
    const now = new Date().toISOString()
    await mark({
      variables: { input },
      update: (cache, res) => {
        const left = res.data?.markNotificationsRead.unreadCount
        if (left === undefined) return
        cache.modify({ fields: { unreadNotificationCount: () => left } })
        for (const n of items) {
          if (input.all || input.ids?.includes(n.id)) cache.modify({ id: cache.identify({ __typename: 'Notification', id: n.id }), fields: { readAt: (v: string | null) => v ?? now } })
        }
      },
    })
  }

  const open = (n: NotificationFieldsFragment) => {
    if (!n.readAt) void markRead({ ids: [n.id] })
    router.push(n.path)
  }

  const older = async () => {
    setMore(true)
    try {
      await fetchMore({
        variables: { first: PAGE, after: data?.notifications.pageInfo.endCursor },
        updateQuery: (prev, { fetchMoreResult }) => ({
          ...fetchMoreResult,
          notifications: { ...fetchMoreResult.notifications, edges: [...prev.notifications.edges, ...fetchMoreResult.notifications.edges] },
        }),
      })
    } finally {
      setMore(false)
    }
  }

  return (
    <section className="mx-auto max-w-2xl">
      <header className="mb-4 flex items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold tracking-tight">{t('title')}</h1>
        {unread ? (
          <button type="button" onClick={() => void markRead({ all: true })} className="inline-flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-accent hover:bg-accent-soft">
            <CheckCheck className="size-4" aria-hidden />
            {t('markAll')}
          </button>
        ) : null}
      </header>
      {!items.length && loading ? <div aria-hidden className="h-40 animate-pulse rounded-2xl bg-surface-2" /> : null}
      {!items.length && !loading ? (
        <p className="flex flex-col items-center gap-3 rounded-2xl border border-dashed border-border px-6 py-12 text-center text-muted">
          <Bell className="size-8" aria-hidden />
          {t('empty')}
        </p>
      ) : null}
      {items.length ? (
        <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
          {items.map((n) => {
            const Icon = ICONS[n.category] ?? Bell
            return (
              <li key={n.id}>
                <button type="button" onClick={() => open(n)} className={`flex w-full items-start gap-3 px-4 py-3 text-left transition hover:bg-surface-2 ${n.readAt ? '' : 'bg-accent-soft/40'}`}>
                  <span className="mt-0.5 grid size-9 shrink-0 place-items-center rounded-full bg-accent-soft text-accent">
                    <Icon className="size-4" aria-hidden />
                  </span>
                  <span className="flex min-w-0 flex-1 flex-col">
                    <span className={n.readAt ? '' : 'font-semibold'}>{describeNotification(n, t)}</span>
                    <span className="text-xs text-muted">{ago(n.createdAt)}</span>
                  </span>
                  {n.readAt ? null : (
                    <span className="mt-2 size-2.5 shrink-0 rounded-full bg-accent">
                      <span className="sr-only">{t('unread')}</span>
                    </span>
                  )}
                </button>
              </li>
            )
          })}
        </ul>
      ) : null}
      {data?.notifications.pageInfo.hasNextPage ? (
        <div className="mt-4 flex justify-center">
          <button type="button" disabled={more} onClick={() => void older()} className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-surface-2 disabled:opacity-60">
            {t('older')}
          </button>
        </div>
      ) : null}
    </section>
  )
}
