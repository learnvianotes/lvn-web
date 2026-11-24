import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { PlansPage } from '@/features/plans/PlansPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('plans'))('title') }
}

/** Active plans, and — once someone is signed in — how much of theirs they have used. */
export default function Page() {
  return <PlansPage />
}
