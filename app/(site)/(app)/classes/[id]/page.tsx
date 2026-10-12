import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ClassPage } from '@/features/classes/ClassPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('classes'))('title'), robots: { index: false } }
}

export default async function Classroom({ params }: { params: Promise<{ id: string }> }) {
  return <ClassPage id={(await params).id} />
}
