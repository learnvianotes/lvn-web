import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AchievementsPage } from '@/features/achievements/AchievementsPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('achievements'))('title'), robots: { index: false } }
}

/** Achievements, level and points (lvn-backend ADR-0080); the achievement notification opens here. */
export default function Achievements() {
  return (
    <div className="mx-auto w-full max-w-3xl">
      <AchievementsPage />
    </div>
  )
}
