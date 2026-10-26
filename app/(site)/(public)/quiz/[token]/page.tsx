import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { SharedQuizPage } from '@/features/quizzes/SharedQuizPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('quizShare'))('taking'), robots: { index: false } }
}

export default async function QuizShare({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params
  return <SharedQuizPage token={token} />
}
