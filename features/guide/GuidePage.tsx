import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { ReplayWalkthrough } from '@/components/guide/ReplayWalkthrough'
import { SUPPORT_EMAIL } from '@/lib/site'

const SECTIONS = [
  { id: 'read', points: ['p1', 'p2', 'p3'] as const, href: '/subjects', link: 'link' },
  { id: 'write', points: ['p1', 'p2', 'p3', 'p4'] as const, href: '/notes', link: 'link' },
  { id: 'groups', points: ['p1', 'p2'] as const, href: '/groups', link: 'link' },
  { id: 'classes', points: ['p1', 'p2'] as const, href: '/classes', link: 'link' },
  { id: 'study', points: ['p1', 'p2', 'p3', 'p4', 'p5'] as const, href: '/exams', link: 'link' },
  { id: 'profile', points: ['p1', 'p2', 'p3', 'p4', 'p5'] as const, href: '/profile', link: 'link' },
] as const

/** What LearnViaNotes can do today. Copy stays in messages/en.json and only names features the app actually has. */
export async function GuidePage() {
  const t = await getTranslations('guide')
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-8 px-4 py-8 sm:py-10">
      <header className="flex flex-col gap-3">
        <h1 className="text-3xl font-semibold tracking-tight">{t('title')}</h1>
        <p className="max-w-2xl text-sm leading-6 text-muted sm:text-base">{t('lead')}</p>
        <nav aria-label={t('onThisPage')} className="flex flex-wrap gap-2">
          {SECTIONS.map((section) => (
            <a key={section.id} href={`#${section.id}`} className="rounded-[4px] border border-border bg-surface px-3 py-1.5 text-sm font-medium text-fg hover:border-accent hover:text-accent">
              {t(`${section.id}.title`)}
            </a>
          ))}
        </nav>
      </header>
      {SECTIONS.map((section) => (
        <section key={section.id} id={section.id} aria-labelledby={`${section.id}-title`} className="scroll-mt-24 rounded-2xl border border-border bg-surface p-4 sm:p-5">
          <h2 id={`${section.id}-title`} className="text-lg font-semibold">
            {t(`${section.id}.title`)}
          </h2>
          <p className="mt-1 text-sm leading-6 text-muted">{t(`${section.id}.lead`)}</p>
          <ul className="mt-3 flex list-disc flex-col gap-2 pl-5 text-sm leading-6">
            {section.points.map((point) => (
              <li key={point}>{t(`${section.id}.${point}`)}</li>
            ))}
          </ul>
          <p className="mt-3">
            <Link href={section.href} className="text-sm font-medium text-accent hover:underline">
              {t(`${section.id}.${section.link}`)}
            </Link>
          </p>
        </section>
      ))}
      <section id="help" aria-labelledby="help-title" className="scroll-mt-24 rounded-2xl border border-border bg-surface p-4 sm:p-5">
        <h2 id="help-title" className="text-lg font-semibold">
          {t('helpTitle')}
        </h2>
        <p className="mt-1 text-sm leading-6 text-muted">{t('helpLead')}</p>
        <p className="mt-3 text-sm">
          <a className="font-medium text-accent hover:underline" href={`mailto:${SUPPORT_EMAIL}`}>
            {SUPPORT_EMAIL}
          </a>
        </p>
        <div className="mt-4">
          <ReplayWalkthrough label={t('replay')} />
        </div>
      </section>
    </div>
  )
}
