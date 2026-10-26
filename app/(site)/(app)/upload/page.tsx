import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { UploadPage } from '@/features/studio/UploadPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('studio.upload'))('title'), robots: { index: false } }
}

export default function Upload() {
  return <UploadPage />
}
