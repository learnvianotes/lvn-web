import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { NotificationSettings } from '@/features/settings/NotificationSettings'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('settings'))('title'), robots: { index: false } }
}

export default function NotificationSettingsPage() {
  return <NotificationSettings />
}
