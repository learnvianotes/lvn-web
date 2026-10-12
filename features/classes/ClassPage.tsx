'use client'

import { useMutation, useQuery } from '@apollo/client/react'
import { Copy, FileText, GraduationCap, RefreshCw, Trash2, Users } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { PostComments } from '@/features/discussion/PostComments'
import { attempt, textToDoc } from '@/features/groups/shared'
import { ago } from '@/features/notes/look'
import { RichDoc } from '@/features/notes/render/RichText'
import {
  AnswerClassroomInviteDocument,
  ClassroomDocument,
  ClassroomNotesDocument,
  ClassroomPeopleDocument,
  ClassroomPostsDocument,
  CreateClassroomPostDocument,
  DeleteClassroomDocument,
  DeleteClassroomPostDocument,
  InviteToClassroomDocument,
  LeaveClassroomDocument,
  MyNotesDocument,
  RemoveClassroomMemberDocument,
  ReviewClassroomJoinRequestDocument,
  SetClassroomRoleDocument,
  ShareNoteToClassroomDocument,
  UpdateClassroomDocument,
  WithdrawClassroomJoinRequestDocument,
  type ClassroomDetailFragment,
} from '@/graphql/generated/graphql'
import type { Doc } from '@/lib/contracts/validation'

type Tab = 'posts' | 'notes' | 'people' | 'requests' | 'settings'
type Run = () => Promise<{ data?: Record<string, { userErrors: { message: string }[] } | null> | null }>

/** One class (lvn-backend ADR-0046): announcements and notes for its members; people, requests and settings for staff. */
export function ClassPage({ id }: { id: string }) {
  const t = useTranslations('classes')
  const { data, loading, refetch } = useQuery(ClassroomDocument, { variables: { id }, fetchPolicy: 'cache-and-network' })
  const [tab, setTab] = useState<Tab>('posts')
  const classroom = data?.classroom
  if (!classroom) return loading ? <p role="status" className="text-sm text-muted">{t('loading')}</p> : <p className="text-muted">{t('notFound')}</p>
  const staff = classroom.viewerCan.review
  const tabs: Tab[] = classroom.viewerRole ? ['posts', 'notes', ...(staff ? (['people', 'requests'] as const) : []), ...(classroom.viewerCan.manage ? (['settings'] as const) : [])] : []
  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <Header classroom={classroom} onChanged={() => void refetch()} />
      {tabs.length ? (
        <>
          <div role="tablist" aria-label={t('sections')} className="flex gap-1 overflow-x-auto border-b border-border">
            {tabs.map((k) => (
              <button key={k} role="tab" type="button" aria-selected={k === tab} onClick={() => setTab(k)} className={`-mb-px whitespace-nowrap border-b-2 px-4 py-2 text-sm font-semibold ${k === tab ? 'border-accent text-accent' : 'border-transparent text-muted hover:text-fg'}`}>
                {t(`tab.${k}`)}
              </button>
            ))}
          </div>
          <div role="tabpanel">
            {tab === 'posts' ? <Posts classroom={classroom} /> : null}
            {tab === 'notes' ? <SharedNotes classroom={classroom} /> : null}
            {tab === 'people' ? <People classroom={classroom} onChanged={() => void refetch()} /> : null}
            {tab === 'requests' ? <Requests classroom={classroom} onChanged={() => void refetch()} /> : null}
            {tab === 'settings' ? <Settings classroom={classroom} onSaved={() => void refetch()} /> : null}
          </div>
        </>
      ) : null}
    </div>
  )
}

function Header({ classroom, onChanged }: { classroom: ClassroomDetailFragment; onChanged: () => void }) {
  const t = useTranslations('classes')
  const router = useRouter()
  const [answer] = useMutation(AnswerClassroomInviteDocument)
  const [withdraw] = useMutation(WithdrawClassroomJoinRequestDocument)
  const [leave] = useMutation(LeaveClassroomDocument)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const run = async (fn: Run) => {
    setError(await attempt(fn, t('failed')))
    onChanged()
  }
  const copyLink = async () => {
    await navigator.clipboard?.writeText(`${window.location.origin}/classes/join/${classroom.joinCode}`).catch(() => undefined)
    setCopied(true)
  }
  return (
    <header className="flex flex-col gap-3 rounded-3xl border border-border bg-surface p-6 shadow-sm">
      <div className="flex flex-wrap items-center gap-2 text-sm text-muted">
        <GraduationCap className="size-4" aria-hidden />
        {t('byTeacher', { name: classroom.teacher.displayName })}
        <span aria-hidden>·</span>
        <Users className="size-4" aria-hidden />
        {t('members', { count: classroom.memberCount })}
        {classroom.viewerRole ? <span className="rounded-full bg-accent-soft px-2 py-0.5 text-xs font-semibold text-accent">{t(`role.${classroom.viewerRole}`)}</span> : null}
      </div>
      <h1 className="text-2xl font-extrabold tracking-tight">{classroom.name}</h1>
      {classroom.description ? <p className="whitespace-pre-line text-muted">{classroom.description}</p> : null}
      {classroom.joinCode ? (
        <div className="flex flex-col gap-1 rounded-2xl bg-surface-2 p-3">
          <span className="text-xs font-semibold text-muted">{t('code')}</span>
          <div className="flex flex-wrap items-center gap-2">
            <span data-testid="class-code" className="font-mono text-xl font-bold tracking-widest">
              {classroom.joinCode}
            </span>
            <Button variant="secondary" size="sm" className="gap-1.5" onClick={() => void copyLink()}>
              <Copy className="size-3.5" aria-hidden />
              {copied ? t('copied') : t('copyLink')}
            </Button>
          </div>
          <span className="text-xs text-muted">{t('codeHint')}</span>
        </div>
      ) : null}
      <div className="flex flex-wrap items-center gap-2">
        {classroom.viewerInviteId ? (
          <>
            <span className="text-sm">{t('invited')}</span>
            <Button size="sm" onClick={() => void run(() => answer({ variables: { inviteId: classroom.viewerInviteId!, accept: true } }))}>
              {t('accept')}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => void attempt(() => answer({ variables: { inviteId: classroom.viewerInviteId!, accept: false } }), t('failed')).then(() => router.push('/classes'))}
            >
              {t('decline')}
            </Button>
          </>
        ) : null}
        {classroom.viewerRequestId ? (
          <>
            <span className="text-sm text-muted">{t('waiting')}</span>
            <Button variant="secondary" size="sm" onClick={() => void attempt(() => withdraw({ variables: { requestId: classroom.viewerRequestId! } }), t('failed')).then(() => router.push('/classes'))}>
              {t('withdraw')}
            </Button>
          </>
        ) : null}
        {classroom.viewerCan.leave ? (
          <Button variant="secondary" size="sm" onClick={() => void attempt(() => leave({ variables: { classroomId: classroom.id } }), t('failed')).then((p) => (p ? setError(p) : router.push('/classes')))}>
            {t('leave')}
          </Button>
        ) : null}
      </div>
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
    </header>
  )
}

function Posts({ classroom }: { classroom: ClassroomDetailFragment }) {
  const t = useTranslations('classes')
  const { data, refetch, fetchMore } = useQuery(ClassroomPostsDocument, { variables: { id: classroom.id }, fetchPolicy: 'cache-and-network' })
  const [create, creating] = useMutation(CreateClassroomPostDocument)
  const [remove] = useMutation(DeleteClassroomPostDocument)
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)
  const posts = data?.classroom?.posts
  const act = async (fn: Run) => {
    setError(await attempt(fn, t('failed')))
    await refetch()
  }
  return (
    <div className="flex flex-col gap-4">
      {classroom.viewerCan.post ? (
        <form
          className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-3"
          onSubmit={(e) => {
            e.preventDefault()
            void act(async () => {
              const res = await create({ variables: { classroomId: classroom.id, body: textToDoc(text) } })
              if (res.data?.createClassroomPost.classroom) setText('')
              return res
            })
          }}
        >
          <label className="sr-only" htmlFor="new-announcement">
            {t('postLabel')}
          </label>
          <textarea id="new-announcement" value={text} rows={3} onChange={(e) => setText(e.target.value)} placeholder={t('postPlaceholder')} className="resize-y bg-transparent text-sm focus:outline-none" />
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
      {posts?.edges.length ? (
        <ul className="flex flex-col gap-3">
          {posts.edges.map(({ node: p }) => (
            <li key={p.id} className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-4">
              <div className="flex items-center gap-2 text-sm">
                <Link href={`/u/${p.author.handle}`} className="font-semibold hover:text-accent">
                  {p.author.displayName}
                </Link>
                <span className="text-xs text-muted">{ago(p.createdAt)}</span>
                {p.viewerCanDelete ? (
                  <button type="button" onClick={() => void act(() => remove({ variables: { postId: p.id } }))} aria-label={t('deletePost')} className="ml-auto rounded-lg p-1.5 text-muted hover:bg-surface-2 hover:text-red-600">
                    <Trash2 className="size-4" aria-hidden />
                  </button>
                ) : null}
              </div>
              <RichDoc doc={p.body as Doc} className="text-sm" />
              <PostComments type="CLASSROOM_POST" id={p.id} count={p.discussion.commentCount} />
            </li>
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
                prev.classroom?.posts && fetchMoreResult.classroom?.posts ? { classroom: { ...fetchMoreResult.classroom, posts: { ...fetchMoreResult.classroom.posts, edges: [...prev.classroom.posts.edges, ...fetchMoreResult.classroom.posts.edges] } } } : fetchMoreResult,
            })
          }>
          {t('older')}
        </Button>
      ) : null}
    </div>
  )
}

function SharedNotes({ classroom }: { classroom: ClassroomDetailFragment }) {
  const t = useTranslations('classes')
  const { data, refetch } = useQuery(ClassroomNotesDocument, { variables: { id: classroom.id }, fetchPolicy: 'cache-and-network' })
  const staff = classroom.viewerCan.post
  const mine = useQuery(MyNotesDocument, { variables: { first: 50 }, fetchPolicy: 'cache-and-network', skip: !staff })
  const [share] = useMutation(ShareNoteToClassroomDocument)
  const [chosen, setChosen] = useState('')
  const [error, setError] = useState<string | null>(null)
  const notes = data?.classroom?.sharedNotes?.edges.map((e) => e.node) ?? []
  const shared = new Set(notes.map((n) => n.id))
  const choices = (mine.data?.myNotes.edges.map((e) => e.node) ?? []).filter((n) => !shared.has(n.id))
  return (
    <div className="flex flex-col gap-4">
      {staff ? (
        <>
          <form
            className="flex flex-wrap items-end gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              if (!chosen) return
              void attempt(() => share({ variables: { noteId: chosen, classroomId: classroom.id } }), t('failed')).then((p) => {
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
        </>
      ) : null}
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

function People({ classroom, onChanged }: { classroom: ClassroomDetailFragment; onChanged: () => void }) {
  const t = useTranslations('classes')
  const { data, refetch } = useQuery(ClassroomPeopleDocument, { variables: { id: classroom.id }, fetchPolicy: 'cache-and-network' })
  const [invite, inviting] = useMutation(InviteToClassroomDocument)
  const [setRole] = useMutation(SetClassroomRoleDocument)
  const [remove] = useMutation(RemoveClassroomMemberDocument)
  const [person, setPerson] = useState('')
  const [as, setAs] = useState<'STUDENT' | 'TA'>('STUDENT')
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  const teacher = classroom.viewerCan.manage
  const act = async (fn: Run) => {
    const problem = await attempt(fn, t('failed'))
    setMessage(problem ? { ok: false, text: problem } : null)
    await refetch()
    onChanged()
  }
  return (
    <div className="flex flex-col gap-4">
      <form
        className="flex flex-col gap-2 rounded-2xl border border-border bg-surface p-3"
        onSubmit={(e) => {
          e.preventDefault()
          void attempt(() => invite({ variables: { classroomId: classroom.id, person: person.trim(), role: as } }), t('failed')).then((problem) => {
            setMessage(problem ? { ok: false, text: problem } : { ok: true, text: t('inviteSent') })
            if (!problem) setPerson('')
          })
        }}
      >
        <span className="text-sm font-semibold">{t('invite')}</span>
        <div className="flex flex-wrap gap-2">
          <label className="min-w-0 flex-1">
            <span className="sr-only">{t('inviteLabel')}</span>
            <input value={person} onChange={(e) => setPerson(e.target.value)} placeholder={t('inviteLabel')} autoComplete="off" className="h-10 w-full rounded-xl border border-border bg-bg px-3 text-sm" />
          </label>
          {teacher ? (
            <label>
              <span className="sr-only">{t('inviteAs')}</span>
              <select value={as} onChange={(e) => setAs(e.target.value as 'STUDENT' | 'TA')} className="h-10 rounded-xl border border-border bg-bg px-2 text-sm">
                <option value="STUDENT">{t('role.STUDENT')}</option>
                <option value="TA">{t('role.TA')}</option>
              </select>
            </label>
          ) : null}
          <Button type="submit" size="sm" className="h-10" disabled={inviting.loading || !person.trim()}>
            {t('inviteSend')}
          </Button>
        </div>
      </form>
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-red-600 dark:text-red-400'}>
          {message.text}
        </p>
      ) : null}
      <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border bg-surface">
        {(data?.classroom?.members ?? []).map((m) => (
          <li key={m.user.id} className="flex flex-wrap items-center gap-3 px-4 py-3">
            <Link href={`/u/${m.user.handle}`} className="flex min-w-0 flex-1 flex-col hover:text-accent">
              <span className="truncate font-semibold">{m.user.displayName}</span>
              <span className="truncate text-xs text-muted">{t(`role.${m.role}`)}</span>
            </Link>
            {teacher && m.role !== 'TEACHER' ? (
              <>
                <label>
                  <span className="sr-only">{t('roleFor', { name: m.user.displayName })}</span>
                  <select
                    value={m.role}
                    onChange={(e) => {
                      const role = e.target.value as 'TEACHER' | 'TA' | 'STUDENT'
                      if (role === 'TEACHER' && !window.confirm(t('handOverConfirm', { name: m.user.displayName }))) return
                      void act(() => setRole({ variables: { classroomId: classroom.id, userId: m.user.id, role } }))
                    }}
                    className="h-9 rounded-lg border border-border bg-bg px-2 text-xs"
                  >
                    <option value="STUDENT">{t('role.STUDENT')}</option>
                    <option value="TA">{t('role.TA')}</option>
                    <option value="TEACHER">{t('makeTeacher', { name: m.user.displayName })}</option>
                  </select>
                </label>
                <Button variant="secondary" size="sm" onClick={() => void act(() => remove({ variables: { classroomId: classroom.id, userId: m.user.id } }))}>
                  {t('remove')}
                </Button>
              </>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  )
}

function Requests({ classroom, onChanged }: { classroom: ClassroomDetailFragment; onChanged: () => void }) {
  const t = useTranslations('classes')
  const { data, refetch } = useQuery(ClassroomPeopleDocument, { variables: { id: classroom.id }, fetchPolicy: 'cache-and-network' })
  const [review] = useMutation(ReviewClassroomJoinRequestDocument)
  const [error, setError] = useState<string | null>(null)
  const requests = data?.classroom?.joinRequests ?? []
  const decide = async (requestId: string, decision: 'APPROVED' | 'REJECTED') => {
    setError(await attempt(() => review({ variables: { requestId, decision } }), t('failed')))
    await refetch()
    onChanged()
  }
  if (!requests.length) return <p className="rounded-2xl border border-dashed border-border px-6 py-8 text-center text-muted">{t('noRequests')}</p>
  return (
    <div className="flex flex-col gap-2">
      {error ? (
        <p role="alert" className="text-sm text-red-600 dark:text-red-400">
          {error}
        </p>
      ) : null}
      <ul className="flex flex-col gap-2">
        {requests.map((r) => (
          <li key={r.id} className="flex flex-wrap items-center gap-3 rounded-2xl border border-border bg-surface px-4 py-3">
            <span className="flex min-w-0 flex-1 flex-col">
              <Link href={`/u/${r.user.handle}`} className="font-semibold hover:text-accent">
                {r.user.displayName}
              </Link>
              <span className="text-xs text-muted">
                {t(`via.${r.via}`)} · {ago(r.createdAt)}
              </span>
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
    </div>
  )
}

function Settings({ classroom, onSaved }: { classroom: ClassroomDetailFragment; onSaved: () => void }) {
  const t = useTranslations('classes')
  const router = useRouter()
  const [update, updating] = useMutation(UpdateClassroomDocument)
  const [del] = useMutation(DeleteClassroomDocument)
  const [name, setName] = useState(classroom.name)
  const [description, setDescription] = useState(classroom.description ?? '')
  const [message, setMessage] = useState<{ ok: boolean; text: string } | null>(null)
  const save = async (newCode = false) => {
    const problem = await attempt(() => update({ variables: { input: { classroomId: classroom.id, name, description: description || null, newCode } } }), t('failed'))
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
      {message ? (
        <p role={message.ok ? 'status' : 'alert'} className={message.ok ? 'text-sm text-accent' : 'text-sm text-red-600 dark:text-red-400'}>
          {message.text}
        </p>
      ) : null}
      <div className="flex flex-wrap justify-between gap-2">
        <div className="flex flex-wrap gap-2">
          <Button type="submit" disabled={updating.loading}>
            {t('save')}
          </Button>
          <Button
            type="button"
            variant="secondary"
            className="gap-1.5"
            onClick={() => {
              if (window.confirm(t('newCodeConfirm'))) void save(true)
            }}
          >
            <RefreshCw className="size-4" aria-hidden />
            {t('newCode')}
          </Button>
        </div>
        <Button
          type="button"
          className="bg-red-600 text-white hover:bg-red-700"
          onClick={() => {
            if (!window.confirm(t('deleteConfirm', { name: classroom.name }))) return
            void del({ variables: { classroomId: classroom.id } }).then(() => router.push('/classes'))
          }}
        >
          {t('delete')}
        </Button>
      </div>
    </form>
  )
}
