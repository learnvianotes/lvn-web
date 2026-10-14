'use client'

import { useApolloClient, useMutation, useQuery } from '@apollo/client/react'
import type { Editor } from '@tiptap/react'
import { ArrowLeft, Crop, Highlighter, ListTree, Minus, NotebookPen, PanelRightClose, PanelRightOpen, Plus, Search, StretchHorizontal, Wand2, X } from 'lucide-react'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  AddPdfHighlightDocument,
  NoteFileDocument,
  NoteHighlightsDocument,
  NotePdfConversionDocument,
  RemovePdfHighlightDocument,
  StudyPdfDocument,
  UpdatePdfHighlightDocument,
  ViewerDocument,
  type HighlightColor,
  type HighlightFieldsFragment,
} from '@/graphql/generated/graphql'
import { cardAnchor, type CardAnchor } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { sendSave, type NoteMeta } from '@/features/notes/api'
import { savedFromMirror } from '@/features/notes/editor/mirror'
import { NoteEditor } from '@/features/notes/editor/NoteEditor'
import { MediaProvider, pendingFiles } from '@/features/notes/media'
import { cardsToDoc, cardToNode, newCardId, type CardType } from '@/features/notes/model/doc'
import { savedStateOf } from '@/features/notes/model/save'
import { CardView } from '@/features/notes/render/CardView'
import { useLoadedNote } from '@/features/notes/useLoadedNote'
import type { PageRect } from './geometry'
import { ACTIVE, ConversionBanner, ConvertDialog } from './convert'
import { AreaActions, FindBar, HighlightCard, HighlightsList, OutlineList, SelectionActions, ToolButton } from './parts'
import { PdfViewer, type AreaSelection, type Mark, type OutlineItem, type PdfViewerHandle, type TextSelection } from './PdfViewer'

type Panel = 'notes' | 'highlights' | 'contents'
type Anchored = { cardId: string; anchor: CardAnchor }

const positionKey = (fileId: string) => `lvn.reader.page.${fileId}`
const paragraph = (text: string) => ({ type: 'doc', content: [{ type: 'paragraph', content: [{ type: 'text', text }] }] })

/**
 * The PDF reader (lvn-backend ADR-0040): a PDF of a note on one side and the note on the other — beside it on wide
 * screens, in a sheet on phones. Owners and editors highlight passages and areas in colours with comments, add a
 * passage (as a quote) or a snipped area (as a picture) to the note with its page, and write their own cards; a
 * card's page chip scrolls the PDF back to where it came from. Readers read the PDF with the published cards beside
 * it and can start notes of their own on it.
 */
export function ReaderPage({ noteId, fileId }: { noteId: string; fileId: string }) {
  const t = useTranslations('reader')
  const client = useApolloClient()
  const router = useRouter()
  const params = useSearchParams()
  const viewerQuery = useQuery(ViewerDocument)
  const userId = viewerQuery.data?.viewer?.id
  const [generation, setGeneration] = useState(0)
  const [loaded, setLoaded] = useLoadedNote(noteId, userId, generation)
  const file = useQuery(NoteFileDocument, { variables: { noteId, fileId }, fetchPolicy: 'network-only' })
  const ready = loaded.state === 'ready'
  const editable = ready && loaded.meta.viewerAccess !== 'READER'

  const pdf = useRef<PdfViewerHandle>(null)
  const [pdfState, setPdfState] = useState<'loading' | 'ready' | 'failed' | 'password'>('loading')
  const [pages, setPages] = useState(0)
  const [page, setPage] = useState(1)
  const [scale, setScale] = useState(100)
  const [outline, setOutline] = useState<OutlineItem[]>([])
  const [panel, setPanel] = useState<Panel>('notes')
  const [panelOpen, setPanelOpen] = useState(false)
  const [findOpen, setFindOpen] = useState(false)
  const [found, setFound] = useState<{ current: number; total: number } | null>(null)
  const [snipping, setSnipping] = useState(false)
  const [selection, setSelection] = useState<TextSelection | null>(null)
  const [area, setArea] = useState<AreaSelection | null>(null)
  const [busy, setBusy] = useState(false)
  const [active, setActive] = useState<{ id: string; at: { x: number; y: number } } | null>(null)
  const [highlights, setHighlights] = useState<HighlightFieldsFragment[]>([])
  const [notice, setNotice] = useState<{ text: string; action?: { label: string; run: () => void } } | null>(null)
  const [editor, setEditor] = useState<Editor | null>(null)
  const [anchors, setAnchors] = useState<Anchored[]>([])
  const [target, setTarget] = useState<{ page: number; cardId: string | null } | null>(() => {
    const p = Number(params.get('page'))
    return p >= 1 ? { page: p, cardId: params.get('card') } : null
  })
  const [initialPage] = useState(() => {
    const p = Number(params.get('page'))
    if (p >= 1) return p
    try {
      return Number(localStorage.getItem(positionKey(fileId))) || 1
    } catch {
      return 1
    }
  })

  const [convertOpen, setConvertOpen] = useState(false)
  const [bannerHidden, setBannerHidden] = useState(false)
  const conversionQuery = useQuery(NotePdfConversionDocument, { variables: { id: noteId }, skip: !userId, fetchPolicy: 'network-only' })
  const conversion = conversionQuery.data?.note?.pdfConversion ?? null
  const converting = !!conversion && ACTIVE.includes(conversion.status)
  // While the engine works the note's cards are on their way: check every two seconds, then load them.
  const wasConverting = useRef(false)
  const { startPolling, stopPolling } = conversionQuery
  useEffect(() => {
    if (!converting) return stopPolling()
    wasConverting.current = true
    startPolling(2000)
    return () => stopPolling()
  }, [converting, startPolling, stopPolling])
  useEffect(() => {
    if (!converting && wasConverting.current) {
      wasConverting.current = false
      setGeneration((g) => g + 1)
    }
  }, [converting])

  const [addHighlight] = useMutation(AddPdfHighlightDocument)
  const [updateHighlight] = useMutation(UpdatePdfHighlightDocument)
  const [removeHighlight] = useMutation(RemovePdfHighlightDocument)
  const [study, studying] = useMutation(StudyPdfDocument)

  // The reader takes the whole window; the page under it does not scroll.
  useEffect(() => {
    const before = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    if (window.matchMedia('(min-width: 1024px)').matches) setPanelOpen(true)
    return () => {
      document.body.style.overflow = before
    }
  }, [])

  useEffect(() => {
    if (!notice) return
    const timer = setTimeout(() => setNotice(null), 4000)
    return () => clearTimeout(timer)
  }, [notice])

  useEffect(() => {
    if (!editable) return
    client
      .query({ query: NoteHighlightsDocument, variables: { id: noteId, fileId }, fetchPolicy: 'network-only' })
      .then((r) => setHighlights(r.data?.note?.highlights ?? []))
      .catch(() => setNotice({ text: t('highlightsFailed') }))
  }, [client, editable, noteId, fileId, t])

  // Cards made from this PDF: from the editor as it changes, or the published cards for readers.
  useEffect(() => {
    if (!editor) return
    const read = () => {
      const list: Anchored[] = []
      editor.state.doc.forEach((node) => {
        const anchor = node.attrs.anchor as CardAnchor | null
        if (anchor?.fileId === fileId && node.attrs.id) list.push({ cardId: node.attrs.id as string, anchor })
      })
      setAnchors((prev) => (JSON.stringify(prev) === JSON.stringify(list) ? prev : list))
    }
    read()
    editor.on('update', read)
    return () => {
      editor.off('update', read)
    }
  }, [editor, fileId])
  const readerAnchors = useMemo<Anchored[]>(
    () =>
      ready && !editable
        ? loaded.cards.flatMap((c) => {
            const anchor = cardAnchor(c.content)
            return anchor?.fileId === fileId ? [{ cardId: c.id, anchor }] : []
          })
        : [],
    [ready, editable, loaded, fileId],
  )
  const anchored = editable ? anchors : readerAnchors

  const marks = useMemo<Mark[]>(
    () => [
      ...highlights.map((h) => ({ id: `h:${h.id}`, page: h.page, rects: h.rects as PageRect[], kind: 'highlight' as const, color: h.color })),
      ...anchored.filter((a) => a.anchor.rects?.length).map((a) => ({ id: `c:${a.cardId}`, page: a.anchor.page, rects: a.anchor.rects as PageRect[], kind: 'anchor' as const })),
      ...(area ? [{ id: 'pending', page: area.page, rects: [area.rect], kind: 'pending' as const }] : []),
    ],
    [highlights, anchored, area],
  )

  // Opened from a card's page chip: go to its passage once the PDF and the cards are there.
  useEffect(() => {
    if (pdfState !== 'ready' || !target) return
    const card = target.cardId ? anchored.find((a) => a.cardId === target.cardId) : undefined
    // Wait for the cards: the editor's, or the published ones.
    if (target.cardId && !card && (editable ? !editor : !ready)) return
    pdf.current?.goTo(card?.anchor.page ?? target.page, card?.anchor.rects as PageRect[] | undefined)
    setTarget(null)
  }, [pdfState, target, anchored, ready, editable, editor])

  const onPage = useCallback(
    (p: number) => {
      setPage(p)
      try {
        localStorage.setItem(positionKey(fileId), String(p))
      } catch {
        // private browsing: the position is not kept
      }
    },
    [fileId],
  )

  const wide = () => window.matchMedia('(min-width: 1024px)').matches
  const showCard = useCallback(
    (cardId: string) => {
      setPanel('notes')
      setPanelOpen(true)
      requestAnimationFrame(() => {
        let el: HTMLElement | null = null
        if (editor) {
          editor.state.doc.forEach((node, offset) => {
            if (node.attrs.id === cardId) el = editor.view.nodeDOM(offset) as HTMLElement | null
          })
        } else el = document.querySelector<HTMLElement>(`[data-card-id="${cardId}"]`)
        const card = el as HTMLElement | null
        if (!card) return
        card.scrollIntoView({ block: 'center', behavior: 'smooth' })
        card.classList.remove('lvn-card-flash')
        void card.offsetWidth
        card.classList.add('lvn-card-flash')
      })
    },
    [editor],
  )

  const openAnchor = useCallback(
    (anchor: CardAnchor, cardId: string) => {
      if (anchor.fileId !== fileId) return router.push(`/notes/${noteId}/read/${anchor.fileId}?page=${anchor.page}&card=${cardId}`)
      if (!wide()) setPanelOpen(false)
      pdf.current?.goTo(anchor.page, anchor.rects as PageRect[] | undefined)
    },
    [fileId, noteId, router],
  )

  /** Adds a card at the end of the note (in place of an empty last text card); returns its id. */
  const addCard = (type: CardType, content: unknown, upload?: File): string | null => {
    if (!editor) return null
    const id = newCardId()
    const node = cardToNode({ id, type, content })
    if (upload) {
      const key = newCardId()
      pendingFiles.set(key, upload)
      node.attrs = { ...node.attrs, upload: key }
    }
    const doc = editor.state.doc
    const last = doc.lastChild
    const replaceLast = last?.type.name === 'textCard' && !last.textContent.trim() && doc.childCount > 0
    const from = replaceLast ? doc.content.size - last!.nodeSize : doc.content.size
    editor.chain().insertContentAt({ from, to: doc.content.size }, node).run()
    setNotice({ text: t('added'), action: wide() ? undefined : { label: t('openNotes'), run: () => showCard(id) } })
    if (wide()) showCard(id)
    return id
  }

  const failed = (message?: string | null) => setNotice({ text: message ?? t('saveFailed') })

  const highlight = async (input: { page: number; kind: 'TEXT' | 'AREA'; rects: PageRect[]; quote?: string; color: HighlightColor; cardId?: string | null }) => {
    const res = await addHighlight({ variables: { input: { noteId, fileId, ...input } } }).catch(() => null)
    const made = res?.data?.addPdfHighlight.highlight
    if (made) setHighlights((list) => [...list, made])
    else failed(res?.data?.addPdfHighlight.userErrors[0]?.message)
    return made ?? null
  }

  const change = async (id: string, input: { color?: HighlightColor; comment?: string; cardId?: string | null }) => {
    const res = await updateHighlight({ variables: { input: { highlightId: id, ...input } } }).catch(() => null)
    const changed = res?.data?.updatePdfHighlight.highlight
    if (changed) setHighlights((list) => list.map((h) => (h.id === id ? changed : h)))
    else failed(res?.data?.updatePdfHighlight.userErrors[0]?.message)
  }

  const quoteCard = (page: number, rects: PageRect[], quote: string) => addCard('quote', { doc: paragraph(quote), anchor: { fileId, page, rects, quote } })

  const pictureCard = async (page: number, rect: PageRect) => {
    const blob = await pdf.current!.crop(page, rect)
    const name = loaded.state === 'ready' ? loaded.meta.title || 'pdf' : 'pdf'
    return addCard('image', { alt: t('snipAlt', { page, name: fileName }), anchor: { fileId, page, rects: [rect] } }, new File([blob], `${name.slice(0, 60)} p${page}.png`, { type: 'image/png' }))
  }

  const startStudy = async () => {
    const res = await study({ variables: { noteId, fileId } }).catch((e: unknown) => ({ data: null, error: e }))
    const id = res.data?.studyPdf.note?.id
    if (id) router.push(`/notes/${id}/read/${fileId}`)
    else failed(res.data?.studyPdf.userErrors[0]?.message ?? t('noCopies'))
  }

  const fileName = file.data?.noteFile?.fileName ?? ''
  const activeHighlight = active?.id.startsWith('h:') ? highlights.find((h) => h.id === active.id.slice(2)) : undefined
  const meta: NoteMeta | null = ready ? loaded.meta : null
  const onNote = useCallback((m: NoteMeta) => setLoaded((l) => (l.state === 'ready' ? { ...l, meta: m } : l)), [setLoaded])
  const send = useMemo(() => sendSave(client, onNote), [client, onNote])
  const onEditor = useCallback((e: Editor | null) => setEditor(e), [])

  // ── States without a PDF ─────────────────────────────────────────────────────────────────────────────────
  const fileMissing = !file.loading && !file.data?.noteFile
  if (loaded.state === 'missing' || fileMissing) {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center gap-3 py-16 text-center">
        <h1 className="text-2xl font-bold">{t('notFound')}</h1>
        <Link href={`/notes/${noteId}`} className="text-accent hover:underline">
          {t('back')}
        </Link>
      </div>
    )
  }

  const tab = (id: Panel, label: string, Icon: typeof ListTree) => (
    <button
      type="button"
      role="tab"
      aria-selected={panel === id}
      onClick={() => setPanel(id)}
      className={cn('inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-sm transition', panel === id ? 'bg-accent-soft font-semibold text-accent' : 'text-muted hover:bg-surface-2 hover:text-fg')}
    >
      <Icon className="size-4" aria-hidden />
      {label}
    </button>
  )

  return (
    <MediaProvider noteId={editable ? noteId : null} cards={ready ? loaded.media : []} readNoteId={noteId} readingFileId={fileId}>
      <div className="fixed inset-0 z-50 flex flex-col bg-bg text-fg" data-testid="pdf-reader">
        <header className="flex h-14 shrink-0 items-center gap-1 border-b border-border bg-surface px-2 sm:gap-2 sm:px-3">
          <Link href={`/notes/${noteId}`} aria-label={t('back')} title={t('back')} className="grid size-9 shrink-0 place-items-center rounded-xl text-muted hover:bg-surface-2 hover:text-fg">
            <ArrowLeft className="size-5" aria-hidden />
          </Link>
          <div className="flex min-w-0 flex-1 flex-col leading-tight">
            <h1 className="truncate text-sm font-semibold">{meta?.title || t('untitled')}</h1>
            <p className="truncate text-xs text-muted">{fileName}</p>
          </div>
          <form
            className="flex shrink-0 items-center gap-1 text-sm text-muted"
            onSubmit={(e) => {
              e.preventDefault()
              const n = Number(new FormData(e.currentTarget).get('page'))
              if (n >= 1) pdf.current?.goTo(Math.min(n, pages || n))
            }}
          >
            <label className="sr-only" htmlFor="reader-page">
              {t('page')}
            </label>
            <input key={page} id="reader-page" name="page" inputMode="numeric" defaultValue={page} className="w-11 rounded-lg border border-border bg-bg px-1.5 py-1 text-center text-sm text-fg focus-visible:border-accent focus-visible:outline-none" />
            <span>{t('pageOf', { n: pages || '…' })}</span>
          </form>
          <span className="hidden items-center md:flex">
            <ToolButton icon={Minus} label={t('zoomOut')} onClick={() => pdf.current?.zoom('out')} />
            <span className="w-12 text-center text-xs tabular-nums text-muted">{scale}%</span>
            <ToolButton icon={Plus} label={t('zoomIn')} onClick={() => pdf.current?.zoom('in')} />
            <ToolButton icon={StretchHorizontal} label={t('fitWidth')} onClick={() => pdf.current?.zoom('width')} />
          </span>
          <ToolButton icon={Search} label={t('find')} pressed={findOpen} onClick={() => setFindOpen((o) => !o)} />
          {editable ? (
            <ToolButton
              icon={Crop}
              label={t('snip')}
              pressed={snipping}
              onClick={() => {
                setSnipping((s) => !s)
                setArea(null)
                setSelection(null)
              }}
            />
          ) : null}
          {meta?.viewerCan.fork && !converting ? <ToolButton icon={Wand2} label={t('convert.button')} onClick={() => setConvertOpen(true)} /> : null}
          <ToolButton icon={panelOpen ? PanelRightClose : PanelRightOpen} label={panelOpen ? t('hidePanel') : t('showPanel')} pressed={panelOpen} onClick={() => setPanelOpen((o) => !o)} />
        </header>
        {conversion && !bannerHidden ? <ConversionBanner conversion={conversion} onDismiss={() => setBannerHidden(true)} /> : null}
        {findOpen ? (
          <FindBar
            result={found}
            onFind={(q, direction) => pdf.current?.find(q, direction)}
            onClose={() => {
              setFindOpen(false)
              pdf.current?.find('')
            }}
          />
        ) : null}
        {snipping ? <p className="shrink-0 border-b border-border bg-accent-soft px-3 py-1.5 text-sm text-accent">{t('snipHint')}</p> : null}

        <div className="relative flex min-h-0 flex-1">
          <section className="relative min-w-0 flex-1" aria-label={t('pdf')}>
            {file.data?.noteFile ? (
              <PdfViewer
                ref={pdf}
                url={file.data.noteFile.url}
                refreshUrl={async () => (await file.refetch().catch(() => null))?.data?.noteFile?.url ?? null}
                marks={marks}
                initialPage={initialPage}
                snipping={snipping}
                onLoaded={({ pages: n, outline: o }) => {
                  setPages(n)
                  setOutline(o)
                  setPdfState('ready')
                }}
                onPage={onPage}
                onScale={setScale}
                onSelection={(s) => {
                  setSelection(s)
                  if (s) setActive(null)
                }}
                onArea={(a) => setArea(a)}
                onMark={(id, at) => (id.startsWith('c:') ? showCard(id.slice(2)) : setActive({ id, at }))}
                onFind={setFound}
                onError={(kind) => setPdfState(kind === 'password' ? 'password' : 'failed')}
              />
            ) : null}
            {pdfState !== 'ready' ? (
              <div role="status" className="absolute inset-0 grid place-items-center p-6 text-center text-sm text-muted">
                {pdfState === 'loading' ? t('loading') : pdfState === 'password' ? t('passwordNeeded') : t('failed')}
              </div>
            ) : null}
          </section>

          <aside
            aria-label={t('panel')}
            className={cn(
              'flex flex-col border-border bg-bg max-lg:fixed max-lg:inset-x-0 max-lg:bottom-0 max-lg:z-[55] max-lg:h-[78dvh] max-lg:rounded-t-3xl max-lg:border-t max-lg:shadow-2xl lg:w-[30rem] lg:shrink-0 lg:border-l xl:w-[34rem]',
              !panelOpen && 'hidden',
            )}
          >
            <div role="tablist" className="flex shrink-0 items-center gap-1 border-b border-border px-2 py-1.5">
              {tab('notes', t('panels.notes'), NotebookPen)}
              {editable ? tab('highlights', t('panels.highlights'), Highlighter) : null}
              {tab('contents', t('panels.contents'), ListTree)}
              <ToolButton icon={X} label={t('hidePanel')} onClick={() => setPanelOpen(false)} className="ml-auto lg:hidden" />
            </div>
            <div className="min-h-0 flex-1 overflow-y-auto p-3">
              <div className={cn(panel !== 'notes' && 'hidden')}>
                {loaded.state !== 'ready' || !userId ? (
                  <p role="status" className="py-8 text-center text-sm text-muted">
                    {t('loadingNotes')}
                  </p>
                ) : converting ? (
                  <p className="py-8 text-center text-sm text-muted">{t('convert.waiting')}</p>
                ) : editable ? (
                  <NoteEditor
                    noteId={noteId}
                    userId={userId}
                    title={loaded.mirror?.title ?? loaded.meta.title}
                    doc={loaded.mirror?.doc ?? cardsToDoc(loaded.cards)}
                    saved={loaded.mirror ? savedFromMirror(loaded.mirror) : savedStateOf(loaded.meta.title, loaded.cards)}
                    send={send}
                    actions={null}
                    onOpenVersion={() => router.push(`/notes/${noteId}`)}
                    onAnchor={openAnchor}
                    onEditor={onEditor}
                    compact
                  />
                ) : (
                  <div className="flex flex-col gap-4">
                    <div className="flex flex-col gap-2 rounded-2xl border border-accent/30 bg-accent-soft p-4 text-sm">
                      <p>{t('readOnly')}</p>
                      {loaded.meta.viewerCan.fork ? (
                        <Button size="sm" className="w-fit gap-1.5" disabled={studying.loading} onClick={() => void startStudy()}>
                          <NotebookPen className="size-4" aria-hidden />
                          {t('study')}
                        </Button>
                      ) : (
                        <p className="text-muted">{t('noCopies')}</p>
                      )}
                    </div>
                    <h2 className="text-xl font-bold">{loaded.meta.title || t('untitled')}</h2>
                    {loaded.cards.map((c) => (
                      <CardView key={c.id} id={c.id} type={c.type} content={c.content} onAnchor={openAnchor} />
                    ))}
                  </div>
                )}
              </div>
              {panel === 'highlights' ? (
                <HighlightsList
                  highlights={highlights}
                  onOpen={(h) => {
                    if (!wide()) setPanelOpen(false)
                    pdf.current?.goTo(h.page, h.rects as PageRect[])
                  }}
                />
              ) : null}
              {panel === 'contents' ? (
                <OutlineList
                  items={outline}
                  onPick={(dest) => {
                    if (!wide()) setPanelOpen(false)
                    pdf.current?.goToDest(dest)
                  }}
                />
              ) : null}
            </div>
          </aside>
        </div>

        {selection && !snipping ? (
          <SelectionActions
            at={selection.at}
            editable={editable}
            onClose={() => {
              pdf.current?.clearSelection()
              setSelection(null)
            }}
            onHighlight={(color) => {
              void highlight({ page: selection.page, kind: 'TEXT', rects: selection.rects, quote: selection.quote, color })
              pdf.current?.clearSelection()
              setSelection(null)
            }}
            onAdd={() => {
              quoteCard(selection.page, selection.rects, selection.quote)
              pdf.current?.clearSelection()
              setSelection(null)
            }}
            onCopy={() => {
              void navigator.clipboard?.writeText(selection.quote).then(() => setNotice({ text: t('copied') }))
              pdf.current?.clearSelection()
              setSelection(null)
            }}
            onStudy={meta?.viewerCan.fork ? () => void startStudy() : undefined}
          />
        ) : null}
        {area ? (
          <AreaActions
            at={area.at}
            busy={busy}
            onCancel={() => setArea(null)}
            onHighlight={(color) => {
              void highlight({ page: area.page, kind: 'AREA', rects: [area.rect], color })
              setArea(null)
            }}
            onAdd={() => {
              setBusy(true)
              pictureCard(area.page, area.rect)
                .catch(() => failed(t('snipFailed')))
                .finally(() => {
                  setBusy(false)
                  setArea(null)
                })
            }}
          />
        ) : null}
        {activeHighlight && active ? (
          <HighlightCard
            key={activeHighlight.id}
            highlight={activeHighlight}
            at={active.at}
            onClose={() => setActive(null)}
            onColor={(color) => void change(activeHighlight.id, { color })}
            onComment={(comment) => void change(activeHighlight.id, { comment })}
            onAdd={() => {
              const h = activeHighlight
              setActive(null)
              const made = h.kind === 'AREA' ? pictureCard(h.page, h.rects[0] as PageRect) : Promise.resolve(quoteCard(h.page, h.rects as PageRect[], h.quote ?? ''))
              void made.then((cardId) => (cardId ? change(h.id, { cardId }) : undefined)).catch(() => failed(t('snipFailed')))
            }}
            onRemove={() => {
              const id = activeHighlight.id
              setActive(null)
              void removeHighlight({ variables: { highlightId: id } })
                .then((r) => (r.data?.removePdfHighlight.ok ? setHighlights((list) => list.filter((h) => h.id !== id)) : failed(r.data?.removePdfHighlight.userErrors[0]?.message)))
                .catch(() => failed())
            }}
          />
        ) : null}
        <ConvertDialog open={convertOpen} onClose={() => setConvertOpen(false)} noteId={noteId} fileId={fileId} fileName={fileName} />
        {notice ? (
          <div role="status" className="fixed bottom-4 left-1/2 z-[70] flex -translate-x-1/2 animate-rise items-center gap-3 rounded-full bg-fg px-4 py-2 text-sm text-bg shadow-xl">
            {notice.text}
            {notice.action ? (
              <button type="button" className="font-semibold underline" onClick={notice.action.run}>
                {notice.action.label}
              </button>
            ) : null}
          </div>
        ) : null}
      </div>
    </MediaProvider>
  )
}
