'use client'

import { usePathname } from 'next/navigation'
import type { ReactNode } from 'react'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { SearchPalette } from '@/features/search/SearchPalette'
import { useSession } from '@/state/session'
import { AppShell } from './AppShell'

/**
 * The frame of public pages: the visitor's header, or, for someone signed in, board A's sidebar and top bar as on
 * signed-in pages (lvn-backend ADR-0076), so the catalogue, a resource, a public note or a profile never drops them out
 * of the app. The server renders the visitor's frame (public pages stay static); the tab switches once it knows the
 * session. The landing page keeps the visitor's frame: it is the way in.
 */
export function PublicFrame({ skip, header, footer, children }: { skip: string; header: ReactNode; footer: ReactNode; children: ReactNode }) {
  const signedIn = useSession((s) => s.status === 'signed-in')
  const path = usePathname()
  return (
    <AuthProvider>
      {signedIn && path !== '/' ? (
        <AppShell footer={footer}>
          {children}
          <SearchPalette />
        </AppShell>
      ) : (
        <>
          <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-3 focus:py-2">
            {skip}
          </a>
          {header}
          <main id="main" className="min-h-[70dvh]">
            {children}
          </main>
          {footer}
        </>
      )}
    </AuthProvider>
  )
}
