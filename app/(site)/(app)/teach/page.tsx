import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Teach } from '@/features/verification/Teach'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('teach'))('title'), robots: { index: false } }
}

/** Becoming a teacher (lvn-backend ADR-0073). */
export default function TeachPage() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <Teach />
    </div>
  )
}
