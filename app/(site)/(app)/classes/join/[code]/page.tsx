import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { JoinByCode } from '@/features/classes/JoinByCode'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('classes'))('joinTitle'), robots: { index: false } }
}

/** The link a teacher hands out; typed codes arrive here from /classes with ?via=code. */
export default async function JoinClass({ params, searchParams }: { params: Promise<{ code: string }>; searchParams: Promise<{ via?: string }> }) {
  const [{ code }, { via }] = await Promise.all([params, searchParams])
  return <JoinByCode code={decodeURIComponent(code)} via={via === 'code' ? 'CODE' : 'LINK'} />
}
