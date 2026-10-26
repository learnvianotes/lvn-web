'use client'

import { Menu, X } from 'lucide-react'
import Link from 'next/link'
import { useEffect, useRef, useState } from 'react'
import { useSession } from '@/state/session'

/**
 * The public header's links on a phone. Named "Browse" so it is not the signed-in app's "Menu"
 * (Playwright treats accessible names as substrings).
 * Closed until asked for; from 768 px the same links sit in the header itself.
 */
export function PublicMenu({ labels }: { labels: { menu: string; close: string; features: string; subjects: string; community: string; resources: string; start: string } }) {
  const [open, setOpen] = useState(false)
  const signedIn = useSession((s) => s.status === 'signed-in')
  const panel = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!open) return
    panel.current?.querySelector('a')?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open])
  const item = 'rounded-lg px-3 py-2.5 text-sm font-medium text-fg hover:bg-surface-2'
  return (
    <div className="md:hidden">
      <button
        type="button"
        aria-expanded={open}
        aria-controls="site-menu"
        aria-label={open ? labels.close : labels.menu}
        onClick={() => setOpen((v) => !v)}
        className="inline-flex size-10 items-center justify-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg"
      >
        {open ? <X className="size-5" aria-hidden /> : <Menu className="size-5" aria-hidden />}
      </button>
      {open ? (
        <div ref={panel} id="site-menu" className="absolute inset-x-0 top-full z-40 border-b border-border bg-surface px-3 py-2 shadow-md">
          <nav aria-label={labels.menu} className="flex flex-col">
            <Link href="/#features" className={item} onClick={() => setOpen(false)}>
              {labels.features}
            </Link>
            <Link href="/subjects" className={item} onClick={() => setOpen(false)}>
              {labels.subjects}
            </Link>
            <Link href="/community" className={item} onClick={() => setOpen(false)}>
              {labels.community}
            </Link>
            <Link href="/resources" className={item} onClick={() => setOpen(false)}>
              {labels.resources}
            </Link>
            {signedIn ? null : (
              <Link href="/sign-up" className="mt-1 inline-flex h-10 items-center justify-center rounded-full bg-accent px-4 text-sm font-semibold text-accent-fg" onClick={() => setOpen(false)}>
                {labels.start}
              </Link>
            )}
          </nav>
        </div>
      ) : null}
    </div>
  )
}
