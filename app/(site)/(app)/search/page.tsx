import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { SearchPage } from '@/features/search/SearchPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('search'))('title'), robots: { index: false } }
}

export default function Search() {
  return (
    <Suspense>
      <SearchPage />
    </Suspense>
  )
}
