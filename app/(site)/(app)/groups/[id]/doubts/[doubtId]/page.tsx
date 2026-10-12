import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { DoubtPage } from '@/features/workspaces/DoubtPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('workspaces'))('doubtTitlePage'), robots: { index: false } }
}

export default async function Doubt({ params }: { params: Promise<{ id: string; doubtId: string }> }) {
  const { id, doubtId } = await params
  return <DoubtPage groupId={id} id={doubtId} />
}
