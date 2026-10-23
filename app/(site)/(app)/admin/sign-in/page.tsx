import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { GoogleSignInSetting } from '@/components/auth/GoogleSignInSetting'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('authAdmin'))('title'), robots: { index: false } }
}

/** Platform admins turn Google sign-in on or off. The admin sidebar lists this page with the other settings. */
export default function GoogleSignInPage() {
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <GoogleSignInSetting />
    </div>
  )
}
