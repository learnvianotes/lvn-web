import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { StudentIdAdmin } from '@/features/verification/StudentIdAdmin'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('verification.collegeIdAdmin'))('title'), robots: { index: false } }
}

/** College ID cards for platform admins (lvn-backend ADR-0099). Path: /admin/student-id. */
export default function StudentIdAdminPage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <StudentIdAdmin />
    </div>
  )
}
