import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { QuizzesPage } from '@/features/contests/QuizzesPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('quizzes'))('title'), robots: { index: false } }
}

/** Quizzes: this week's contest, class quizzes waiting, practice and recent results (lvn-backend ADR-0082). */
export default function Quizzes() {
  return (
    <div className="mx-auto w-full max-w-3xl">
      <QuizzesPage />
    </div>
  )
}
