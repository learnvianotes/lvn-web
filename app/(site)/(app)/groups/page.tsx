import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { GroupsHome } from '@/features/groups/GroupsHome'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('groups'))('title'), robots: { index: false } }
}

export default function GroupsPage() {
  return <GroupsHome />
}
