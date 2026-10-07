import Image from 'next/image'
import Link from 'next/link'
import { getTranslations } from 'next-intl/server'
import { ThemeToggle } from './ThemeToggle'

export async function SiteHeader() {
  const t = await getTranslations('site')
  return (
    <header className="sticky top-0 z-30 border-b border-border bg-bg/85 backdrop-blur supports-[backdrop-filter]:bg-bg/70">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <Image src="/icons/icon-48.png" alt="" width={28} height={28} className="rounded-lg" priority />
          {t('name')}
        </Link>
        <nav className="ml-auto flex items-center gap-1" aria-label="Main">
          <Link href="/core" className="rounded-lg px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg">
            {t('nav.notes')}
          </Link>
          <ThemeToggle labels={{ toLight: t('theme.toLight'), toDark: t('theme.toDark') }} />
        </nav>
      </div>
    </header>
  )
}
