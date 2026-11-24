import type { Metadata } from 'next'
import { IBM_Plex_Sans } from 'next/font/google'
import Link from 'next/link'
import { NextIntlClientProvider } from 'next-intl'
import { getLocale, getTranslations } from 'next-intl/server'
import { Button } from '@/components/ui/button'
import { themeBootScript } from '@/lib/theme'
import './globals.css'

/** 404 for URLs outside every route: / and /core have separate root layouts, so neither can render it. */

const inter = IBM_Plex_Sans({ subsets: ['latin'], weight: ['400', '500', '600'], variable: '--font-inter', display: 'swap' })

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('notFound')
  return { title: t('title'), robots: { index: false } }
}

const themeScript = themeBootScript()

export default async function GlobalNotFound() {
  const [locale, t] = await Promise.all([getLocale(), getTranslations('notFound')])
  return (
    <html lang={locale} className={inter.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body className="antialiased">
        <NextIntlClientProvider>
          <main className="mx-auto flex min-h-dvh max-w-xl flex-col items-start justify-center gap-4 px-4 py-16">
            <h1 className="text-3xl font-semibold tracking-tight">{t('title')}</h1>
            <p className="text-muted">{t('lead')}</p>
            <Button asChild><Link href="/">{t('home')}</Link></Button>
          </main>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
