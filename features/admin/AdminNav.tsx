'use client'

import { useQuery } from '@apollo/client/react'
import { Activity, BadgeCheck, Bug, Building2, IdCard, KeyRound, LayoutDashboard, PanelLeft, ScrollText, ShieldCheck, SlidersHorizontal, Sparkles, Trophy, UserCog, Users, Wallet, X, type LucideIcon } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { AdminMfaGate } from '@/features/admin/AdminMfa'
import { MfaStatusDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { ADMIN_VERIFY_PATH, isAdminMfaRole, isMfaRequiredError, isUnknownMfaField, noteSessionMfa } from '@/lib/auth/mfa'
import { cn } from '@/lib/cn'
import { useSession } from '@/state/session'

export type AdminGroupKey = 'platform' | 'people' | 'content' | 'ai'

export type StaffRole = 'PLATFORM_ADMIN' | 'MANAGER' | 'TEACHER'

export type AdminSectionKey = 'overview' | 'settings' | 'plans' | 'errors' | 'usage' | 'activity' | 'access' | 'users' | 'roles' | 'domains' | 'verification' | 'studentId' | 'moderation' | 'contests' | 'ai'

/** Routes under /admin that are not settings sections. The code screen is one of them. */
export const ADMIN_GATE_ROUTES = ['/admin/verify'] as const

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
/** Proof of study and college IDs. Verified teachers are added in sectionsForRole; managers are not. */
const REVIEW: readonly StaffRole[] = ['PLATFORM_ADMIN']

type ReviewOpts = { verified?: boolean | null }

/**
 * Every settings page under app/(site)/(app)/admin, in sidebar order. A unit test fails when a page is added there
 * and left out of this list, so the sidebar stays the whole admin area. ADMIN_GATE_ROUTES are the exception: the
 * email-code screen is a gate, not a section.
 */
export const ADMIN_SECTIONS: AdminSection[] = [
  { href: '/admin', group: 'platform', key: 'overview', icon: LayoutDashboard, roles: ADMIN },
  { href: '/admin/settings', group: 'platform', key: 'settings', icon: SlidersHorizontal, roles: ADMIN },
  { href: '/admin/plans', group: 'platform', key: 'plans', icon: Wallet, roles: ADMIN },
  { href: '/admin/errors', group: 'platform', key: 'errors', icon: Bug, roles: ADMIN },
  { href: '/admin/usage', group: 'platform', key: 'usage', icon: Activity, roles: ADMIN },
  { href: '/admin/activity', group: 'platform', key: 'activity', icon: ScrollText, roles: ADMIN },
  { href: '/admin/access', group: 'people', key: 'access', icon: KeyRound, roles: ADMIN },
  { href: '/admin/users', group: 'people', key: 'users', icon: Users, roles: ADMIN },
  { href: '/admin/roles', group: 'people', key: 'roles', icon: UserCog, roles: ADMIN },
  { href: '/admin/domains', group: 'people', key: 'domains', icon: Building2, roles: ADMIN },
  { href: '/admin/verification', group: 'people', key: 'verification', icon: BadgeCheck, roles: REVIEW },
  { href: '/admin/student-id', group: 'people', key: 'studentId', icon: IdCard, roles: REVIEW },
  { href: '/admin/moderation', group: 'content', key: 'moderation', icon: ShieldCheck, roles: ADMIN },
  { href: '/admin/contests', group: 'content', key: 'contests', icon: Trophy, roles: ADMIN },
  { href: '/admin/ai', group: 'ai', key: 'ai', icon: Sparkles, roles: ADMIN },
]

/**
 * Sections this role may open. Students and signed-out visitors get none.
 * Verification and college ID queues are for platform admins and verified teachers only.
 */
export function sectionsForRole(role: string | null | undefined, opts?: ReviewOpts): AdminSection[] {
  if (role !== 'PLATFORM_ADMIN' && role !== 'MANAGER' && role !== 'TEACHER') return []
  const review = role === 'PLATFORM_ADMIN' || (role === 'TEACHER' && opts?.verified === true)
  return ADMIN_SECTIONS.filter((section) => {
    if (section.key === 'verification' || section.key === 'studentId') return review
    return section.roles.includes(role)
  })
}

export function canSeeSection(role: string | null | undefined, key: AdminSectionKey, opts?: ReviewOpts): boolean {
  return sectionsForRole(role, opts).some((section) => section.key === key)
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
export function canSeeAdminNav(role: string | null | undefined, opts?: ReviewOpts): boolean {
  return sectionsForRole(role, opts).length > 0
}

/**
 * The admin area's side navigation: every settings page, grouped, with the open one marked. From 1024 px it stays
 * on the left; below that it is a drawer opened from "Admin settings" (the app's own menu is separate).
 */
export function AdminNav({ role, verified }: { role?: string | null; verified?: boolean | null }) {
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
          <SectionList pathname={path} idPrefix="admin-nav" role={role} verified={verified} />
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
            <SectionList pathname={path} idPrefix="admin-drawer" onNavigate={close} role={role} verified={verified} />
          </div>
        </div>
      ) : null}
    </div>
  )
}

function SectionList({ pathname, idPrefix, onNavigate, role, verified }: { pathname: string; idPrefix: string; onNavigate?: () => void; role?: string | null; verified?: boolean | null }) {
  const t = useTranslations('adminNav')
  const active = activeAdminSection(pathname)
  const sections = role === undefined ? ADMIN_SECTIONS : sectionsForRole(role, { verified })
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
  const t = useTranslations('adminMfa')
  const pathname = usePathname()
  const viewerQuery = useQuery(ViewerDocument)
  const viewer = viewerQuery.data?.viewer
  const role = viewer?.globalRole
  const mfaRole = isAdminMfaRole(role)
  const pending = useSession((state) => state.mfaPending)
  const verifiedLocally = useSession((state) => state.mfaVerified)
  const mfa = useQuery(MfaStatusDocument, { skip: !mfaRole })
  const admin = canSeeAdminNav(role, { verified: viewer?.verified })
  const status = mfa.data?.mfaStatus
  const needsCode = mfaRole && !verifiedLocally && (pending || isMfaRequiredError(mfa.error) || Boolean(status && status.required && !status.satisfied))
  const unknown = isUnknownMfaField(mfa.error)
  const waitingOnVerify = pathname === ADMIN_VERIFY_PATH && (viewerQuery.loading && !viewerQuery.data || (mfaRole && mfa.loading && !status && !mfa.error))
  const gate = (needsCode && !unknown) || waitingOnVerify

  useEffect(() => {
    if (role && useSession.getState().role !== role) useSession.setState({ role })
  }, [role])

  useEffect(() => {
    if (status && (!status.required || status.satisfied)) noteSessionMfa(role, false)
  }, [status, role])

  return (
    <div className={admin && !gate ? 'flex flex-col gap-4 lg:grid lg:grid-cols-[14.5rem_minmax(0,1fr)] lg:gap-8' : undefined}>
      {admin && !gate ? <AdminNav role={role} verified={viewer?.verified} /> : null}
      <div className={admin && !gate ? 'min-w-0' : undefined}>
        {gate ? (needsCode && !unknown ? <AdminMfaGate /> : <p role="status" className="text-sm text-muted">{t('checking')}</p>) : children}
      </div>
    </div>
  )
}
