import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AccountPage } from '@/components/auth/AccountPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('profile'))('title'), robots: { index: false } }
}

export default function ProfilePage() {
  return <AccountPage />
}
