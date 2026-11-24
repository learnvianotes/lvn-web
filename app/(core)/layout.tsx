import type { Metadata, Viewport } from 'next'
import { APP_NAME } from '@core/config'
import { env } from '@/lib/env'
import { SITE_DESCRIPTION, SITE_KEYWORDS } from '@/lib/site'
import { PAPER, themeBootScript } from '@/lib/theme'
// The old site's global styles, in its order; feature styles are imported by their components.
import '@tabler/icons-webfont/dist/tabler-icons.min.css'
import '@core/shared/styles/base.css'
import '@core/shared/styles/layout.css'
import '@core/shared/styles/components.css'
import '@core/shared/styles/prose.css'

/**
 * Root layout of /core: the old site's index.html (lvn-backend ADR-0002). /core has its own root
 * layout so none of the new site's styles reach it — moving between / and /core is a full page load.
 */

export const metadata: Metadata = {
  metadataBase: new URL(env.NEXT_PUBLIC_SITE_URL),
  title: APP_NAME,
  description: SITE_DESCRIPTION,
  keywords: [...SITE_KEYWORDS],
  applicationName: APP_NAME,
  appleWebApp: { capable: true, title: APP_NAME, statusBarStyle: 'default' },
  other: { 'mobile-web-app-capable': 'yes' },
  openGraph: { siteName: APP_NAME, type: 'website', title: APP_NAME, description: SITE_DESCRIPTION },
  twitter: { card: 'summary', title: APP_NAME, description: SITE_DESCRIPTION },
  icons: {
    icon: [
      { url: '/icons/icon-16.png', sizes: '16x16', type: 'image/png' },
      { url: '/icons/icon-32.png', sizes: '32x32', type: 'image/png' },
      { url: '/icons/icon-192.png', sizes: '192x192', type: 'image/png' },
    ],
    apple: { url: '/icons/apple-touch-icon.png', sizes: '180x180' },
  },
  robots: env.NEXT_PUBLIC_APP_ENV === 'production' ? undefined : { index: false, follow: false },
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

// Same pre-paint script as the product site, so accent and mode survive a full load into /core.
const themeScript = themeBootScript()

// Launch splash: shown only while the app is actually loading (removed by core-app/src/app/splash.ts).
// Inner HTML, so React never owns the nodes the app removes.
const splash = `<div id="splash" role="status" aria-label="Loading ${APP_NAME}">
  <div class="splash-mark">
    <img src="/icons/icon-192.png" alt="" width="64" height="64" />
  </div>
  <div class="splash-name">${APP_NAME}</div>
  <p class="splash-status">Opening notes…</p>
  <div class="splash-bar"><span></span></div>
</div>
<style>
  #splash { position: fixed; inset: 0; z-index: 1000; display: grid; place-content: center; justify-items: center; gap: 12px;
    background: #f8f7f4; color: #1c1b18; font: 500 17px/1.2 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
    transition: opacity .2s cubic-bezier(.22,1,.36,1), visibility .2s; }
  [data-theme='dark'] #splash { background: #141413; color: #ecebe6; }
  #splash.is-done { opacity: 0; visibility: hidden; }
  .splash-mark { width: 64px; height: 64px; animation: splash-in .32s cubic-bezier(.22,1,.36,1) both; }
  .splash-mark img { border-radius: 14px; }
  .splash-name { animation: splash-in .32s .05s cubic-bezier(.22,1,.36,1) both; }
  .splash-status { margin: 0; font-size: 14px; font-weight: 400; color: #66625b; animation: splash-in .32s .1s cubic-bezier(.22,1,.36,1) both; }
  [data-theme='dark'] .splash-status { color: #9a968d; }
  .splash-bar { width: 120px; height: 4px; border-radius: 4px; overflow: hidden; background: rgb(28 27 24 / .08); animation: splash-in .32s .1s both; }
  [data-theme='dark'] .splash-bar { background: rgb(236 235 230 / .1); }
  .splash-bar span { display: block; width: 40%; height: 100%; border-radius: 4px; background: #f2c230; animation: splash-slide 1.1s cubic-bezier(.22,1,.36,1) infinite; }
  @keyframes splash-in { from { opacity: 0; transform: translateY(8px); } }
  @keyframes splash-slide { from { transform: translateX(-110%); } to { transform: translateX(260%); } }
  @media (prefers-reduced-motion: reduce) { #splash * { animation: none !important; } }
</style>`

export default function CoreLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* The reader's fonts (IBM Plex Sans, JetBrains Mono), loaded the same way: its CSS names the families directly. */}
        {/* eslint-disable-next-line @next/next/no-page-custom-font -- this is the /core root layout */}
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <div dangerouslySetInnerHTML={{ __html: splash }} />
        <div id="root">{children}</div>
      </body>
    </html>
  )
}
