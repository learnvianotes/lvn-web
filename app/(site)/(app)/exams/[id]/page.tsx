import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ExamDetail } from '@/features/learning/Exams'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('exams'))('title'), robots: { index: false } }
}

/** One exam: Readiness, its topics and the revision plan (lvn-backend ADR-0070). */
export default async function ExamPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <ExamDetail id={id} />
    </div>
  )
}
