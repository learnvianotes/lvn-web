import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { SkillsEditor } from '@/features/people/SkillsEditor'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('people.skills'))('editTitle'), robots: { index: false } }
}

export default function SkillsPage() {
  return <SkillsEditor />
}
