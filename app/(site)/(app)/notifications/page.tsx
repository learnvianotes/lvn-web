import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { NotificationsList } from '@/features/notifications/NotificationsList'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('notifications'))('title'), robots: { index: false } }
}

export default function NotificationsPage() {
  return <NotificationsList />
}
