import { getTranslations } from 'next-intl/server'

export async function SiteFooter() {
  const t = await getTranslations('site')
  return (
    <footer className="border-t border-border">
      <div className="mx-auto max-w-6xl px-4 py-8 text-sm text-muted">
        <p className="font-medium text-fg">{t('name')}</p>
        <p className="mt-1">{t('footer')}</p>
      </div>
    </footer>
  )
}
