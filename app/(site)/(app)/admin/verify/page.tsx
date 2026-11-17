import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AdminVerifyPage } from '@/features/admin/AdminMfa'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('adminMfa'))('title'), robots: { index: false } }
}

/**
 * Landing spot after sign-in when an admin still needs a code. The layout shows the code screen while it is
 * required; this page only sends people onward once it is not.
 */
export default function VerifyPage() {
  return <AdminVerifyPage />
}
