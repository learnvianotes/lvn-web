import { BookOpen } from 'lucide-react'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { Logo } from './brand/Logo'
import { NotificationBell } from '@/features/notifications/NotificationBell'
import { SearchButton } from '@/features/search/SearchButton'
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
          {/* The word mark from 400 px up; narrower phones show the logo (the link keeps the name for screen readers). */}
          <span aria-hidden="true" className="hidden min-[400px]:inline">
            {t('wordmark.lead')}
            <span className="text-accent">{t('wordmark.accent')}</span>
          </span>
        </Link>
        <nav className="ml-auto flex items-center gap-0.5 sm:gap-1" aria-label="Main">
          {/* An icon on phones, like the account links, so the header fits a phone's width with the bell. */}
          <Link href="/core" aria-label={t('nav.notes')} className="inline-flex items-center rounded-lg px-2 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg sm:px-3">
            <BookOpen className="size-4 sm:hidden" aria-hidden />
            <span className="hidden sm:inline">{t('nav.notes')}</span>
          </Link>
          <SearchButton label={t('nav.search')} />
          <NotificationBell />
          <AccountLink labels={{ signIn: ta('signIn'), account: ta('account'), notes: ta('myNotes'), community: ta('community') }} />
          <ThemeToggle labels={{ toLight: t('theme.toLight'), toDark: t('theme.toDark') }} />
        </nav>
      </div>
    </header>
  )
}
