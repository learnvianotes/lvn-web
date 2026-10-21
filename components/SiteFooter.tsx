import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { AnalyticsChoiceButton } from '@/components/analytics/Analytics'
import { LEGAL_DOCUMENTS } from '@/features/legal/documents'

export async function SiteFooter() {
  const t = await getTranslations('site')
  return (
    <footer className="border-t border-border">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-muted">
        <p className="font-medium text-fg">{t('name')}</p>
        <p className="mt-1">{t('footer')}</p>
        <nav aria-label={t('legalNav')} className="mt-3 flex flex-wrap gap-x-4 gap-y-1">
          {Object.values(LEGAL_DOCUMENTS).map((d) => (
            <Link key={d.path} href={d.path} className="hover:text-fg hover:underline">
              {d.title}
            </Link>
          ))}
          <AnalyticsChoiceButton />
        </nav>
      </div>
    </footer>
  )
}
