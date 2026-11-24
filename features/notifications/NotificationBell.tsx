'use client'

import { ApolloProvider, useApolloClient, useQuery } from '@apollo/client/react'
import { Bell } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { UnreadNotificationCountDocument } from '@/graphql/generated/graphql'
import { apolloClient } from '@/lib/apollo'
import { useSession } from '@/state/session'
import { useLive } from './live'

/**
 * The header's bell (lvn-backend ADR-0042): the unread count, refreshed whenever a live event arrives, linking to the
 * notifications page. Shown only to a signed-in tab. It brings its own client, as public pages have none around them.
 */
export function NotificationBell() {
  const signedIn = useSession((s) => s.status === 'signed-in')
  if (!signedIn) return null
  return (
    <ApolloProvider client={apolloClient()}>
      <BellLink />
    </ApolloProvider>
  )
}

function BellLink() {
  const t = useTranslations('notifications')
  const client = useApolloClient()
  const { data } = useQuery(UnreadNotificationCountDocument, { fetchPolicy: 'cache-and-network' })
  // Whatever changed, the count and any list on screen are fetched again.
  useLive(() => void client.refetchQueries({ include: ['UnreadNotificationCount', 'Notifications'] }))
  const unread = data?.unreadNotificationCount ?? 0
  return (
    <Link
      href="/notifications"
      aria-label={unread ? t('bellUnread', { count: unread }) : t('bell')}
      className="relative inline-flex items-center rounded-lg px-1.5 py-2 text-muted hover:bg-surface-2 hover:text-fg sm:px-2"
    >
      <Bell className="size-5" aria-hidden />
      {unread ? (
        <span aria-hidden className="absolute right-0.5 top-0.5 grid min-w-4 place-items-center rounded-[10px] bg-accent px-1 text-[10px] font-semibold leading-4 text-accent-fg">
          {unread > 99 ? '99+' : unread}
        </span>
      ) : null}
    </Link>
  )
}
