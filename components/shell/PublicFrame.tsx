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
 * session, without mounting the page again. The landing page keeps the visitor's frame: it is the way in. Someone
 * already signed in does not stay — the page sends them to Home.
 */
export function PublicFrame({ header, footer, children }: { header: ReactNode; footer: ReactNode; children: ReactNode }) {
  const signedIn = useSession((s) => s.status === 'signed-in')
  const path = usePathname()
  const app = signedIn && path !== '/'
  return (
    <AuthProvider>
      <AppShell footer={footer} visitor={app ? undefined : header}>
        {children}
        {app ? <SearchPalette /> : null}
      </AppShell>
    </AuthProvider>
  )
}
