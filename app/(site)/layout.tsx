import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { NextIntlClientProvider } from 'next-intl'
import { Analytics } from '@/components/analytics/Analytics'
import { UsageTracker } from '@/components/analytics/UsageTracker'
import { ReleaseLandingHold } from '@/components/landing/ReleaseLandingHold'
import { getLocale, getTranslations } from 'next-intl/server'
import { ThemeSync } from '@/components/theme/ThemeSync'
import { landingHoldScript } from '@/lib/auth/hint'
import { env } from '@/lib/env'
import { SITE_DESCRIPTION, SITE_KEYWORDS } from '@/lib/site'
import { PAPER, themeBootScript } from '@/lib/theme'
import '../globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' })
// Code only: not preloaded on every page, fetched where code is shown.
const jetbrains = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains', display: 'swap', preload: false })

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations('site')
  return {
    metadataBase: new URL(env.NEXT_PUBLIC_SITE_URL),
    title: { default: t('name'), template: `%s · ${t('name')}` },
    description: SITE_DESCRIPTION,
    keywords: [...SITE_KEYWORDS],
    applicationName: t('name'),
    openGraph: { siteName: t('name'), type: 'website', title: t('name'), description: SITE_DESCRIPTION },
    twitter: { card: 'summary', title: t('name'), description: SITE_DESCRIPTION },
    icons: {
      // The SVG is crisp at every size; PNGs cover browsers without SVG favicons. Rendered by branding/render-icons.mjs.
      icon: [
        { url: '/icons/logo.svg', type: 'image/svg+xml' },
        { url: '/icons/icon-32.png', sizes: '32x32', type: 'image/png' },
        { url: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
      ],
      apple: '/icons/apple-touch-icon.png',
    },
    robots: env.NEXT_PUBLIC_APP_ENV === 'production' ? undefined : { index: false, follow: false },
  }
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: PAPER.light },
    { media: '(prefers-color-scheme: dark)', color: PAPER.dark },
  ],
}

// Mode, accent, and the resolved scheme, before first paint.
const themeScript = themeBootScript()

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const locale = await getLocale()
  return (
    <html lang={locale} className={`${inter.variable} ${jetbrains.variable}`} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        {/* Hides `/` before first paint when this browser has signed in, so the landing page does not flash on the way to Home. */}
        <script dangerouslySetInnerHTML={{ __html: landingHoldScript() }} />
      </head>
      <body className="antialiased">
        <ReleaseLandingHold />
        <ThemeSync />
        <NextIntlClientProvider>
          {children}
          <Analytics />
          <UsageTracker />
        </NextIntlClientProvider>
      </body>
    </html>
  )
}
