'use client'

import { CombinedGraphQLErrors } from '@apollo/client/errors'
import { useMutation, useQuery } from '@apollo/client/react'
import { Ellipsis, Handshake, UserCheck, UserPlus } from 'lucide-react'
import Link from 'next/link'
import { useTranslations } from 'next-intl'
import { useEffect, useRef, useState } from 'react'
import { AuthProvider } from '@/components/auth/AuthProvider'
import { GatedNotice } from '@/components/auth/GatedNotice'
import { useUnverifiedGates } from '@/components/auth/useUnverifiedGates'
import { Button } from '@/components/ui/button'
import { Dialog } from '@/components/ui/dialog'
import {
  BlockUserDocument,
  FollowUserDocument,
  ProfileRelationDocument,
  RemoveConnectionDocument,
  RemoveFollowerDocument,
  RequestConnectionDocument,
  RespondToConnectionRequestDocument,
  RestrictUserDocument,
  UnblockUserDocument,
  UnfollowUserDocument,
  UnrestrictUserDocument,
  WithdrawConnectionRequestDocument,
} from '@/graphql/generated/graphql'
import { useSession } from '@/state/session'
import { ReportDialog } from '@/features/moderation/ReportDialog'

/**
 * The viewer's buttons on a profile (lvn-backend ADR-0043), loaded in the browser around the cached page: Follow, or
 * Following; the menu to remove a follower, restrict or block. What shows comes from `relation.viewerCan`, the same
 * rules the API applies. Signed out, Follow leads to sign-in.
 */
export function ProfileActions(props: { id: string; handle: string }) {
  return (
    <AuthProvider>
      <Actions {...props} />
    </AuthProvider>
  )
}

type Act = 'follow' | 'unfollow' | 'removeFollower' | 'block' | 'unblock' | 'restrict' | 'unrestrict' | 'connect' | 'disconnect'

function Actions({ id, handle }: { id: string; handle: string }) {
  const t = useTranslations('people')
  const followHeld = useUnverifiedGates().gated('FOLLOW')
  const status = useSession((s) => s.status)
  const { data } = useQuery(ProfileRelationDocument, { variables: { handle }, skip: status !== 'signed-in', fetchPolicy: 'cache-and-network' })
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [menu, setMenu] = useState(false)
  const [confirmBlock, setConfirmBlock] = useState(false)
  const [reporting, setReporting] = useState(false)
  const [run] = useMutation(FollowUserDocument)
  const [unfollow] = useMutation(UnfollowUserDocument)
  const [removeFollower] = useMutation(RemoveFollowerDocument)
  const [block] = useMutation(BlockUserDocument)
  const [unblock] = useMutation(UnblockUserDocument)
  const [restrict] = useMutation(RestrictUserDocument)
  const [unrestrict] = useMutation(UnrestrictUserDocument)
  const [connect] = useMutation(RequestConnectionDocument)
  const [disconnect] = useMutation(RemoveConnectionDocument)
  const [respond] = useMutation(RespondToConnectionRequestDocument)
  const [withdraw] = useMutation(WithdrawConnectionRequestDocument)
  const mutate: Record<Act, (o: { variables: { input: { userId: string } } }) => Promise<{ data?: unknown }>> = { follow: run, unfollow, removeFollower, block, unblock, restrict, unrestrict, connect, disconnect }

  /** Runs one change and shows what went wrong in the API's words. */
  const attempt = async (call: () => Promise<{ data?: unknown }>) => {
    setBusy(true)
    setError(null)
    setMenu(false)
    try {
      const res = (await call()) as { data?: Record<string, { userErrors: { message: string }[] }> }
      const problem = Object.values(res.data ?? {})[0]?.userErrors[0]?.message
      if (problem) setError(problem)
    } catch (e) {
      setError(CombinedGraphQLErrors.is(e) ? (e.errors[0]?.message ?? t('failed')) : t('failed'))
    } finally {
      setBusy(false)
    }
  }
  const act = (what: Act) => attempt(() => mutate[what]({ variables: { input: { userId: id } } }))

  if (status === 'unknown') return null
  if (status !== 'signed-in') {
    return (
      <Button asChild>
        <Link href={`/sign-in?next=${encodeURIComponent(`/u/${handle}`)}`}>
          <UserPlus className="size-4" aria-hidden />
          {t('follow')}
        </Link>
      </Button>
    )
  }
  const person = data?.userByHandle
  if (!person) return null
  // One's own profile: exact counts (others see a milestone, ADR-0027) and the way to the lists.
  if (data?.viewer?.id === person.id) {
    return (
      <div className="flex flex-col items-start gap-2 sm:items-end">
        <Link href="/profile/people" className="text-sm text-muted hover:text-accent">
          {t('counts', { followers: person.followerCount ?? 0, following: person.followingCount ?? 0 })}
        </Link>
        <Button asChild variant="secondary" size="sm">
          <Link href="/profile">{t('editProfile')}</Link>
        </Button>
      </div>
    )
  }
  const r = person.relation
  if (!r) return null
  return (
    <div className="flex flex-col items-start gap-2 sm:items-end">
      {r.followedBy ? <span className="rounded-full bg-surface-2 px-2.5 py-0.5 text-xs font-medium text-muted">{t('followsYou')}</span> : null}
      <div className="flex items-center gap-2">
        {r.blocked ? (
          <Button variant="secondary" disabled={busy} onClick={() => void act('unblock')}>
            {t('unblock')}
          </Button>
        ) : r.following ? (
          <Button variant="secondary" disabled={busy} onClick={() => void act('unfollow')} aria-label={t('unfollowLabel')}>
            <UserCheck className="size-4" aria-hidden />
            {t('following')}
          </Button>
        ) : r.viewerCan.follow || (followHeld && !r.blocked) ? (
          <Button disabled={busy} onClick={() => void act('follow')}>
            <UserPlus className="size-4" aria-hidden />
            {t('follow')}
          </Button>
        ) : null}
        {/* Teachers connect with teachers (ADR-0013). */}
        {r.connected ? (
          <span className="inline-flex h-11 items-center gap-1.5 rounded-xl bg-accent-soft px-3 text-sm font-semibold text-accent">
            <Handshake className="size-4" aria-hidden />
            {t('connected')}
          </span>
        ) : r.pendingConnection?.direction === 'INCOMING' ? (
          <>
            <Button disabled={busy} onClick={() => void attempt(() => respond({ variables: { input: { requestId: r.pendingConnection!.requestId, accept: true } } }))}>
              {t('acceptConnection')}
            </Button>
            <Button variant="secondary" disabled={busy} onClick={() => void attempt(() => respond({ variables: { input: { requestId: r.pendingConnection!.requestId, accept: false } } }))}>
              {t('decline')}
            </Button>
          </>
        ) : r.pendingConnection?.direction === 'OUTGOING' ? (
          <Button variant="secondary" disabled={busy} aria-label={t('requestedLabel')} onClick={() => void attempt(() => withdraw({ variables: { input: { requestId: r.pendingConnection!.requestId } } }))}>
            {t('requested')}
          </Button>
        ) : r.viewerCan.requestConnection ? (
          <Button variant="secondary" disabled={busy} onClick={() => void act('connect')}>
            <Handshake className="size-4" aria-hidden />
            {t('connect')}
          </Button>
        ) : null}
        <MoreMenu open={menu} onToggle={setMenu} label={t('more')}>
          {r.viewerCan.removeConnection ? <MenuItem onClick={() => void act('disconnect')}>{t('removeConnection')}</MenuItem> : null}
          {r.viewerCan.removeFollower ? <MenuItem onClick={() => void act('removeFollower')}>{t('removeFollower')}</MenuItem> : null}
          {r.viewerCan.restrict ? <MenuItem onClick={() => void act('restrict')}>{t('restrict')}</MenuItem> : null}
          {r.viewerCan.unrestrict ? <MenuItem onClick={() => void act('unrestrict')}>{t('unrestrict')}</MenuItem> : null}
          {r.viewerCan.block ? (
            <MenuItem danger onClick={() => (setMenu(false), setConfirmBlock(true))}>
              {t('block')}
            </MenuItem>
          ) : null}
          {r.viewerCan.unblock ? <MenuItem onClick={() => void act('unblock')}>{t('unblock')}</MenuItem> : null}
          <MenuItem onClick={() => (setMenu(false), setReporting(true))}>{t('report')}</MenuItem>
        </MoreMenu>
        <ReportDialog entityType="USER" entityId={person.id} open={reporting} onClose={() => setReporting(false)} />
      </div>
      <GatedNotice feature="FOLLOW" when={!r.viewerCan.follow && !r.following && !r.blocked} />
      {r.restricted ? <span className="text-xs text-muted">{t('restrictedNote')}</span> : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <Dialog open={confirmBlock} onClose={() => setConfirmBlock(false)} title={t('blockTitle')}>
        <div className="flex flex-col gap-4">
          <ul className="list-disc space-y-1 pl-5 text-sm text-muted">
            <li>{t('blockEffects.follows')}</li>
            <li>{t('blockEffects.contact')}</li>
            <li>{t('blockEffects.hidden')}</li>
            <li>{t('blockEffects.silent')}</li>
          </ul>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setConfirmBlock(false)}>
              {t('cancel')}
            </Button>
            <Button className="bg-red-600 text-white hover:bg-red-700" disabled={busy} onClick={() => (setConfirmBlock(false), void act('block'))}>
              {t('block')}
            </Button>
          </div>
        </div>
      </Dialog>
    </div>
  )
}

function MoreMenu({ open, onToggle, label, children }: { open: boolean; onToggle: (open: boolean) => void; label: string; children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  useEffect(() => {
    if (!open) return
    const close = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent ? e.key === 'Escape' : !ref.current?.contains(e.target as Node)) onToggle(false)
    }
    document.addEventListener('mousedown', close)
    document.addEventListener('keydown', close)
    return () => {
      document.removeEventListener('mousedown', close)
      document.removeEventListener('keydown', close)
    }
  }, [open, onToggle])
  return (
    <div ref={ref} className="relative">
      <Button variant="secondary" size="sm" aria-label={label} aria-haspopup="menu" aria-expanded={open} onClick={() => onToggle(!open)}>
        <Ellipsis className="size-4" aria-hidden />
      </Button>
      {open ? (
        <div role="menu" className="absolute right-0 top-full z-20 mt-1 flex min-w-48 flex-col overflow-hidden rounded-xl border border-border bg-surface py-1 shadow-lg">
          {children}
        </div>
      ) : null}
    </div>
  )
}

function MenuItem({ onClick, danger, children }: { onClick: () => void; danger?: boolean; children: React.ReactNode }) {
  return (
    <button role="menuitem" type="button" onClick={onClick} className={`px-4 py-2 text-left text-sm hover:bg-surface-2 ${danger ? 'text-red-600 dark:text-red-400' : ''}`}>
      {children}
    </button>
  )
}
