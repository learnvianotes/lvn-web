import type { Metadata } from 'next'
import { getTranslations } from 'next-intl/server'
import { ProjectsPage } from '@/features/studio/ProjectsPage'

export async function generateMetadata(): Promise<Metadata> {
  return { title: (await getTranslations('studio.projects'))('title'), robots: { index: false } }
}

export default function Projects() {
  return <ProjectsPage />
}
