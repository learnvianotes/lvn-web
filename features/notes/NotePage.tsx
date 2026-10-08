'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import { ArrowLeft, Folder, Hash, History, Rocket, SlidersHorizontal, Trash2, BookMarked } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { DeleteNoteDocument, PublishNoteDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { loadNote, sendSave, type NoteMeta } from './api'
import { NoteDetailsDialog } from './NoteDetailsDialog'
import { NoteReader } from './NoteReader'
import { VersionsDialog } from './VersionsDialog'
import { celebrate } from './celebrate'
import { NoteEditor } from './editor/NoteEditor'
import { readMirror, removeMirror, savedFromMirror } from './editor/mirror'
import { cardsToDoc, docToCards, type StoredCard } from './model/doc'
import { planSave, savedStateOf } from './model/save'

type Loaded =
  | { state: 'loading' }
  | { state: 'missing' }
  | { state: 'ready'; meta: NoteMeta; cards: StoredCard[]; mirror: Awaited<ReturnType<typeof readMirror>>; offline: boolean }

/**
 * A note: the editor for its owner and editors, the reader for everyone else. Edits a previous visit left in this
 * browser (the IndexedDB mirror) are sent first; when that is impossible (offline), the editor opens on them.
 */
export function NotePage({ id }: { id: string }) {
  const t = useTranslations('notes')
  const client = useApolloClient()
  const router = useRouter()
  const viewer = useQuery(ViewerDocument)
  const userId = viewer.data?.viewer?.id
  const [loaded, setLoaded] = useState<Loaded>({ state: 'loading' })
  const [generation, setGeneration] = useState(0)
  const [versionsOpen, setVersionsOpen] = useState<{ open: boolean; versionId?: string }>({ open: false })
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [publish, publishing] = useMutation(PublishNoteDocument)
  const [trash] = useMutation(DeleteNoteDocument)
  const [notice, setNotice] = useState<string | null>(null)

  const reload = useCallback(() => setGeneration((g) => g + 1), [])

  useEffect(() => {
    if (!userId) return
    let cancelled = false
    void (async () => {
      setLoaded({ state: 'loading' })
      const mirror = await readMirror(userId, id)
      let offline = false
      // Kept when it could not be sent: the editor opens on it and its autosave tries again.
      let keep = false
      if (mirror) {
        const plan = planSave(savedFromMirror(mirror), mirror.title, docToCards(mirror.doc))
        try {
          const res = plan.ops.length || plan.title !== undefined ? await sendSave(client, () => {})({ noteId: id, ...(plan.title !== undefined ? { title: plan.title } : {}), ops: plan.ops }) : null
          if (res?.userErrors.length) keep = true
          else await removeMirror(userId, id)
        } catch {
          offline = true
          keep = true
        }
      }
      let note: Awaited<ReturnType<typeof loadNote>> = null
      try {
        note = await loadNote(client, id)
      } catch {
        offline = true
      }
      if (cancelled) return
      if (!note && mirror && offline) {
        // Offline with a local copy: open the editor on it; the autosave sends it when the connection is back.
        setLoaded({ state: 'ready', meta: mirrorMeta(id, mirror.title), cards: [], mirror, offline: true })
        return
      }
      if (!note) return setLoaded({ state: 'missing' })
      setLoaded({ state: 'ready', meta: note.meta, cards: note.cards, mirror: keep ? mirror : null, offline })
    })()
    return () => {
      cancelled = true
    }
  }, [client, id, userId, generation])

  const onNote = useCallback((meta: NoteMeta) => setLoaded((l) => (l.state === 'ready' ? { ...l, meta } : l)), [])
  const send = useMemo(() => sendSave(client, onNote), [client, onNote])

  if (loaded.state === 'loading' || !userId) return <p role="status" className="py-16 text-center text-sm text-muted">{t('loading')}</p>
  if (loaded.state === 'missing') {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center gap-3 py-16 text-center">
        <h1 className="text-2xl font-bold">{t('notFound')}</h1>
        <p className="text-sm text-muted">{t('notFoundLead')}</p>
        <Link href="/notes" className="text-accent hover:underline">
          {t('backToNotes')}
        </Link>
      </div>
    )
  }
  const { meta } = loaded
  if (meta.viewerAccess === 'READER') return <NoteReader meta={meta} cards={loaded.cards} />

  const doPublish = async (event: React.MouseEvent) => {
    const first = !meta.publishedVersion
    const origin = { x: event.clientX, y: event.clientY }
    const res = await publish({ variables: { noteId: id } }).catch(() => null)
    const payload = res?.data?.publishNote
    if (payload?.note) {
      onNote(payload.note)
      setNotice(t('published', { n: payload.note.publishedVersion?.number ?? 1 }))
      if (first) celebrate(origin)
    } else setNotice(payload?.userErrors[0]?.message ?? t('publishFailed'))
  }

  const moveToTrash = async () => {
    if (!window.confirm(t('trashConfirm'))) return
    await trash({ variables: { noteId: id } })
    router.push('/notes')
  }
  const menuItems = [
    ...(meta.viewerAccess === 'OWNER' ? [{ label: t('details.button'), icon: SlidersHorizontal, onClick: () => setDetailsOpen(true) }] : []),
    { label: t('versions.button'), icon: History, onClick: () => setVersionsOpen({ open: true }) },
    ...(meta.viewerCan.delete ? [{ label: t('trash'), icon: Trash2, onClick: () => void moveToTrash(), danger: true }] : []),
  ]

  const actions = (
    <>
      {meta.viewerAccess === 'OWNER' ? (
        <Button variant="secondary" size="sm" className="hidden gap-1.5 sm:inline-flex" onClick={() => setDetailsOpen(true)}>
          <SlidersHorizontal className="size-4" aria-hidden />
          {t('details.button')}
        </Button>
      ) : null}
      <Button variant="secondary" size="sm" className="hidden gap-1.5 sm:inline-flex" onClick={() => setVersionsOpen({ open: true })}>
        <History className="size-4" aria-hidden />
        {t('versions.button')}
      </Button>
      {meta.viewerAccess === 'OWNER' ? (
        <Button size="sm" className="gap-1.5 shadow-md shadow-accent/25" disabled={!meta.viewerCan.publish || publishing.loading} title={meta.viewerCan.publish ? t('publishHint') : t('verifyToPublish')} onClick={(e) => void doPublish(e)}>
          <Rocket className="size-4" aria-hidden />
          {t('publish')}
        </Button>
      ) : null}
      {meta.viewerCan.delete ? (
        <Button variant="ghost" size="icon" className="hidden sm:inline-flex" aria-label={t('trash')} title={t('trash')} onClick={() => void moveToTrash()}>
          <Trash2 className="size-4" aria-hidden />
        </Button>
      ) : null}
    </>
  )

  const chips =
    meta.viewerAccess === 'OWNER' ? (
      <button type="button" onClick={() => setDetailsOpen(true)} className="flex flex-wrap items-center gap-1.5 text-left text-xs text-muted">
        <span className="inline-flex items-center gap-1 rounded-full border border-border bg-surface px-2.5 py-1 hover:border-accent hover:text-accent">
          <Folder className="size-3.5" aria-hidden />
          {meta.folder?.name ?? t('details.noFolder')}
        </span>
        {meta.tags.map((x) => (
          <span key={x.id} className="inline-flex items-center gap-0.5 rounded-full bg-accent-soft px-2.5 py-1 text-accent">
            <Hash className="size-3" aria-hidden />
            {x.name}
          </span>
        ))}
        {meta.topics.map((x) => (
          <span key={x.id} className="inline-flex items-center gap-1 rounded-full border border-border bg-surface px-2.5 py-1">
            <BookMarked className="size-3.5" aria-hidden />
            {x.title}
          </span>
        ))}
        {!meta.tags.length && !meta.topics.length ? <span className="px-1 hover:text-accent">{t('addTagsTopics')}</span> : null}
      </button>
    ) : null

  return (
    <div className="flex flex-col gap-3">
      <nav className="flex items-center justify-between gap-2 text-sm">
        <Link href="/notes" className="inline-flex items-center gap-1.5 rounded-full px-2 py-1 text-muted transition hover:bg-surface-2 hover:text-fg">
          <ArrowLeft className="size-4" aria-hidden />
          {t('backToNotes')}
        </Link>
        <span className="text-xs text-muted">
          {meta.publishedVersion ? t('publishedVersion', { n: meta.publishedVersion.number }) : t('neverPublished')}
          {meta.viewerAccess === 'EDITOR' ? ` · ${t('editingFor', { name: meta.owner.displayName })}` : ''}
        </span>
      </nav>
      {loaded.offline ? <p role="status" className="rounded-xl border border-amber-500/40 bg-amber-50 px-4 py-3 text-sm text-amber-950 dark:bg-amber-950/30 dark:text-amber-100">{t('offlineCopy')}</p> : null}
      {notice ? (
        <p role="status" className="animate-rise rounded-2xl border border-accent/30 bg-accent-soft px-4 py-3 text-sm font-medium">
          {notice}
        </p>
      ) : null}
      {!meta.viewerCan.publish && meta.viewerAccess === 'OWNER' ? (
        <p className="text-xs text-muted">
          {t('verifyToPublish')}{' '}
          <Link href="/profile" className="text-accent hover:underline">
            {t('verifyLink')}
          </Link>
        </p>
      ) : null}
      <NoteEditor
        key={generation}
        noteId={id}
        userId={userId}
        title={loaded.mirror?.title ?? meta.title}
        doc={loaded.mirror?.doc ?? cardsToDoc(loaded.cards)}
        saved={loaded.mirror ? savedFromMirror(loaded.mirror) : savedStateOf(meta.title, loaded.cards)}
        send={send}
        actions={actions}
        meta={chips}
        menuItems={menuItems}
        onOpenVersion={(versionId) => setVersionsOpen({ open: true, versionId })}
      />
      <VersionsDialog
        noteId={id}
        open={versionsOpen.open}
        initialVersionId={versionsOpen.versionId}
        onClose={() => setVersionsOpen({ open: false })}
        onRestored={() => {
          setVersionsOpen({ open: false })
          reload()
        }}
      />
      {meta.viewerAccess === 'OWNER' ? <NoteDetailsDialog meta={meta} open={detailsOpen} onClose={() => setDetailsOpen(false)} onSaved={onNote} /> : null}
    </div>
  )
}

/** What the page shows about a note while offline with only its local copy. */
function mirrorMeta(id: string, title: string): NoteMeta {
  return {
    id,
    title,
    slug: '',
    kind: 'NOTE',
    visibility: 'PRIVATE',
    viewerAccess: 'OWNER',
    viewerCan: { edit: true, publish: false, changeVisibility: false, delete: false, share: false, fork: false },
    owner: { id: '', displayName: '', handle: '' },
    folder: null,
    tags: [],
    topics: [],
    draftRevision: null,
    draftUpdatedAt: null,
    publishedAt: null,
    publishedVersion: null,
    forkingEnabled: true,
    cardCount: 0,
    deletedAt: null,
  }
}
