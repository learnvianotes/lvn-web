'use client'

import { useQuery } from '@apollo/client/react'
import { Activity, BadgeCheck, Bug, Building2, IdCard, KeyRound, LayoutDashboard, PanelLeft, ShieldCheck, SlidersHorizontal, Sparkles, Trophy, UserCog, Wallet, X, type LucideIcon } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { ViewerDocument } from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'

export type AdminGroupKey = 'platform' | 'people' | 'content' | 'ai'

export type StaffRole = 'PLATFORM_ADMIN' | 'MANAGER' | 'TEACHER'

export type AdminSectionKey = 'overview' | 'settings' | 'plans' | 'errors' | 'usage' | 'access' | 'roles' | 'domains' | 'verification' | 'studentId' | 'moderation' | 'contests' | 'ai'

export type AdminSection = {
  href: string
  group: AdminGroupKey
  /** Key under adminNav.sections */
  key: AdminSectionKey
  icon: LucideIcon
  /** Who may open this page. The API still enforces the same rule. */
  roles: readonly StaffRole[]
}

const ADMIN: readonly StaffRole[] = ['PLATFORM_ADMIN']
const REVIEW: readonly StaffRole[] = ['PLATFORM_ADMIN', 'MANAGER', 'TEACHER']
const OPS: readonly StaffRole[] = ['PLATFORM_ADMIN', 'MANAGER']

/**
 * Every page under app/(site)/(app)/admin, in sidebar order. A unit test fails when a page is added there and left
 * out of this list, so the sidebar stays the whole admin area.
 */
export const ADMIN_SECTIONS: AdminSection[] = [
  { href: '/admin', group: 'platform', key: 'overview', icon: LayoutDashboard, roles: ADMIN },
  { href: '/admin/settings', group: 'platform', key: 'settings', icon: SlidersHorizontal, roles: ADMIN },
  { href: '/admin/plans', group: 'platform', key: 'plans', icon: Wallet, roles: ADMIN },
  { href: '/admin/errors', group: 'platform', key: 'errors', icon: Bug, roles: OPS },
  { href: '/admin/usage', group: 'platform', key: 'usage', icon: Activity, roles: OPS },
  { href: '/admin/access', group: 'people', key: 'access', icon: KeyRound, roles: ADMIN },
  { href: '/admin/roles', group: 'people', key: 'roles', icon: UserCog, roles: ADMIN },
  { href: '/admin/domains', group: 'people', key: 'domains', icon: Building2, roles: ADMIN },
  { href: '/admin/verification', group: 'people', key: 'verification', icon: BadgeCheck, roles: REVIEW },
  { href: '/admin/student-id', group: 'people', key: 'studentId', icon: IdCard, roles: REVIEW },
  { href: '/admin/moderation', group: 'content', key: 'moderation', icon: ShieldCheck, roles: ADMIN },
  { href: '/admin/contests', group: 'content', key: 'contests', icon: Trophy, roles: ADMIN },
  { href: '/admin/ai', group: 'ai', key: 'ai', icon: Sparkles, roles: ADMIN },
]

/** Sections this role may open. Students and signed-out visitors get none. */
export function sectionsForRole(role: string | null | undefined): AdminSection[] {
  if (role !== 'PLATFORM_ADMIN' && role !== 'MANAGER' && role !== 'TEACHER') return []
  return ADMIN_SECTIONS.filter((section) => section.roles.includes(role))
}

export function canSeeSection(role: string | null | undefined, key: AdminSectionKey): boolean {
  return sectionsForRole(role).some((section) => section.key === key)
}

export const ADMIN_GROUP_ORDER: AdminGroupKey[] = ['platform', 'people', 'content', 'ai']

/**
 * The section this path belongs to. Overview is only `/admin` itself; a longer path wins when several could match.
 */
export function activeAdminSection(pathname: string): AdminSection | undefined {
  return ADMIN_SECTIONS.filter((section) => (section.href === '/admin' ? pathname === '/admin' : pathname === section.href || pathname.startsWith(`${section.href}/`))).sort(
    (a, b) => b.href.length - a.href.length,
  )[0]
}

/** The admin area is for platform admins, managers and teachers. Each role only sees its sections. */
export function canSeeAdminNav(role: string | null | undefined): boolean {
  return sectionsForRole(role).length > 0
}

/**
 * The admin area's side navigation: every settings page, grouped, with the open one marked. From 1024 px it stays
 * on the left; below that it is a drawer opened from "Admin settings" (the app's own menu is separate).
 */
export function AdminNav({ role }: { role?: string | null }) {
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
      <div className="lg:sticky lg:top-0 lg:max-h-[calc(100dvh-7.5rem)] lg:overflow-y-auto">
        <button
          ref={openButton}
          type="button"
          aria-expanded={open}
          onClick={() => setOpen(true)}
          className="inline-flex min-h-11 items-center gap-2 rounded-xl border border-border bg-surface px-3 text-sm font-semibold hover:border-accent lg:hidden"
        >
          <PanelLeft className="size-4" aria-hidden />
          {t('open')}
        </button>
        <aside className="hidden lg:block">
          <SectionList pathname={path} idPrefix="admin-nav" role={role} />
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
            <SectionList pathname={path} idPrefix="admin-drawer" onNavigate={close} role={role} />
          </div>
        </div>
      ) : null}
    </div>
  )
}

function SectionList({ pathname, idPrefix, onNavigate, role }: { pathname: string; idPrefix: string; onNavigate?: () => void; role?: string | null }) {
  const t = useTranslations('adminNav')
  const active = activeAdminSection(pathname)
  const sections = role === undefined ? ADMIN_SECTIONS : sectionsForRole(role)
  return (
    <nav aria-label={t('label')} className="flex flex-col gap-4">
      {ADMIN_GROUP_ORDER.map((group) => {
        const items = sections.filter((section) => section.group === group)
        if (!items.length) return null
        return (
        <div key={group} className="flex flex-col gap-0.5">
          <p id={`${idPrefix}-${group}`} className="px-3 pb-1 text-xs font-semibold uppercase tracking-wide text-muted">
            {t(`groups.${group}`)}
          </p>
          <ul aria-labelledby={`${idPrefix}-${group}`} className="flex flex-col gap-0.5">
            {items.map((section) => {
              const Icon = section.icon
              const on = active?.href === section.href
              return (
                <li key={section.href}>
                  <Link
                    href={section.href}
                    aria-current={on ? 'page' : undefined}
                    onClick={onNavigate}
                    className={cn(
                      'flex min-h-11 items-center gap-3 rounded-xl px-3 py-2 text-left text-sm font-medium',
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
        )
      })}
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
      {admin ? <AdminNav role={role} /> : null}
      <div className={admin ? 'min-w-0' : undefined}>{children}</div>
    </div>
  )
}
