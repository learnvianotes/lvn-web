'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import {
  Activity,
  Bookmark,
  BookOpen,
  CalendarDays,
  Compass,
  GraduationCap,
  House,
  Library,
  ListChecks,
  Menu,
  MessagesSquare,
  NotebookPen,
  Plus,
  Search,
  ShieldCheck,
  Sparkles,
  Trophy,
  Upload,
  Users,
  X,
  type LucideIcon,
} from 'lucide-react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState, type ReactNode, type RefObject } from 'react'
import { Logo } from '@/components/brand/Logo'
import { AppearanceMenu } from '@/components/theme/AppearanceMenu'
import { LimitNotice } from '@/components/ui/limit-notice'
import { NotificationBell } from '@/features/notifications/NotificationBell'
import { useReadPdf } from '@/features/reader/readPdf'
import { OPEN_SEARCH_EVENT } from '@/features/search/SearchPalette'
import { CreateNoteDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { canSeeAdminNav } from '@/features/admin/AdminNav'
import { isLimitCode, refusalMessage } from '@/lib/limit-error'
import { cn } from '@/lib/cn'
import { VerifyEmailBanner } from '@/components/auth/VerifyEmailBanner'
import { DeletionBanner } from '@/features/data/DeleteAccount'
import { useUploadsEnabled } from '@/features/notes/uploads'

type Entry = { href: string; key: string; icon: LucideIcon; match?: RegExp; staff?: boolean }

/**
 * Board A's left sidebar (lvn-backend ADR-0076): its Calendar is Exams, and its Quizzes and Contests are the weekly
 * contests and the quizzes waiting for the person (ADR-0082).
 */
const ENTRIES: Entry[] = [
  { href: '/home', key: 'home', icon: House },
  { href: '/notes', key: 'notes', icon: NotebookPen, match: /^\/notes(\/|$)/ },
  { href: '/search', key: 'explore', icon: Compass },
  { href: '/admin', key: 'admin', icon: ShieldCheck, match: /^\/admin(\/|$)/, staff: true },
  { href: '/subjects', key: 'subjects', icon: BookOpen, match: /^\/subjects(\/|$)/ },
  { href: '/groups', key: 'groups', icon: Users },
  { href: '/classes', key: 'classes', icon: GraduationCap },
  { href: '/exams', key: 'exams', icon: CalendarDays },
  { href: '/quizzes', key: 'quizzes', icon: ListChecks },
  { href: '/contests', key: 'contests', icon: Trophy, match: /^\/contests(\/|$)/ },
  { href: '/rhythm', key: 'rhythm', icon: Activity },
  { href: '/resources', key: 'resources', icon: Library },
  { href: '/community', key: 'community', icon: MessagesSquare },
  { href: '/ask', key: 'ask', icon: Sparkles },
  { href: '/saved', key: 'saved', icon: Bookmark },
]

/**
 * The signed-in app's frame: the sidebar from 1024 px (a drawer below), and the top bar with search, bell and avatar.
 * With `visitor` (a public page before or without a session) it is the visitor's header instead; the page sits at the
 * same place in both, so switching once the session is known never mounts it again (a page's state, such as an
 * unsubscribe link's answer, survives).
 */
export function AppShell({ children, footer, visitor }: { children: ReactNode; footer?: ReactNode; visitor?: ReactNode }) {
  const t = useTranslations('shell')
  const app = !visitor
  const [open, setOpen] = useState(false)
  const path = usePathname()
  // Admin keeps the top bar in the frame and scrolls the page under it. A sticky bar inside a document that also
  // overflows sideways is painted over the content (and over a full-page screenshot).
  const admin = path.startsWith('/admin')
  const menuButton = useRef<HTMLButtonElement>(null)
  const closeButton = useRef<HTMLButtonElement>(null)
  useEffect(() => setOpen(false), [path])
  useEffect(() => {
    if (!open) return
    const button = menuButton.current
    closeButton.current?.focus()
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    window.addEventListener('keydown', onKey)
    return () => {
      document.body.style.overflow = previous
      window.removeEventListener('keydown', onKey)
      button?.focus()
    }
  }, [open])
  return (
    <div className={cn('min-h-dvh', app && 'lg:grid lg:grid-cols-[15.5rem_minmax(0,1fr)]', admin && 'h-dvh max-h-dvh overflow-hidden')}>
      <a href="#main" className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-3 focus:z-50 focus:rounded-lg focus:bg-surface focus:px-3 focus:py-2">
        {t('skip')}
      </a>
      {app ? (
        <aside className="sticky top-0 hidden h-dvh flex-col gap-4 overflow-y-auto border-r border-border bg-surface px-3 py-4 lg:flex">
          <Brand />
          <Nav />
        </aside>
      ) : null}
      <div className={cn('flex min-w-0 flex-col', admin && 'h-dvh max-h-dvh min-h-0 overflow-hidden')}>
        {app ? <TopBar menuButton={menuButton} open={open} onMenu={() => setOpen(true)} pinned={admin} /> : visitor}
        {app ? <VerifyEmailBanner /> : null}
        {app ? <DeletionBanner /> : null}
        <main
          id="main"
          className={
            app
              ? cn('mx-auto w-full min-w-0 flex-1 px-4 py-6 sm:px-6 sm:py-8', admin ? 'max-w-none overflow-y-auto' : 'min-h-[70dvh] max-w-6xl')
              : 'min-h-[70dvh]'
          }
        >
          {children}
          {admin ? footer : null}
        </main>
        {admin ? null : footer}
      </div>
      {app && open ? (
        <div className="fixed inset-0 z-50 lg:hidden" role="dialog" aria-modal="true" aria-label={t('menu')}>
          <button type="button" aria-label={t('close')} className="absolute inset-0 bg-black/40" onClick={() => setOpen(false)} />
          <div className="absolute inset-y-0 left-0 flex w-72 max-w-[85vw] flex-col gap-4 overflow-y-auto bg-surface px-3 py-4 shadow-2xl">
            <div className="flex items-center justify-between">
              <Brand />
              <button ref={closeButton} type="button" aria-label={t('close')} onClick={() => setOpen(false)} className="inline-flex size-10 items-center justify-center rounded-lg text-muted hover:bg-surface-2">
                <X className="size-5" aria-hidden />
              </button>
            </div>
            <Nav />
          </div>
        </div>
      ) : null}
    </div>
  )
}

function Brand() {
  const t = useTranslations('site')
  return (
    <Link href="/home" aria-label={t('name')} className="flex items-center gap-2 px-2 text-lg font-extrabold tracking-tight">
      <Logo size={30} />
      <span aria-hidden>
        {t('wordmark.lead')}
        <span className="text-accent">{t('wordmark.accent')}</span>
      </span>
    </Link>
  )
}

/** The sidebar's entries, Upload and Create Note. */
function Nav() {
  const t = useTranslations('shell')
  const path = usePathname()
  const router = useRouter()
  const viewer = useQuery(ViewerDocument).data?.viewer
  const entries = ENTRIES.filter((entry) => !entry.staff || canSeeAdminNav(viewer?.globalRole, { verified: viewer?.verified }))
  const readPdf = useReadPdf()
  const pdf = useRef<HTMLInputElement>(null)
  // Upload (read a PDF) only while uploads are on (lvn-backend ADR-0097).
  const uploadsOn = useUploadsEnabled()
  const [create, creating] = useMutation(CreateNoteDocument)
  const [createError, setCreateError] = useState<{ message: string; limit: boolean } | null>(null)
  const newNote = async () => {
    setCreateError(null)
    try {
      const res = await create({ variables: { input: {} } })
      const problem = res.data?.createNote.userErrors[0]
      const id = res.data?.createNote.note?.id
      if (id) router.push(`/notes/${id}`)
      else setCreateError({ message: problem?.message ?? t('createFailed'), limit: isLimitCode(problem?.code) })
    } catch (error) {
      const refused = refusalMessage(error)
      setCreateError({ message: refused ?? t('createFailed'), limit: !!refused })
    }
  }
  return (
    <nav aria-label={t('nav')} className="flex flex-1 flex-col gap-1">
      {entries.map(({ href, key, icon: Icon, match }) => {
        const active = match ? match.test(path) : path === href || path.startsWith(`${href}/`)
        return (
          <Link key={key} href={href} aria-current={active ? 'page' : undefined} className={cn('flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium', active ? 'bg-accent-soft text-accent' : 'text-muted hover:bg-surface-2 hover:text-fg')}>
            <Icon className="size-[18px] shrink-0" aria-hidden />
            {t(`entries.${key}`)}
          </Link>
        )
      })}
      <div className="mt-auto flex flex-col gap-1 pt-4">
        {uploadsOn ? (
          <>
        <input
          ref={pdf}
          type="file"
          accept="application/pdf"
          className="sr-only"
          aria-hidden
          tabIndex={-1}
          onChange={(e) => {
            const file = e.target.files?.[0]
            e.target.value = ''
            if (file) void readPdf.start(file)
          }}
        />
        <button type="button" onClick={() => pdf.current?.click()} disabled={readPdf.uploading !== null} className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg">
          <Upload className="size-[18px]" aria-hidden />
          {readPdf.uploading !== null ? t('uploading') : t('upload')}
        </button>
        {readPdf.error ? (
          readPdf.limit ? (
            <LimitNotice>{readPdf.error}</LimitNotice>
          ) : (
            <p role="alert" className="px-3 text-xs text-bad">
              {readPdf.error}
            </p>
          )
        ) : null}
        {createError ? (
          createError.limit ? (
            <LimitNotice>{createError.message}</LimitNotice>
          ) : (
            <p role="alert" className="px-3 text-xs text-bad">
              {createError.message}
            </p>
          )
        ) : null}
          </>
        ) : null}
        <button type="button" onClick={() => void newNote()} disabled={creating.loading} className="mt-1 flex min-h-10 items-center justify-center gap-2 rounded-xl bg-accent px-3 py-2.5 text-sm font-semibold text-accent-fg hover:bg-[var(--accent-hover)]">
          <Plus className="size-4" aria-hidden />
          {t('createNote')}
        </button>
      </div>
    </nav>
  )
}

/** The top bar: the menu (below 1024 px), search (opens the palette), appearance, the bell and the avatar. */
function TopBar({ onMenu, open, menuButton, pinned }: { onMenu: () => void; open: boolean; menuButton: RefObject<HTMLButtonElement | null>; pinned?: boolean }) {
  const t = useTranslations('shell')
  const router = useRouter()
  const viewer = useQuery(ViewerDocument).data?.viewer
  return (
    <header className={cn('z-30 shrink-0 border-b border-border bg-bg/85 pt-[env(safe-area-inset-top)] backdrop-blur supports-[backdrop-filter]:bg-bg/70', pinned ? 'relative' : 'sticky top-0')}>
      <div className={cn('mx-auto flex h-14 min-w-0 items-center gap-1 px-3 sm:gap-2 sm:px-4', pinned ? 'max-w-none' : 'max-w-6xl')}>
        <button ref={menuButton} type="button" aria-label={t('menu')} aria-expanded={open} onClick={onMenu} className="grid size-11 shrink-0 place-items-center rounded-lg text-muted hover:bg-surface-2 hover:text-fg lg:hidden">
          <Menu className="size-5" aria-hidden />
        </button>
        <button
          type="button"
          aria-label={t('search')}
          onClick={() => {
            // The palette on the page takes the event; without one, the search page.
            if (window.dispatchEvent(new Event(OPEN_SEARCH_EVENT, { cancelable: true }))) router.push('/search')
          }}
          className="flex h-11 min-w-0 flex-1 items-center gap-2 rounded-full border border-border bg-surface px-3 text-left text-sm text-muted hover:border-accent sm:max-w-xl"
        >
          <Search className="size-4 shrink-0" aria-hidden />
          <span className="truncate">{t('searchPlaceholder')}</span>
          <kbd className="ml-auto hidden rounded border border-border px-1.5 text-[10px] sm:inline">Ctrl K</kbd>
        </button>
        <div className="ml-auto flex shrink-0 items-center gap-0.5">
          <AppearanceMenu />
          <NotificationBell />
          <Link href="/profile" aria-label={t('account')} className="ml-1 grid size-9 place-items-center rounded-full bg-accent-soft text-sm font-bold text-accent hover:ring-2 hover:ring-accent/40">
            {(viewer?.displayName ?? '?').slice(0, 1).toUpperCase()}
          </Link>
        </div>
      </div>
    </header>
  )
}
