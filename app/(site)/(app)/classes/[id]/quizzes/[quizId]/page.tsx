import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { QuizPage } from '@/features/classes/quizzes/QuizPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('classes.quiz'))('pageTitle'), robots: { index: false } }
}

export default async function ClassQuiz({ params }: { params: Promise<{ id: string; quizId: string }> }) {
  const { id, quizId } = await params
  return <QuizPage classroomId={id} quizId={quizId} />
}
