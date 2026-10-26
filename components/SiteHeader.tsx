import { BookOpen } from 'lucide-react'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { HomeLink } from './brand/HomeLink'
import { Logo } from './brand/Logo'
import { NotificationBell } from '@/features/notifications/NotificationBell'
import { SearchButton } from '@/features/search/SearchButton'
import { AccountLink } from './auth/AccountLink'
import { AppearanceMenu } from './theme/AppearanceMenu'
import { GuestNav } from './landing/GuestNav'
import { PublicMenu } from './landing/PublicMenu'

export async function SiteHeader() {
  const t = await getTranslations('site')
  const ta = await getTranslations('auth.nav')
  return (
    <header className="sticky top-0 z-30 border-b border-border bg-bg/85 pt-[env(safe-area-inset-top)] backdrop-blur supports-[backdrop-filter]:bg-bg/70">
      <div className="relative mx-auto flex h-14 max-w-6xl items-center gap-2 px-4 sm:gap-3">
        <HomeLink label={t('name')} className="flex min-w-0 items-center gap-2 text-base font-extrabold tracking-tight sm:text-lg">
          <Logo size={30} />
          <span aria-hidden="true" className="truncate">
            {t('wordmark.lead')}
            <span className="text-accent">{t('wordmark.accent')}</span>
          </span>
        </HomeLink>
        <PublicMenu labels={{ menu: t('nav.menu'), close: t('nav.menuClose'), features: t('nav.features'), subjects: t('nav.subjects'), community: t('nav.community'), resources: t('nav.resources'), start: t('nav.start') }} />
        <nav className="ml-auto flex items-center gap-0.5 sm:gap-1" aria-label="Main">
          <GuestNav labels={{ features: t('nav.features'), subjects: t('nav.subjects'), community: t('nav.community'), start: t('nav.start') }} />
          {/* An icon on phones, like the account links, so the header fits a phone's width with the bell. */}
          <Link href="/subjects" aria-label={t('nav.notes')} className="inline-flex items-center rounded-lg px-2 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg sm:px-3 md:hidden">
            <BookOpen className="size-4 sm:hidden" aria-hidden />
            <span className="hidden sm:inline">{t('nav.notes')}</span>
          </Link>
          {/* From laptops up; narrower screens reach the catalogue from the account page (until the app's side menu). */}
          <Link href="/resources" className="hidden items-center rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg lg:inline-flex">
            {t('nav.resources')}
          </Link>
          <SearchButton label={t('nav.search')} />
          <NotificationBell />
          <AccountLink labels={{ signIn: ta('signIn'), account: ta('account'), notes: ta('myNotes'), community: ta('community'), askAi: ta('askAi') }} />
          <AppearanceMenu />
        </nav>
      </div>
    </header>
  )
}
