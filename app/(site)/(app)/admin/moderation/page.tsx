import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ModerationQueue } from '@/features/moderation/ModerationQueue'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('moderation.queue'))('title'), robots: { index: false } }
}

export default function ModerationPage() {
  return (
    <div className="mx-auto w-full max-w-5xl">
      <ModerationQueue />
    </div>
  )
}
