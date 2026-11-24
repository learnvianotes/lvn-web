import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { AiProviders } from '@/features/ai/admin/AiProviders'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('aiAdmin'))('title'), robots: { index: false } }
}

/** Who answers AI requests (lvn-backend ADR-0065), for platform admins, until the admin app exists. */
export default function AiProvidersPage() {
  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
      <AiProviders />
    </div>
  )
}
