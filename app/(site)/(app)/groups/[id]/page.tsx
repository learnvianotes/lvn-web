import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { GroupPage } from '@/features/groups/GroupPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('groups'))('title'), robots: { index: false } }
}

export default async function Group({ params }: { params: Promise<{ id: string }> }) {
  return <GroupPage id={(await params).id} />
}
