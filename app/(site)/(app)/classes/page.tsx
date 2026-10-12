import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ClassesHome } from '@/features/classes/ClassesHome'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('classes'))('title'), robots: { index: false } }
}

export default function ClassesPage() {
  return <ClassesHome />
}
