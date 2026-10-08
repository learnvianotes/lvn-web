import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { Logo } from './brand/Logo'
import { AccountLink } from './auth/AccountLink'
import { ThemeToggle } from './ThemeToggle'

export async function SiteHeader() {
  const t = await getTranslations('site')
  const ta = await getTranslations('auth.nav')
  return (
    <header className="sticky top-0 z-30 border-b border-border bg-bg/85 backdrop-blur supports-[backdrop-filter]:bg-bg/70">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4">
        <Link href="/" className="flex items-center gap-2 text-lg font-extrabold tracking-tight" aria-label={t('name')}>
          <Logo size={30} />
          <span aria-hidden="true">
            {t('wordmark.lead')}
            <span className="text-accent">{t('wordmark.accent')}</span>
          </span>
        </Link>
        <nav className="ml-auto flex items-center gap-1" aria-label="Main">
          <Link href="/core" className="rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg">
            {t('nav.notes')}
          </Link>
          <AccountLink labels={{ signIn: ta('signIn'), account: ta('account') }} />
          <ThemeToggle labels={{ toLight: t('theme.toLight'), toDark: t('theme.toDark') }} />
        </nav>
      </div>
    </header>
  )
}
