'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { Check, Copy, GitFork, Globe, Handshake, Lock, Share2, UserPlus, Users, X } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import {
  ChangeNoteVisibilityDocument,
  ForkNoteDocument,
  NoteSharesDocument,
  SetNoteForkingDocument,
  SetNoteSharedWithConnectionsDocument,
  ShareNoteDocument,
  UnshareNoteDocument,
  type NoteShareRole,
  type Visibility,
} from '@/graphql/generated/graphql'
import { cn } from '@/lib/cn'
import { publicNotePath } from '@/features/public-notes/paths'
import type { NoteMeta } from './api'
import { accentOf } from './look'

const VISIBILITIES: { value: Visibility; icon: typeof Lock }[] = [
  { value: 'PRIVATE', icon: Lock },
  { value: 'SHARED', icon: Users },
  { value: 'PUBLIC', icon: Globe },
]

/** What went wrong, in the server's words: refusals (FORBIDDEN) arrive as errors, invalid input as userErrors (§6.2). */
function problemOf(error: unknown, payload: { userErrors: { message: string }[] } | null | undefined, fallback: string) {
  if (CombinedGraphQLErrors.is(error)) return error.errors[0]?.message ?? fallback
  return error ? fallback : (payload?.userErrors[0]?.message ?? null)
}

async function attempt<T>(run: () => Promise<T>): Promise<{ result: T | null; error: unknown }> {
  try {
    return { result: await run(), error: null }
  } catch (error) {
    return { result: null, error }
  }
}

/** Who can read a note (§4.2, §4.4): only the owner, the people it is shared with, or everyone; and whether others may copy it. */
export function ShareDialog({ meta, open, onClose, onSaved }: { meta: NoteMeta; open: boolean; onClose: () => void; onSaved: (meta: NoteMeta) => void }) {
  const t = useTranslations('notes.share')
  const shares = useQuery(NoteSharesDocument, { variables: { id: meta.id }, skip: !open, fetchPolicy: 'cache-and-network' })
  const [changeVisibility, changing] = useMutation(ChangeNoteVisibilityDocument)
  const [share, sharing] = useMutation(ShareNoteDocument)
  const [unshare] = useMutation(UnshareNoteDocument)
  const [setForking, settingForking] = useMutation(SetNoteForkingDocument)
  const [setConnections, settingConnections] = useMutation(SetNoteSharedWithConnectionsDocument)
  const teacher = shares.data?.viewer?.globalRole === 'TEACHER'
  const withConnections = shares.data?.note?.sharedWithConnections ?? false
  const [person, setPerson] = useState('')
  const [role, setRole] = useState<NoteShareRole>('VIEWER')
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const people = shares.data?.note?.shares ?? []
  // Public notes have their own page anyone can open; shared ones open in the app for the people they are shared with.
  const link = typeof window === 'undefined' ? '' : `${window.location.origin}${meta.visibility === 'PUBLIC' ? publicNotePath(meta) : `/notes/${meta.id}`}`

  const pickVisibility = async (visibility: Visibility) => {
    if (visibility === meta.visibility) return
    setError(null)
    const { result, error } = await attempt(() => changeVisibility({ variables: { noteId: meta.id, visibility } }))
    const payload = result?.data?.changeNoteVisibility
    if (payload?.note) onSaved(payload.note)
    setError(problemOf(error, payload, t('failed')))
  }
  const add = async (who: string, as: NoteShareRole) => {
    setError(null)
    const { result, error } = await attempt(() => share({ variables: { noteId: meta.id, person: who.trim(), role: as } }))
    const payload = result?.data?.shareNote
    if (payload?.note) {
      onSaved(payload.note)
      setPerson('')
    }
    setError(problemOf(error, payload, t('failed')))
  }
  const remove = async (userId: string) => {
    setError(null)
    const { result, error } = await attempt(() => unshare({ variables: { noteId: meta.id, userId } }))
    setError(problemOf(error, result?.data?.unshareNote, t('failed')))
  }
  /** Teachers share with all their connections at once, and new connections get it too (lvn-backend ADR-0044). */
  const toggleConnections = async () => {
    setError(null)
    const { result, error } = await attempt(() => setConnections({ variables: { noteId: meta.id, shared: !withConnections } }))
    const payload = result?.data?.setNoteSharedWithConnections
    const problem = problemOf(error, payload, t('failed'))
    if (problem) return setError(problem)
    if (payload?.note) onSaved({ ...meta, visibility: payload.note.visibility })
    await shares.refetch()
  }

  const toggleForking = async () => {
    setError(null)
    const { result, error } = await attempt(() => setForking({ variables: { noteId: meta.id, enabled: !meta.forkingEnabled } }))
    const payload = result?.data?.setNoteForking
    if (payload?.note) onSaved(payload.note)
    setError(problemOf(error, payload, t('failed')))
  }
  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(link)
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    } catch {
      window.prompt(t('copyLink'), link)
    }
  }

  return (
    <Dialog open={open} onClose={onClose} title={t('title')}>
      <div className="flex flex-col gap-5">
        <fieldset className="flex flex-col gap-2" disabled={changing.loading}>
          <legend className="pb-2 text-sm font-semibold">{t('whoCanRead')}</legend>
          {VISIBILITIES.map(({ value, icon: Icon }) => {
            const active = meta.visibility === value
            const needsPublish = value === 'PUBLIC' && !meta.publishedVersion
            // ADR-0037: a note moderators hid or removed stays off the public pages until they approve it.
            const offPublic = value === 'PUBLIC' && (meta.moderation?.state === 'HIDDEN' || meta.moderation?.state === 'REMOVED')
            return (
              <label
                key={value}
                className={cn(
                  'flex cursor-pointer items-start gap-3 rounded-2xl border p-3 transition',
                  active ? 'border-accent bg-accent-soft ring-1 ring-accent/40' : 'border-border bg-surface hover:border-accent/40',
                  (needsPublish || offPublic) && 'cursor-not-allowed opacity-60',
                )}
              >
                <input type="radio" name="visibility" value={value} checked={active} disabled={needsPublish || offPublic || !meta.viewerCan.changeVisibility} onChange={() => void pickVisibility(value)} className="sr-only" />
                <span className={cn('grid size-9 shrink-0 place-items-center rounded-xl', active ? 'bg-accent text-accent-fg' : 'bg-surface-2 text-muted')}>
                  <Icon className="size-[1.125rem]" aria-hidden />
                </span>
                <span className="flex min-w-0 flex-col">
                  <span className="text-sm font-semibold">{t(`visibility.${value}`)}</span>
                  <span className="text-xs leading-5 text-muted">{offPublic ? t('offPublic') : needsPublish ? t('publishFirst') : t(`visibilityHint.${value}`)}</span>
                </span>
                {active ? <Check className="ml-auto size-4 shrink-0 text-accent" aria-hidden /> : null}
              </label>
            )
          })}
          {!meta.viewerCan.changeVisibility ? (
            <p className="text-xs text-muted">
              {t('verifyToShare')}{' '}
              <Link href="/profile" className="text-accent hover:underline">
                {t('verifyLink')}
              </Link>
            </p>
          ) : null}
        </fieldset>

        <section aria-labelledby="share-people" className="flex flex-col gap-3">
          <h3 id="share-people" className="text-sm font-semibold">
            {t('people')}
          </h3>
          <form
            className="flex flex-col gap-2 sm:flex-row"
            onSubmit={(e) => {
              e.preventDefault()
              if (person.trim()) void add(person, role)
            }}
          >
            <label className="min-w-0 flex-1">
              <span className="sr-only">{t('personLabel')}</span>
              <Input value={person} onChange={(e) => setPerson(e.target.value)} placeholder={t('personPlaceholder')} autoComplete="off" disabled={!meta.viewerCan.share} />
            </label>
            <div className="flex gap-2">
              <label className="flex-1 sm:flex-none">
                <span className="sr-only">{t('roleLabel')}</span>
                <select className="h-11 w-full rounded-xl border border-border bg-surface px-3 text-sm" value={role} onChange={(e) => setRole(e.target.value as NoteShareRole)} disabled={!meta.viewerCan.share}>
                  <option value="VIEWER">{t('role.VIEWER')}</option>
                  <option value="EDITOR">{t('role.EDITOR')}</option>
                </select>
              </label>
              <Button type="submit" className="gap-1.5" disabled={!person.trim() || sharing.loading || !meta.viewerCan.share}>
                <UserPlus className="size-4" aria-hidden />
                {t('add')}
              </Button>
            </div>
          </form>
          {people.length ? (
            <ul className="flex flex-col divide-y divide-border rounded-2xl border border-border bg-surface">
              {people.map((s) => {
                const accent = accentOf(s.user.id)
                return (
                  <li key={s.user.id} className="flex items-center gap-3 px-3 py-2.5">
                    <span className="grid size-8 shrink-0 place-items-center rounded-full text-sm font-bold text-white" style={{ background: `linear-gradient(135deg, ${accent.from}, ${accent.to})` }} aria-hidden>
                      {s.user.displayName.charAt(0).toUpperCase()}
                    </span>
                    <span className="flex min-w-0 flex-1 flex-col">
                      <span className="truncate text-sm font-medium">{s.user.displayName}</span>
                      <span className="truncate text-xs text-muted">@{s.user.handle}</span>
                    </span>
                    {s.source === 'CONNECTIONS' ? (
                      <span className="rounded-full bg-surface-2 px-2 py-0.5 text-xs text-muted">{t('viaConnections')}</span>
                    ) : (
                      <label>
                        <span className="sr-only">{t('roleFor', { name: s.user.displayName })}</span>
                        <select className="h-9 rounded-lg border border-border bg-bg px-2 text-xs" value={s.role} onChange={(e) => void add(`@${s.user.handle}`, e.target.value as NoteShareRole)}>
                          <option value="VIEWER">{t('role.VIEWER')}</option>
                          <option value="EDITOR">{t('role.EDITOR')}</option>
                        </select>
                      </label>
                    )}
                    <button type="button" className="rounded-lg p-1.5 text-muted hover:bg-surface-2 hover:text-fg" aria-label={t('remove', { name: s.user.displayName })} title={t('remove', { name: s.user.displayName })} onClick={() => void remove(s.user.id)}>
                      <X className="size-4" aria-hidden />
                    </button>
                  </li>
                )
              })}
            </ul>
          ) : shares.data ? (
            <p className="text-sm text-muted">{t('nobodyYet')}</p>
          ) : null}
          {meta.visibility === 'PRIVATE' && people.length ? <p className="text-xs text-muted">{t('privateHidesShares')}</p> : null}
        </section>

        {teacher ? (
          <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-border bg-surface p-3">
            <Handshake className="mt-0.5 size-[1.125rem] shrink-0 text-muted" aria-hidden />
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="text-sm font-semibold">{t('withConnections')}</span>
              <span className="text-xs leading-5 text-muted">{t('withConnectionsHint')}</span>
            </span>
            <input type="checkbox" role="switch" className="peer sr-only" checked={withConnections} disabled={settingConnections.loading} onChange={() => void toggleConnections()} />
            <span aria-hidden className="relative mt-0.5 h-6 w-11 shrink-0 rounded-full bg-surface-2 ring-1 ring-border transition after:absolute after:left-0.5 after:top-0.5 after:size-5 after:rounded-full after:bg-white after:shadow after:transition peer-checked:bg-accent peer-checked:after:translate-x-5 peer-focus-visible:ring-2 peer-focus-visible:ring-accent" />
          </label>
        ) : null}

        <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-border bg-surface p-3">
          <GitFork className="mt-0.5 size-[1.125rem] shrink-0 text-muted" aria-hidden />
          <span className="flex min-w-0 flex-1 flex-col">
            <span className="text-sm font-semibold">{t('allowCopies')}</span>
            <span className="text-xs leading-5 text-muted">{t('allowCopiesHint')}</span>
          </span>
          <input type="checkbox" role="switch" className="peer sr-only" checked={meta.forkingEnabled} disabled={settingForking.loading} onChange={() => void toggleForking()} />
          <span aria-hidden className="relative mt-0.5 h-6 w-11 shrink-0 rounded-full bg-surface-2 ring-1 ring-border transition after:absolute after:left-0.5 after:top-0.5 after:size-5 after:rounded-full after:bg-white after:shadow after:transition peer-checked:bg-accent peer-checked:after:translate-x-5 peer-focus-visible:ring-2 peer-focus-visible:ring-accent" />
        </label>

        {error ? (
          <p role="alert" className="text-sm text-red-600 dark:text-red-400">
            {error}
          </p>
        ) : null}

        <div className="flex items-center justify-between gap-2">
          <Button type="button" variant="secondary" className="gap-1.5" disabled={meta.visibility === 'PRIVATE'} title={meta.visibility === 'PRIVATE' ? t('copyLinkPrivate') : undefined} onClick={() => void copyLink()}>
            {copied ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}
            {copied ? t('copied') : t('copyLink')}
          </Button>
          <Button type="button" onClick={onClose}>
            {t('done')}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}

/** "Make a copy" (§4.4): a private copy of the note, credited to its author, opened in the editor. */
export function useMakeCopy(noteId: string) {
  const t = useTranslations('notes.share')
  const router = useRouter()
  const [fork, forking] = useMutation(ForkNoteDocument)
  const [error, setError] = useState<string | null>(null)
  const makeCopy = async () => {
    setError(null)
    const { result, error } = await attempt(() => fork({ variables: { noteId } }))
    const id = result?.data?.forkNote.note?.id
    if (id) router.push(`/notes/${id}`)
    else setError(problemOf(error, result?.data?.forkNote, t('copyFailed')) ?? t('copyFailed'))
  }
  return { makeCopy, copying: forking.loading, copyError: error }
}

export function MakeCopyButton({ copy, className }: { copy: ReturnType<typeof useMakeCopy>; className?: string }) {
  const t = useTranslations('notes.share')
  return (
    <Button variant="secondary" size="sm" className={cn('gap-1.5', className)} disabled={copy.copying} title={t('makeCopyHint')} onClick={() => void copy.makeCopy()}>
      <GitFork className="size-4" aria-hidden />
      {t('makeCopy')}
    </Button>
  )
}

/** The credit on a copy (ADR-0010): always the author; the original only while the viewer can still open it. */
export function ForkCredit({ credit }: { credit: NonNullable<NoteMeta['forkedFrom']> }) {
  const t = useTranslations('notes.share')
  return (
    <p className="inline-flex flex-wrap items-center gap-1 text-xs text-muted">
      <GitFork className="size-3.5" aria-hidden />
      {credit.note && credit.title ? (
        t.rich('copiedFrom', {
          title: () => (
            <Link href={`/notes/${credit.note!.id}`} className="font-medium text-accent hover:underline">
              {credit.title}
            </Link>
          ),
          name: credit.author.displayName,
        })
      ) : (
        t('copiedFromAuthor', { name: credit.author.displayName })
      )}
    </p>
  )
}

/** A small badge with the note's visibility, for the owner. */
export function VisibilityBadge({ visibility }: { visibility: Visibility }) {
  const t = useTranslations('notes.share')
  const Icon = VISIBILITIES.find((v) => v.value === visibility)!.icon
  return (
    <span className={cn('inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium', visibility === 'PUBLIC' ? 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' : visibility === 'SHARED' ? 'bg-accent-soft text-accent' : 'bg-surface-2 text-muted')}>
      <Icon className="size-3" aria-hidden />
      {t(`visibility.${visibility}`)}
    </span>
  )
}

/**
 * Share for someone who reads a note (board A's header, lvn-backend ADR-0076): copies its link — the public page of a
 * public note, else the note in the app, which opens for whoever it is shared with.
 */
export function CopyLinkButton({ note }: { note: Pick<NoteMeta, 'id' | 'slug' | 'visibility'> }) {
  const t = useTranslations('notes.view')
  const [copied, setCopied] = useState(false)
  const copyLink = async () => {
    const link = `${window.location.origin}${note.visibility === 'PUBLIC' ? publicNotePath(note) : `/notes/${note.id}`}`
    try {
      await navigator.clipboard.writeText(link)
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    } catch {
      window.prompt(t('shareHint'), link)
    }
  }
  return (
    <>
      <Button variant="secondary" size="sm" className="gap-1.5" title={t('shareHint')} onClick={() => void copyLink()}>
        <Share2 className="size-4" aria-hidden />
        {t('share')}
      </Button>
      {copied ? (
        <span role="status" className="text-xs font-medium text-accent">
          {t('linkCopied')}
        </span>
      ) : null}
    </>
  )
}
