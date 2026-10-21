import type { Metadata, Viewport } from 'next'
import { APP_NAME } from '@core/config'
import { SITE_DESCRIPTION } from '@core/app/title'
import { env } from '@/lib/env'
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
  applicationName: APP_NAME,
  appleWebApp: { capable: true, title: APP_NAME, statusBarStyle: 'default' },
  other: { 'mobile-web-app-capable': 'yes' },
  openGraph: { siteName: APP_NAME },
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
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#17171a' },
  ],
}

// Apply the saved theme before first paint (no flash).
const themeScript = `try{var t=JSON.parse(localStorage.getItem('cnote:theme'));if(t!=='light'&&t!=='dark')t=matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light';document.documentElement.setAttribute('data-theme',t)}catch(e){}`

// Launch splash: shown only while the app is actually loading (removed by core-app/src/app/splash.ts).
// Inner HTML, so React never owns the nodes the app removes.
const splash = `<div id="splash" role="status" aria-label="Loading ${APP_NAME}">
  <div class="splash-mark">
    <span class="splash-glow"></span>
    <img src="/icons/icon-192.png" alt="" width="72" height="72" />
  </div>
  <div class="splash-name">${APP_NAME}</div>
  <div class="splash-bar"><span></span></div>
</div>
<style>
  #splash { position: fixed; inset: 0; z-index: 1000; display: grid; place-content: center; justify-items: center; gap: 14px;
    background: #f7f7f8; color: #18181b; font: 600 17px/1.2 Inter, system-ui, -apple-system, 'Segoe UI', sans-serif; letter-spacing: -0.01em;
    transition: opacity .18s ease, visibility .18s; }
  [data-theme='dark'] #splash { background: #0e0e10; color: #f4f4f5; }
  #splash.is-done { opacity: 0; visibility: hidden; }
  .splash-mark { position: relative; width: 72px; height: 72px; animation: splash-in .4s cubic-bezier(.2,.8,.2,1) both; }
  .splash-mark img { position: relative; border-radius: 18px; box-shadow: 0 10px 30px -10px rgb(37 99 235 / .45); animation: splash-float 1.6s ease-in-out infinite; }
  .splash-glow { position: absolute; inset: -18px; border-radius: 50%; background: radial-gradient(circle, rgb(37 99 235 / .22), transparent 70%); animation: splash-pulse 1.6s ease-in-out infinite; }
  .splash-name { animation: splash-in .4s .06s cubic-bezier(.2,.8,.2,1) both; }
  .splash-bar { width: 120px; height: 3px; border-radius: 3px; overflow: hidden; background: rgb(127 127 127 / .18); animation: splash-in .4s .1s both; }
  .splash-bar span { display: block; width: 40%; height: 100%; border-radius: 3px; background: linear-gradient(90deg, #2563eb, #60a5fa); animation: splash-slide 1s ease-in-out infinite; }
  @keyframes splash-in { from { opacity: 0; transform: translateY(6px) scale(.97); } }
  @keyframes splash-float { 50% { transform: translateY(-4px); } }
  @keyframes splash-pulse { 50% { transform: scale(1.12); opacity: .6; } }
  @keyframes splash-slide { from { transform: translateX(-110%); } to { transform: translateX(260%); } }
  @media (prefers-reduced-motion: reduce) { #splash * { animation: none !important; } }
</style>`

export default function CoreLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        {/* The old site's fonts, loaded the same way: its CSS names the families directly. */}
        {/* eslint-disable-next-line @next/next/no-page-custom-font -- this is the /core root layout */}
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>
        <div dangerouslySetInnerHTML={{ __html: splash }} />
        <div id="root">{children}</div>
      </body>
    </html>
  )
}
