import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { Suspense } from 'react'
import { GitHubSetup } from '@/features/workspaces/GitHubSetup'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('workspaces.app'))('setupTitle'), robots: { index: false } }
}

/** Where GitHub returns after the App is installed on a workspace's repository (lvn-backend ADR-0078). */
export default function GitHubSetupPage() {
  return (
    <Suspense>
      <GitHubSetup />
    </Suspense>
  )
}
