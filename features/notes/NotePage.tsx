'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import type { Editor } from '@tiptap/react'
import { Folder, Hash, History, Rocket, Share2, SlidersHorizontal, Trash2, BookMarked, GitFork } from 'lucide-react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useMemo, useState } from 'react'
import type { CardType } from '@/lib/contracts/domain/enums'
import { Button } from '@/components/ui/button'
import { LoadFailed } from '@/components/ui/query-state'
import { DeleteNoteDocument, PublishNoteDocument, ViewerDocument } from '@/graphql/generated/graphql'
import { trackUsage } from '@/lib/analytics'
import { sendSave, type NoteMeta } from './api'
import { NoteDetailsDialog } from './NoteDetailsDialog'
import { NoteReader } from './NoteReader'
import { ModerationBanner } from '@/features/moderation/ModerationBanner'
import { MediaProvider } from './media'
import { ForkCredit, ShareDialog, VisibilityBadge, useMakeCopy } from './ShareDialog'
import { VersionsDialog } from './VersionsDialog'
import { celebrate } from './celebrate'
import { NoteEditor } from './editor/NoteEditor'
import { savedFromMirror } from './editor/mirror'
import { cardsToDoc, docToCards } from './model/doc'
import { insertCardAfter } from './editor/nodes'
import { Breadcrumb } from './view/Breadcrumb'
import { NoteTabPanel, NoteTabs, useNoteTab } from './view/NoteTabs'
import { offeredTabs } from './view/offered'
import { CardsTab, SummaryTab, useNoteStudy } from './view/StudyTabs'
import { savedStateOf } from './model/save'
import { useLoadedNote } from './useLoadedNote'
import { Discussion } from '@/features/discussion/Discussion'
import { AiButton, AiPanel } from '@/features/ai/AiPanel'
import { AiDock, useWide } from '@/features/ai/AiDock'
import { useLearningTime } from '@/features/learning/useLearningTime'

/** A note: the editor for its owner and editors, the reader for everyone else (loading: ./useLoadedNote). */
export function NotePage({ id }: { id: string }) {
  const t = useTranslations('notes')
  const tAi = useTranslations('ai')
  const client = useApolloClient()
  const router = useRouter()
  const viewer = useQuery(ViewerDocument)
  const userId = viewer.data?.viewer?.id
  useEffect(() => {
    trackUsage('note_open')
  }, [id])
  const [generation, setGeneration] = useState(0)
  const [loaded, setLoaded] = useLoadedNote(id, userId, generation)
  const [versionsOpen, setVersionsOpen] = useState<{ open: boolean; versionId?: string }>({ open: false })
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [shareOpen, setShareOpen] = useState(false)
  // Notes from photos (ADR-0084) opens the note with its AI panel, where the new notes arrive; once.
  const askedAi = useSearchParams().get('ai') === '1'
  const [aiOpen, setAiOpen] = useState(askedAi)
  useEffect(() => {
    if (!askedAi) return
    const url = new URL(window.location.href)
    url.searchParams.delete('ai')
    window.history.replaceState(window.history.state, '', url)
  }, [askedAi])
  const copy = useMakeCopy(id)
  const [publish, publishing] = useMutation(PublishNoteDocument)
  const [trash] = useMutation(DeleteNoteDocument)
  const [notice, setNotice] = useState<string | null>(null)
  const [editor, setEditor] = useState<Editor | null>(null)
  const study = useNoteStudy(id)
  const wide = useWide()
  const ready = loaded.state === 'ready' ? loaded : null
  // The tabs it offers (ADR-0076): each has something, or a way to make something.
  const offered = offeredTabs({
    canEdit: !!ready?.meta.viewerCan.edit,
    reader: ready?.meta.viewerAccess === 'READER',
    published: !!ready?.meta.publishedVersion,
    ai: study.ai.available,
    cardTypes: (ready?.cards ?? []).map((c) => c.type),
    tasks: study.tasks,
  })
  const [tab, chooseTab] = useNoteTab(offered)

  const reload = useCallback(() => setGeneration((g) => g + 1), [])
  // Learning history (lvn-backend ADR-0067): the note opened, and the time it is read.
  useLearningTime(loaded.state === 'ready' ? { entityType: 'NOTE', entityId: id, topicKeys: loaded.meta.topics?.map((t) => `topic:${t.id}`) } : null, 'NOTE_OPENED')

  const onNote = useCallback((meta: NoteMeta) => setLoaded((l) => (l.state === 'ready' ? { ...l, meta } : l)), [setLoaded])
  const send = useMemo(() => sendSave(client, onNote), [client, onNote])

  // The note is asked for once the viewer is known; when the viewer cannot be, nor can the note.
  if (!userId && viewer.error && !viewer.loading) return <LoadFailed className="mx-auto my-16 max-w-md" onRetry={viewer.refetch} />
  if (loaded.state === 'loading' || !userId) return <p role="status" className="py-16 text-center text-sm text-muted">{t('loading')}</p>
  if (loaded.state === 'failed') return <LoadFailed className="mx-auto my-16 max-w-md" onRetry={reload} />
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
  if (meta.viewerAccess === 'READER') {
    return (
      <MediaProvider noteId={null} cards={loaded.media} readNoteId={id}>
        <NoteReader meta={meta} cards={loaded.cards} study={study} offered={offered} tab={tab} onTab={chooseTab} wide={wide} />
      </MediaProvider>
    )
  }

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
    ...(meta.viewerCan.fork ? [{ label: t('share.makeCopy'), icon: GitFork, onClick: () => void copy.makeCopy() }] : []),
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
      <AiButton onClick={() => setAiOpen(true)} />
      {meta.viewerAccess === 'OWNER' ? (
        <Button variant="secondary" size="sm" className="gap-1.5" aria-label={t('share.button')} onClick={() => setShareOpen(true)}>
          <Share2 className="size-4" aria-hidden />
          <span className="hidden sm:inline">{t('share.button')}</span>
        </Button>
      ) : null}
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

  const idBase = `note-${id}`
  /** The cards as they are now in the editor (they may have changed since loading). */
  const currentCards = () => (editor ? docToCards(editor.getJSON()) : loaded.cards)
  const addedToNote = () => {
    // The cards are in the draft now: show them (the tab stays open through the reload).
    setAiOpen(false)
    setNotice(tAi('addedToNote'))
    reload()
  }
  // A card added from the Flashcards or Quiz tab is written in the cards, so the cards open with it.
  const addCard = (type: CardType) => {
    chooseTab('content')
    requestAnimationFrame(() => {
      if (!editor) return
      editor.commands.focus('end')
      insertCardAfter(editor, type)
    })
  }
  const tabPanel =
    tab === 'summary' ? (
      <SummaryTab noteId={id} study={study} canEdit={meta.viewerCan.edit} onAddedToNote={addedToNote} />
    ) : tab === 'flashcards' || tab === 'quiz' ? (
      <CardsTab kind={tab} noteId={id} cards={currentCards()} study={study} canEdit={meta.viewerCan.edit} reader={false} onAdd={meta.viewerCan.edit ? addCard : undefined} onAddedToNote={addedToNote} />
    ) : tab === 'discussions' ? (
      // What readers said about the published note (lvn-backend ADR-0047).
      <Discussion target={{ type: 'NOTE', id }} />
    ) : null

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
    <MediaProvider noteId={id} cards={loaded.media} readNoteId={id}>
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between gap-2 text-sm">
          <Breadcrumb meta={meta} own={meta.viewerAccess === 'OWNER'} />
          <span className="flex items-center gap-2 text-xs text-muted">
            {meta.viewerAccess === 'OWNER' ? (
              <button type="button" className="rounded-full hover:ring-1 hover:ring-accent/40" title={t('share.title')} onClick={() => setShareOpen(true)}>
                <VisibilityBadge visibility={meta.visibility} />
              </button>
            ) : null}
            {meta.publishedVersion ? t('publishedVersion', { n: meta.publishedVersion.number }) : t('neverPublished')}
            {meta.viewerAccess === 'EDITOR' ? ` · ${t('editingFor', { name: meta.owner.displayName })}` : ''}
          </span>
        </div>
        {meta.moderation ? <ModerationBanner entityType="NOTE" entityId={id} moderation={meta.moderation} /> : null}
        {meta.forkedFrom ? <ForkCredit credit={meta.forkedFrom} /> : null}
        {copy.copyError ? (
          <p role="alert" className="text-sm text-red-600 dark:text-red-400">
            {copy.copyError}
          </p>
        ) : null}
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
          onAnchor={(anchor, cardId) => router.push(`/notes/${id}/read/${anchor.fileId}?page=${anchor.page}&card=${cardId}`)}
          onEditor={setEditor}
          tabs={<NoteTabs tabs={offered} current={tab} onChange={chooseTab} idBase={idBase} />}
          contentPanel={{ id: `${idBase}-panel-content`, labelledBy: `${idBase}-tab-content` }}
          panel={tab === 'content' ? null : <NoteTabPanel idBase={idBase} tab={tab} current={tab}>{tabPanel}</NoteTabPanel>}
          aside={wide && !aiOpen ? <AiDock noteId={id} study={study} canEdit={meta.viewerCan.edit} canFork={meta.viewerCan.fork} hasCode={currentCards().some((c) => c.type === 'code')} onAddedToNote={addedToNote} /> : null}
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
        <AiPanel
          noteId={id}
          open={aiOpen}
          onClose={() => setAiOpen(false)}
          canEdit={meta.viewerCan.edit}
          canFork={meta.viewerCan.fork}
          onAddedToNote={addedToNote}
          onTextMended={(applied, refused) => {
            // Clean-up changed cards' words (ADR-0063): show them.
            setAiOpen(false)
            setNotice([tAi('cleanUp.done', { n: applied }), refused ? tAi('cleanUp.refused', { n: refused }) : null].filter(Boolean).join(' '))
            reload()
          }}
        />
        {meta.viewerAccess === 'OWNER' ? <ShareDialog meta={meta} open={shareOpen} onClose={() => setShareOpen(false)} onSaved={onNote} /> : null}
        {meta.viewerAccess === 'OWNER' ? <NoteDetailsDialog meta={meta} open={detailsOpen} onClose={() => setDetailsOpen(false)} onSaved={onNote} /> : null}
      </div>
    </MediaProvider>
  )
}
