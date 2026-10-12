'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { FileText, Globe, Lock, Pin, PinOff, Trash2, Users } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { ago } from '@/features/notes/look'
import { PostComments } from '@/features/discussion/PostComments'
import { ContentModeration, ModerationBanner } from '@/features/moderation/ModerationBanner'
import { ModerationQueue } from '@/features/moderation/ModerationQueue'
import { ReportButton } from '@/features/moderation/ReportDialog'
import { RichDoc } from '@/features/notes/render/RichText'
import {
  CreateGroupPostDocument,
  DeleteGroupDocument,
  DeleteGroupPostDocument,
  GroupDocument,
  GroupMembersDocument,
  GroupNotesDocument,
  GroupPostsDocument,
  JoinGroupDocument,
  LeaveGroupDocument,
  MuteGroupMemberDocument,
  MyNotesDocument,
  PinGroupPostDocument,
  RemoveGroupMemberDocument,
  RequestToJoinGroupDocument,
  ReviewGroupJoinRequestDocument,
  SetGroupRoleDocument,
  ShareNoteToGroupDocument,
  UpdateGroupDocument,
  WithdrawGroupJoinRequestDocument,
  type GroupDetailFragment,
  type GroupPostFieldsFragment,
} from '@/graphql/generated/graphql'
import type { Doc } from '@/lib/contracts/validation'
import { Doubts } from '@/features/workspaces/Doubts'
import { Ideas } from '@/features/workspaces/Ideas'
import { InviteMentor, ShowcaseSetting, WorkspaceHeader } from '@/features/workspaces/Workspace'
import { attempt, textToDoc } from './shared'

type Tab = 'posts' | 'ideas' | 'doubts' | 'notes' | 'members' | 'requests' | 'reports' | 'settings'

/** One group (lvn-backend ADR-0045): who it is for and how to get in; inside, posts, shared notes and members. */
export function GroupPage({ id }: { id: string }) {
  const t = useTranslations('groups')
  const { data, loading, refetch } = useQuery(GroupDocument, { variables: { id }, fetchPolicy: 'cache-and-network' })
  const [tab, setTab] = useState<Tab>('posts')
  const group = data?.group
  if (!group) return loading ? <p role="status" className="text-sm text-muted">{t('loading')}</p> : <p className="text-muted">{t('notFound')}</p>
  const member = !!group.viewerRole
  const project = group.type === 'PROJECT'
  const tabs: Tab[] = member ? ['posts', ...(project ? (['ideas', 'doubts'] as const) : []), 'notes', 'members', ...(group.viewerCan.reviewRequests ? (['requests'] as const) : []), ...(group.viewerCan.moderate ? (['reports'] as const) : []), ...(group.viewerCan.manage ? (['settings'] as const) : [])] : []
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Header group={group} onChanged={() => void refetch()} />
      {member ? (
        <>
          <div role="tablist" aria-label={t('sections')} className="flex gap-1 overflow-x-auto border-b border-border">
            {tabs.map((k) => (
              <button key={k} role="tab" type="button" aria-selected={k === tab} onClick={() => setTab(k)} className={`-mb-px whitespace-nowrap border-b-2 px-4 py-2 text-sm font-semibold ${k === tab ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}>
                {t(`tab.${k}`)}
              </button>
            ))}
          </div>
          <div role="tabpanel">
            {tab === 'posts' ? <Posts group={group} /> : null}
            {tab === 'ideas' ? <Ideas group={group} /> : null}
            {tab === 'doubts' ? <Doubts group={group} /> : null}
            {tab === 'notes' ? <SharedNotes group={group} /> : null}
            {tab === 'members' ? (
              <div className="flex flex-col gap-4">
                {group.viewerCan.inviteMentor ? <InviteMentor groupId={group.id} /> : null}
                <Members group={group} />
              </div>
            ) : null}
            {tab === 'requests' ? <Requests group={group} /> : null}
            {tab === 'reports' ? <ModerationQueue scope={{ scope: 'GROUP', id: group.id }} groupId={group.id} /> : null}
            {tab === 'settings' ? (
              <div className="flex flex-col gap-8">
                <Settings group={group} onSaved={() => void refetch()} />
                {project ? <ShowcaseSetting group={group} /> : null}
              </div>
            ) : null}
          </div>
        </>
      ) : (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('membersOnly')}</p>
      )}
    </div>
  )
}

function Header({ group, onChanged }: { group: GroupDetailFragment; onChanged: () => void }) {
  const t = useTranslations('groups')
  const [join] = useMutation(JoinGroupDocument)
  const [request] = useMutation(RequestToJoinGroupDocument)
  const [withdraw] = useMutation(WithdrawGroupJoinRequestDocument)
  const [leave] = useMutation(LeaveGroupDocument)
  const [message, setMessage] = useState('')
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const run = async (fn: () => Promise<{ data?: Record<string, { userErrors: { message: string }[] } | null> | null }>) => {
    setError(await attempt(fn, t('failed')))
    onChanged()
  }
  const Icon = group.privacy === 'PRIVATE' ? Lock : Globe
  return (
    <header className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-6 shadow-sm">
      <div className="flex flex-wrap items-center gap-2 text-sm text-muted">
        <Icon className="size-4" aria-hidden />
        {t(`privacy.${group.privacy}`)}
        {group.type === 'PROJECT' ? (
          <>
            <span aria-hidden>·</span>
            {t('project')}
          </>
        ) : null}
        <span aria-hidden>·</span>
        <Users className="size-4" aria-hidden />
        {t('members', { count: group.memberCount })}
        {group.viewerRole ? <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">{t(`role.${group.viewerRole}`)}</span> : null}
      </div>
      <h1 className="text-2xl font-extrabold tracking-tight">{group.name}</h1>
      {group.description ? <p className="whitespace-pre-line text-muted">{group.description}</p> : null}
      {group.moderationWarning ? <ModerationBanner entityType="GROUP" entityId={group.id} moderation={{ state: 'OK', reason: group.moderationWarning, canAppeal: false }} /> : null}
      {group.type === 'PROJECT' ? <WorkspaceHeader group={group} onChanged={onChanged} /> : null}
      <div className="flex flex-wrap items-center gap-2">
        {group.viewerCan.join ? <Button onClick={() => void run(() => join({ variables: { groupId: group.id } }))}>{t('join')}</Button> : null}
        {group.viewerCan.requestJoin && !asking ? (
          <Button onClick={() => setAsking(true)}>{t('askToJoin')}</Button>
        ) : null}
        {group.viewerRequestId ? (
          <>
            <span className="text-sm text-muted">{t('waiting')}</span>
            <Button variant="secondary" size="sm" onClick={() => void run(() => withdraw({ variables: { requestId: group.viewerRequestId! } }))}>
              {t('withdraw')}
            </Button>
          </>
        ) : null}
        {group.viewerCan.leave ? (
          <Button variant="secondary" size="sm" onClick={() => void run(() => leave({ variables: { groupId: group.id } }))}>
            {t('leave')}
          </Button>
        ) : null}
        <ReportButton entityType="GROUP" entityId={group.id} authorId={group.owner.id} className="ml-auto" />
      </div>
      {asking && group.viewerCan.requestJoin ? (
        <form
          className="flex flex-col gap-2"
          onSubmit={(e) => {
            e.preventDefault()
            setAsking(false)
            void run(() => request({ variables: { groupId: group.id, message: message.trim() || null } }))
          }}
        >
          <label className="flex flex-col gap-1.5">
            <span className="text-sm font-semibold">{t('messageLabel')}</span>
            <textarea value={message} maxLength={500} rows={2} onChange={(e) => setMessage(e.target.value)} className="rounded-xl border border-border bg-bg px-3 py-2 text-sm" />
          </label>
          <Button type="submit" className="w-fit">
            {t('sendRequest')}
          </Button>
        </form>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
    </header>
  )
}

function Posts({ group }: { group: GroupDetailFragment }) {
  const t = useTranslations('groups')
  const { data, refetch, fetchMore } = useQuery(GroupPostsDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const [create, creating] = useMutation(CreateGroupPostDocument)
  const [remove] = useMutation(DeleteGroupPostDocument)
  const [pin] = useMutation(PinGroupPostDocument)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const posts = data?.group?.posts
  const act = async (fn: () => Promise<{ data?: Record<string, { userErrors: { message: string }[] } | null> | null }>) => {
    setError(await attempt(fn, t('failed')))
    await refetch()
  }
  const all = [...(posts?.pinned ?? []), ...(posts?.edges.map((e) => e.node) ?? [])]
  return (
    <div className="flex flex-col gap-4">
      {group.viewerCan.post ? (
        <form
          className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-3"
          onSubmit={(e) => {
            e.preventDefault()
            void act(async () => {
              const res = await create({ variables: { groupId: group.id, body: textToDoc(text) } })
              if (res.data?.createGroupPost.post) setText('')
              return res
            })
          }}
        >
          <label className="sr-only" htmlFor="new-post">
            {t('postLabel')}
          </label>
          <textarea id="new-post" value={text} rows={3} onChange={(e) => setText(e.target.value)} placeholder={t('postPlaceholder')} className="resize-y bg-transparent text-sm focus:outline-none" />
          <Button type="submit" size="sm" className="self-end" disabled={creating.loading || !text.trim()}>
            {t('post')}
          </Button>
        </form>
      ) : null}
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      {all.length ? (
        <ul className="flex flex-col gap-3">
          {all.map((p) => (
            <PostItem key={p.id} post={p} onPin={() => void act(() => pin({ variables: { postId: p.id, pinned: !p.pinned } }))} onDelete={() => void act(() => remove({ variables: { postId: p.id } }))} onChanged={() => void refetch()} />
          ))}
        </ul>
      ) : posts ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noPosts')}</p>
      ) : null}
      {posts?.pageInfo.hasNextPage ? (
        <Button variant="secondary" className="self-center" onClick={() =>
            void fetchMore({
              variables: { after: posts.pageInfo.endCursor },
              updateQuery: (prev, { fetchMoreResult }) =>
                prev.group?.posts && fetchMoreResult.group?.posts ? { group: { ...fetchMoreResult.group, posts: { ...fetchMoreResult.group.posts, pinned: prev.group.posts.pinned, edges: [...prev.group.posts.edges, ...fetchMoreResult.group.posts.edges] } } } : fetchMoreResult,
            })
          }>
          {t('older')}
        </Button>
      ) : null}
    </div>
  )
}

function PostItem({ post, onPin, onDelete, onChanged }: { post: GroupPostFieldsFragment; onPin: () => void; onDelete: () => void; onChanged: () => void }) {
  const t = useTranslations('groups')
  return (
    <li className={`flex flex-col gap-2 rounded-2xl border bg-surface p-4 ${post.pinned ? 'border-accent/50' : 'border-border'}`}>
      <div className="flex items-center gap-2 text-sm">
        <Link href={`/u/${post.author.handle}`} className="font-semibold hover:text-accent">
          {post.author.displayName}
        </Link>
        <span className="text-xs text-muted">
          {ago(post.createdAt)}
          {post.editedAt ? ` · ${t('edited')}` : ''}
        </span>
        {post.pinned ? <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">{t('pinned')}</span> : null}
        <span className="ml-auto flex gap-1">
          {post.viewerCan.pin ? (
            <button type="button" onClick={onPin} aria-label={post.pinned ? t('unpin') : t('pin')} className="rounded-lg p-1.5 text-muted hover:bg-surface-2 hover:text-fg">
              {post.pinned ? <PinOff className="size-4" aria-hidden /> : <Pin className="size-4" aria-hidden />}
            </button>
          ) : null}
          {post.viewerCan.delete ? (
            <button type="button" onClick={onDelete} aria-label={t('deletePost')} className="rounded-lg p-1.5 text-muted hover:bg-surface-2 hover:text-red-600">
              <Trash2 className="size-4" aria-hidden />
            </button>
          ) : null}
          <ReportButton look="icon" entityType="GROUP_POST" entityId={post.id} authorId={post.author.id} />
        </span>
      </div>
      <ContentModeration entityType="GROUP_POST" item={post} onAppealed={onChanged} />
      <RichDoc doc={post.body as Doc} className="text-sm" />
      <PostComments type="GROUP_POST" id={post.id} count={post.discussion.commentCount} />
    </li>
  )
}

function SharedNotes({ group }: { group: GroupDetailFragment }) {
  const t = useTranslations('groups')
  const { data, refetch } = useQuery(GroupNotesDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const mine = useQuery(MyNotesDocument, { variables: { first: 50 }, fetchPolicy: 'cache-and-network' })
  const [share] = useMutation(ShareNoteToGroupDocument)
  const [chosen, setChosen] = useState('')
  const [error, setError] = useState<string | null>(null)
  const notes = data?.group?.sharedNotes?.edges.map((e) => e.node) ?? []
  const shared = new Set(notes.map((n) => n.id))
  const choices = (mine.data?.myNotes.edges.map((e) => e.node) ?? []).filter((n) => !shared.has(n.id))
  return (
    <div className="flex flex-col gap-4">
      <form
        className="flex flex-wrap items-end gap-2"
        onSubmit={(e) => {
          e.preventDefault()
          if (!chosen) return
          void attempt(() => share({ variables: { noteId: chosen, groupId: group.id } }), t('failed')).then((p) => {
            setError(p)
            setChosen('')
            void refetch()
          })
        }}
      >
        <label className="flex min-w-0 flex-1 flex-col gap-1.5">
          <span className="text-sm font-semibold">{t('shareNote')}</span>
          <select value={chosen} onChange={(e) => setChosen(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3 text-sm">
            <option value="">{t('chooseNote')}</option>
            {choices.map((n) => (
              <option key={n.id} value={n.id}>
                {n.title || t('untitled')}
              </option>
            ))}
          </select>
        </label>
        <Button type="submit" disabled={!chosen}>
          {t('share')}
        </Button>
      </form>
      <p className="text-xs text-muted">{t('shareHint')}</p>
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      {notes.length ? (
        <ul className="grid gap-3 sm:grid-cols-2">
          {notes.map((n) => (
            <li key={n.id}>
              <Link href={`/notes/${n.id}`} className="flex h-full items-start gap-3 rounded-2xl border border-border bg-surface p-4 hover:border-accent/50">
                <FileText className="mt-0.5 size-5 shrink-0 text-accent" aria-hidden />
                <span className="flex min-w-0 flex-col">
                  <span className="font-semibold">{n.title || t('untitled')}</span>
                  <span className="text-xs text-muted">{t('by', { name: n.owner.displayName })}</span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      ) : data ? (
        <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noNotes')}</p>
      ) : null}
    </div>
  )
}

const ROLES = ['ADMIN', 'MODERATOR', 'MEMBER'] as const

function Members({ group }: { group: GroupDetailFragment }) {
  const t = useTranslations('groups')
  const { data, refetch } = useQuery(GroupMembersDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const [setRole] = useMutation(SetGroupRoleDocument)
  const [remove] = useMutation(RemoveGroupMemberDocument)
  const [mute] = useMutation(MuteGroupMemberDocument)
  const [error, setError] = useState<string | null>(null)
  const act = async (fn: () => Promise<{ data?: Record<string, { userErrors: { message: string }[] } | null> | null }>) => {
    setError(await attempt(fn, t('failed')))
    await refetch()
  }
  const rank = { OWNER: 4, ADMIN: 3, MODERATOR: 2, MEMBER: 1, MENTOR: 1 } as const
  const mine = rank[group.viewerRole ?? 'MEMBER']
  return (
    <div className="flex flex-col gap-3">
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
        {(data?.group?.members ?? []).map((m) => {
          const below = rank[m.role] < mine
          const muted = m.mutedUntil && new Date(m.mutedUntil) > new Date()
          return (
            <li key={m.user.id} className="flex flex-wrap items-center gap-3 px-4 py-3">
              <Link href={`/u/${m.user.handle}`} className="flex min-w-0 flex-1 flex-col hover:text-accent">
                <span className="truncate font-semibold">{m.user.displayName}</span>
                <span className="truncate text-xs text-muted">
                  {t(`role.${m.role}`)}
                  {muted ? ` · ${t('muted')}` : ''}
                </span>
              </Link>
              {group.viewerCan.manage && below ? (
                <>
                  {/* A mentor stays a mentor (ADR-0048): no role to change, nothing to hand over. */}
                  {m.role !== 'MENTOR' ? (
                    <label>
                      <span className="sr-only">{t('roleFor', { name: m.user.displayName })}</span>
                      <select
                        value={m.role}
                        onChange={(e) => {
                          const role = e.target.value as (typeof ROLES)[number] | 'OWNER'
                          if (role === 'OWNER' && !window.confirm(t('handOverConfirm', { name: m.user.displayName }))) return
                          void act(() => setRole({ variables: { groupId: group.id, userId: m.user.id, role } }))
                        }}
                        className="h-9 rounded-lg border border-border bg-bg px-2 text-xs"
                      >
                        {ROLES.filter((r) => rank[r] < mine || r === m.role).map((r) => (
                          <option key={r} value={r}>
                            {t(`role.${r}`)}
                          </option>
                        ))}
                        {group.viewerRole === 'OWNER' ? <option value="OWNER">{t('handOver', { name: m.user.displayName })}</option> : null}
                      </select>
                    </label>
                  ) : null}
                  <Button variant="secondary" size="sm" onClick={() => void act(() => remove({ variables: { groupId: group.id, userId: m.user.id } }))}>
                    {t('remove')}
                  </Button>
                </>
              ) : null}
              {group.viewerCan.moderate && below ? (
                <Button variant="ghost" size="sm" onClick={() => void act(() => mute({ variables: { groupId: group.id, userId: m.user.id, until: muted ? null : new Date(Date.now() + 86_400_000).toISOString() } }))}>
                  {muted ? t('unmute') : t('muteDay')}
                </Button>
              ) : null}
            </li>
          )
        })}
      </ul>
    </div>
  )
}

function Requests({ group }: { group: GroupDetailFragment }) {
  const t = useTranslations('groups')
  const { data, refetch } = useQuery(GroupMembersDocument, { variables: { id: group.id }, fetchPolicy: 'cache-and-network' })
  const [review] = useMutation(ReviewGroupJoinRequestDocument)
  const requests = data?.group?.joinRequests ?? []
  const decide = async (requestId: string, decision: 'APPROVED' | 'REJECTED') => {
    await review({ variables: { requestId, decision } })
    await refetch()
  }
  if (!requests.length) return <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noRequests')}</p>
  return (
    <ul className="flex flex-col gap-2">
      {requests.map((r) => (
        <li key={r.id} className="flex flex-wrap items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3">
          <span className="flex min-w-0 flex-1 flex-col">
            <Link href={`/u/${r.user.handle}`} className="font-semibold hover:text-accent">
              {r.user.displayName}
            </Link>
            {r.message ? <span className="text-sm text-muted">“{r.message}”</span> : null}
          </span>
          <Button size="sm" onClick={() => void decide(r.id, 'APPROVED')}>
            {t('approve')}
          </Button>
          <Button variant="secondary" size="sm" onClick={() => void decide(r.id, 'REJECTED')}>
            {t('reject')}
          </Button>
        </li>
      ))}
    </ul>
  )
}

function Settings({ group, onSaved }: { group: GroupDetailFragment; onSaved: () => void }) {
  const t = useTranslations('groups')
  const router = useRouter()
  const [update, updating] = useMutation(UpdateGroupDocument)
  const [del] = useMutation(DeleteGroupDocument)
  const [name, setName] = useState(group.name)
  const [description, setDescription] = useState(group.description ?? '')
  const [privacy, setPrivacy] = useState(group.privacy)
  const [open, setOpen] = useState(group.joinPolicy === 'OPEN')
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  const save = async () => {
    const problem = await attempt(() => update({ variables: { input: { groupId: group.id, name, description: description || null, privacy, joinPolicy: privacy === 'PUBLIC' && open ? 'OPEN' : 'APPROVAL' } } }), t('failed'))
    setMessage(problem ? { ok: false, text: problem } : { ok: true, text: t('saved') })
    onSaved()
  }
  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={(e) => {
        e.preventDefault()
        void save()
      }}
    >
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">{t('name')}</span>
        <input value={name} maxLength={80} onChange={(e) => setName(e.target.value)} className="h-11 rounded-xl border border-border bg-surface px-3" />
      </label>
      <label className="flex flex-col gap-1.5">
        <span className="text-sm font-semibold">{t('description')}</span>
        <textarea value={description} maxLength={2000} rows={3} onChange={(e) => setDescription(e.target.value)} className="rounded-xl border border-border bg-surface px-3 py-2" />
      </label>
      <fieldset className="flex flex-col gap-2">
        <legend className="mb-1 text-sm font-semibold">{t('who')}</legend>
        {(['PUBLIC', 'PRIVATE'] as const).map((p) => (
          <label key={p} className="flex items-center gap-2 text-sm">
            <input type="radio" name="settings-privacy" checked={privacy === p} onChange={() => setPrivacy(p)} />
            {t(`privacy.${p}`)}
          </label>
        ))}
      </fieldset>
      {privacy === 'PUBLIC' ? (
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={open} onChange={(e) => setOpen(e.target.checked)} />
          {t('openJoin')}
        </label>
      ) : null}
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-red-600 dark:text-red-400'}>
          {message.text}
        </p>
      ) : null}
      <div className="flex flex-wrap justify-between gap-2">
        <Button type="submit" disabled={updating.loading}>
          {t('save')}
        </Button>
        {group.viewerCan.delete ? (
          <Button
            type="button"
            className="bg-red-600 text-white hover:bg-red-700"
            onClick={() => {
              if (!window.confirm(t('deleteConfirm', { name: group.name }))) return
              void del({ variables: { groupId: group.id } }).then(() => router.push('/groups'))
            }}
          >
            {t('delete')}
          </Button>
        ) : null}
      </div>
    </form>
  )
}
