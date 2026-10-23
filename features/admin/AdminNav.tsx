'use client'

import { useQuery } from '@apollo/client/react'
import { BadgeCheck, PanelLeft, ShieldCheck, Sparkles, Trophy, X, type LucideIcon } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { ViewerDocument } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

export type AdminGroupKey = 'people' | 'content' | 'ai'

export type AdminSection = {
  href: string
  group: AdminGroupKey
  /** Key under adminNav.sections */
  key: 'verification' | 'moderation' | 'contests' | 'ai'
  icon: LucideIcon
}

/**
 * Every page under app/(site)/(app)/admin, in sidebar order. A unit test fails when a page is added there and left
 * out of this list, so the sidebar stays the whole admin area.
 */
export const ADMIN_SECTIONS: AdminSection[] = [
  { href: '/admin/verification', group: 'people', key: 'verification', icon: BadgeCheck },
  { href: '/admin/moderation', group: 'content', key: 'moderation', icon: ShieldCheck },
  { href: '/admin/contests', group: 'content', key: 'contests', icon: Trophy },
  { href: '/admin/ai', group: 'ai', key: 'ai', icon: Sparkles },
]

export const ADMIN_GROUP_ORDER: AdminGroupKey[] = ['people', 'content', 'ai']

/** The section this path belongs to: the page itself, or a page under it. */
export function activeAdminSection(pathname: string): AdminSection | undefined {
  return ADMIN_SECTIONS.find((section) => pathname === section.href || pathname.startsWith(`${section.href}/`))
}

/** The sidebar is chrome for platform admins. Each page still refuses everyone else, as it did before. */
export function canSeeAdminNav(role: string | null | undefined): boolean {
  return role === 'PLATFORM_ADMIN'
}

/**
 * The admin area's side navigation: every settings page, grouped, with the open one marked. From 1024 px it stays
 * on the left; below that it is a drawer opened from "Admin settings" (the app's own menu is separate).
 */
export function AdminNav() {
  const t = useTranslations('adminNav')
  const path = usePathname()
  const [open, setOpen] = useState(false)
  const openButton = useRef<HTMLButtonElement>(null)
  const closeButton = useRef<HTMLButtonElement>(null)
  const close = useCallback(() => {
    setOpen(false)
    openButton.current?.focus()
  }, [])
  useEffect(() => setOpen(false), [path])
  useEffect(() => {
    if (!open) return
    closeButton.current?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') close()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [open, close])

  return (
    <div>
      {/* The outer box is the grid cell (it stretches with the page). The inner one sticks below the top bar. */}
      <div className="lg:sticky lg:top-20 lg:max-h-[calc(100dvh-6rem)] lg:overflow-y-auto">
        <button
          ref={openButton}
          type="button"
          aria-expanded={open}
          onClick={() => setOpen(true)}
          className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface px-3 py-2 text-sm font-semibold hover:border-accent lg:hidden"
        >
          <PanelLeft className="size-4" aria-hidden />
          {t('open')}
        </button>
        <aside className="hidden lg:block">
          <SectionList pathname={path} idPrefix="admin-nav" />
        </aside>
      </div>
      {open ? (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label={t('label')}>
          <button type="button" aria-label={t('close')} className="absolute inset-0 bg-black/40" onClick={close} />
          <div id="admin-settings-drawer" className="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col gap-4 overflow-y-auto bg-surface px-3 py-4 shadow-2xl">
            <div className="flex items-center justify-between gap-3">
              <p className="px-2 text-sm font-semibold">{t('label')}</p>
              <button
                ref={closeButton}
                type="button"
                aria-label={t('close')}
                onClick={close}
                className="rounded-lg p-2 text-muted hover:bg-surface-2 hover:text-fg"
              >
                <X className="size-5" aria-hidden />
              </button>
            </div>
            <SectionList pathname={path} idPrefix="admin-drawer" onNavigate={close} />
          </div>
        </div>
      ) : null}
    </div>
  )
}

function SectionList({ pathname, idPrefix, onNavigate }: { pathname: string; idPrefix: string; onNavigate?: () => void }) {
  const t = useTranslations('adminNav')
  const active = activeAdminSection(pathname)
  return (
    <nav aria-label={t('label')} className="flex flex-col gap-4">
      {ADMIN_GROUP_ORDER.map((group) => (
        <div key={group} className="flex flex-col gap-0.5">
          <p id={`${idPrefix}-${group}`} className="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-muted">
            {t(`groups.${group}`)}
          </p>
          <ul aria-labelledby={`${idPrefix}-${group}`} className="flex flex-col gap-0.5">
            {ADMIN_SECTIONS.filter((section) => section.group === group).map((section) => {
              const Icon = section.icon
              const on = active?.href === section.href
              return (
                <li key={section.href}>
                  <Link
                    href={section.href}
                    aria-current={on ? 'page' : undefined}
                    onClick={onNavigate}
                    className={cn(
                      'flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium',
                      on ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-surface-2 hover:text-fg',
                    )}
                  >
                    <Icon className="size-[18px] shrink-0" aria-hidden />
                    {t(`sections.${section.key}`)}
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>
      ))}
    </nav>
  )
}

/**
 * Puts the sidebar beside admin pages for platform admins. Everyone else gets the page alone, so a refused visit
 * looks as it did before. Children stay in one place so the page does not remount when the viewer's role arrives.
 */
export function AdminShell({ children }: { children: ReactNode }) {
  const role = useQuery(ViewerDocument).data?.viewer?.globalRole
  const admin = canSeeAdminNav(role)
  return (
    <div className={admin ? 'flex flex-col gap-4 lg:grid lg:grid-cols-[14.5rem_minmax(0,1fr)] lg:gap-8' : undefined}>
      {admin ? <AdminNav /> : null}
      <div className={admin ? 'min-w-0' : undefined}>{children}</div>
    </div>
  )
}
