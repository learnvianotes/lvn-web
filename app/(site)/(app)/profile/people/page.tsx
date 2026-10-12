import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { PeopleLists } from '@/features/people/PeopleLists'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('people.lists'))('title'), robots: { index: false } }
}

export default function PeoplePage() {
  return <PeopleLists />
}
