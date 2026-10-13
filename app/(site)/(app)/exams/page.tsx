import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Exams } from '@/features/learning/Exams'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('exams'))('title'), robots: { index: false } }
}

/** The signed-in person's exams and weak topics (lvn-backend ADR-0070). */
export default function ExamsPage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Exams />
    </div>
  )
}
