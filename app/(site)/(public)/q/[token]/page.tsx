import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { SharedQuizPage } from '@/features/quizzes/SharedQuizPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('quizShare'))('taking'), robots: { index: false } }
}

/** A shared quiz. The API returns a relative path `/q/{token}`; this route is that path. */
export default async function QuizByLink({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params
  return <SharedQuizPage token={token} />
}
