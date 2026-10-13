import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Review } from '@/features/learning/Review'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('review'))('title'), robots: { index: false } }
}

/** Today's flashcard reviews (lvn-backend ADR-0068). */
export default function ReviewPage() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col gap-6">
      <Review />
    </div>
  )
}
