import type { Metadata } from 'next'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { HomeLink } from '@/components/brand/HomeLink'
import { Logo } from '@/components/brand/Logo'
import { AppearanceMenu } from '@/components/theme/AppearanceMenu'
import { LEGAL_DOCUMENTS } from '@/features/legal/documents'

/** Sign-in pages are for people, not search results (links in emails carry tokens). */
export const metadata: Metadata = { robots: { index: false, follow: false } }

/**
 * Sign-in, sign-up, verification and reset (§12.1 `(auth)`): one focused screen. A logo bar, the form centred in a
 * narrow column, and the legal links under it. No site navigation, hero or footer, so the form fits without scrolling.
 */
export default async function AuthLayout({ children }: { children: React.ReactNode }) {
  const t = await getTranslations('site')
  return (
    <AuthProvider>
      <div className="flex min-h-dvh flex-col bg-bg">
        <header className="border-b border-border pt-[env(safe-area-inset-top)]">
          <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
            <HomeLink label={t('name')} className="flex items-center gap-2 text-base font-semibold">
              <Logo size={28} />
              <span aria-hidden="true">
                {t('wordmark.lead')}
                {t('wordmark.accent')}
              </span>
            </HomeLink>
            <AppearanceMenu />
          </div>
        </header>
        <main id="main" className="flex flex-1 items-start justify-center px-4 py-8 sm:items-center sm:py-10">
          <div className="w-full max-w-[400px] sm:border sm:border-border sm:bg-surface sm:p-8">{children}</div>
        </main>
        <footer className="flex flex-wrap justify-center gap-x-5 gap-y-1 px-4 pb-[max(1rem,env(safe-area-inset-bottom))] text-xs text-muted">
          <Link href={LEGAL_DOCUMENTS.terms.path} className="hover:text-fg">{LEGAL_DOCUMENTS.terms.title}</Link>
          <Link href={LEGAL_DOCUMENTS.privacy.path} className="hover:text-fg">{LEGAL_DOCUMENTS.privacy.title}</Link>
        </footer>
      </div>
    </AuthProvider>
  )
}
