import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminContests } from '@/features/contests/AdminContests'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminContests'))('title'), robots: { index: false } }
}

/** Writing weekly contests, for platform admins (lvn-backend ADR-0082). */
export default function AdminContestsPage() {
  return (
    <div className="mx-auto w-full max-w-5xl">
      <AdminContests />
    </div>
  )
}
