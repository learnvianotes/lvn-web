'use client'

import type { JSONContent } from '@tiptap/core'
import Highlight from '@tiptap/extension-highlight'
import Subscript from '@tiptap/extension-subscript'
import Superscript from '@tiptap/extension-superscript'
import { Placeholder } from '@tiptap/extensions'
import { EditorContent, useEditor, useEditorState, type Editor } from '@tiptap/react'
import { BubbleMenu } from '@tiptap/react/menus'
import StarterKit from '@tiptap/starter-kit'
import { CircleAlert, ArrowDown, ArrowUp, Bold, Check, CloudOff, Code, Copy, GripVertical, Highlighter, Italic, Link2, List, ListOrdered, ListTree, LoaderCircle, type LucideIcon, Maximize2, Mic, Minimize2, Ellipsis, Notebook, Plus, Redo2, Strikethrough, Trash, Underline, Undo2, Volume2, WandSparkles } from 'lucide-react'
import { useTranslations } from 'next-intl'
import { useCallback, useEffect, useRef, useState } from 'react'
import { Dialog } from '@/components/ui/dialog'
import { cardPlainText, type CardAnchor } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { readingMinutes } from '../look'
import { docToCards, type CardType } from '../model/doc'
import type { SavedState } from '../model/save'
import { ReadAloudControls } from '../ReadAloudControls'
import { useReadAloud } from '../readAloud'
import { useAutosave, type SaveStatus, type SendSave } from './autosave'
import { CARD_NODES, CONVERTIBLE, convertCard, currentCard, deleteCard, duplicateCard, insertCardAfter, insertMediaCards, moveCard, selectCard } from './nodes'
import { AnchorChips } from './anchors'
import { ReadingHighlight, setReadingCard } from './reading'
import { uploads, useUploadsEnabled } from '../uploads'
import { cardMenu, SlashMenu } from './slash'
import { PageEditor } from '../pages/PageEditor'
import { RecordDialog } from './Recorder'
import { CardRail } from '../view/CardRail'
import { useFeatureUse } from '@/lib/analytics'

export interface NoteEditorProps {
  noteId: string
  userId: string
  title: string
  doc: JSONContent
  saved: SavedState
  send: SendSave
  /** Header actions of the page (publish, versions, details…) */
  actions: React.ReactNode
  /** Under the title: folder, tags, topics */
  meta?: React.ReactNode
  /** The page's actions again, as items of the phone's More menu */
  menuItems?: { label: string; icon: LucideIcon; onClick: () => void; danger?: boolean }[]
  onOpenVersion: (versionId: string) => void
  /** Opens the PDF a card came from (its page chip, lvn-backend ADR-0040) */
  onAnchor?: (anchor: CardAnchor, cardId: string) => void
  /** The editor, for pages that add cards to it (the PDF reader) */
  onEditor?: (editor: Editor | null) => void
  /** Beside a PDF: no outline column or focus mode, a smaller title */
  compact?: boolean
  /** Under the title: the note's tabs (lvn-backend ADR-0076) */
  tabs?: React.ReactNode
  /** Another tab's panel: shown instead of the cards, which stay mounted (autosave, undo) */
  panel?: React.ReactNode
  /** The cards' tab panel ids, when there are tabs */
  contentPanel?: { id: string; labelledBy: string }
  /** Beside the note from 1280 px: Ask AI (ADR-0076) */
  aside?: React.ReactNode
}

const SAFE_LINK = /^(https?:\/\/|mailto:)/i

/**
 * The note editor (lvn-backend §12.2): one Tiptap document of cards under a large title. Formatting appears next to
 * the selection; each card has a handle (add a card below, move, duplicate, turn into, delete); the outline sits
 * beside the note on wide screens and in a sheet on phones; autosave reports itself in a pill; focus mode hides
 * everything but the writing; read aloud highlights the card being read.
 */
export function NoteEditor({ noteId, userId, title: initialTitle, doc, saved, send, actions, meta, menuItems = [], onOpenVersion, onAnchor, onEditor, compact = false, tabs, panel, contentPanel, aside }: NoteEditorProps) {
  const t = useTranslations('notes.editor')
  useFeatureUse('notes_editor')
  // Keeps `uploads.enabled` current for the slash menu, drop and paste (lvn-backend ADR-0097).
  useUploadsEnabled()
  const anchorRef = useRef(onAnchor)
  anchorRef.current = onAnchor
  const [title, setTitle] = useState(initialTitle)
  const [focus, setFocus] = useState(false)
  const [pages, setPages] = useState(false)
  const [contentsOpen, setContentsOpen] = useState(false)
  const titleRef = useRef(initialTitle)
  const autosave = useAutosave({ userId, noteId, saved, send })

  const editor = useEditor({
    immediatelyRender: false,
    extensions: [
      StarterKit.configure({
        document: false,
        heading: false,
        blockquote: false,
        codeBlock: false,
        horizontalRule: false,
        trailingNode: false,
        link: { openOnClick: false, autolink: true, defaultProtocol: 'https', isAllowedUri: (url) => SAFE_LINK.test(url) },
      }),
      Highlight,
      Subscript,
      Superscript,
      Placeholder.configure({ placeholder: ({ node }) => (node.type.name === 'paragraph' ? t('placeholder') : ''), includeChildren: true }),
      ReadingHighlight,
      SlashMenu,
      AnchorChips.configure({ onOpen: (anchor, cardId) => anchorRef.current?.(anchor, cardId), label: (page) => t('anchorPage', { page }) }),
      ...CARD_NODES,
    ],
    content: doc,
    editorProps: {
      attributes: { class: 'lvn-editor-content focus:outline-none', 'aria-label': t('content'), 'aria-multiline': 'true', role: 'textbox' },
      // Pictures, video, audio and PDFs dropped or pasted into the note become media cards that upload them. While uploads
      // are off (lvn-backend ADR-0097) a dropped or pasted file is ignored, not opened by the browser.
      handleDrop: (view, event, _slice, moved) => {
        const files = [...(event.dataTransfer?.files ?? [])]
        if (!uploads.enabled) return files.length > 0
        return !moved && insertMediaCards(view, files, view.posAtCoords({ left: event.clientX, top: event.clientY })?.pos)
      },
      handlePaste: (view, event) => {
        const files = [...(event.clipboardData?.files ?? [])]
        if (!uploads.enabled) return files.length > 0
        return insertMediaCards(view, files)
      },
    },
    onUpdate: ({ editor: e }) => autosave.changed(titleRef.current, e.getJSON()),
  })

  useEffect(() => {
    onEditor?.(editor ?? null)
  }, [editor, onEditor])

  const changeTitle = (value: string) => {
    setTitle(value)
    titleRef.current = value
    if (editor) autosave.changed(value, editor.getJSON())
  }

  const stats = useEditorState({
    editor,
    selector: ({ editor: e }) => {
      if (!e) return { cards: 0, minutes: 0 }
      const cards = docToCards(e.getJSON())
      return { cards: cards.length, minutes: readingMinutes(cards.map((c) => cardPlainText(c.type, c.content)).join(' ')) }
    },
  })
  const spoken = useCallback(() => (editor ? docToCards(editor.getJSON()).map((c) => ({ id: c.id, text: cardPlainText(c.type, c.content) })) : []), [editor])
  const reader = useReadAloud(spoken)
  const readingId = reader.current
  useEffect(() => {
    if (editor) setReadingCard(editor, readingId)
  }, [editor, readingId])
  useEffect(() => {
    if (!focus) return
    const exit = (e: KeyboardEvent) => e.key === 'Escape' && setFocus(false)
    window.addEventListener('keydown', exit)
    return () => window.removeEventListener('keydown', exit)
  }, [focus])

  // Focus mode is the writing alone: no tabs, rail or dock, and the cards even if another tab was open.
  const showPanel = !!panel && !focus
  const wide = !focus && !compact
  return (
    <div className={cn('grid gap-6', wide && aside && 'xl:grid-cols-[minmax(0,1fr)_19rem]')}>
      <div className={cn('flex min-w-0 flex-col gap-4', focus && 'mx-auto w-full max-w-3xl')}>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <SavePill status={autosave.status} />
            {stats ? (
              <span className="hidden text-xs text-muted sm:inline">
                {t('cardsCount', { n: stats.cards })}
                {stats.minutes ? ` · ${t('readingTime', { n: stats.minutes })}` : ''}
              </span>
            ) : null}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" className={cn('inline-flex items-center gap-1.5 rounded-full border border-border bg-surface px-3 py-1.5 text-sm hover:bg-surface-2', pages && 'border-sky-600 bg-sky-50 text-sky-900')} aria-pressed={pages} onClick={() => setPages((open) => !open)}>
              <Notebook className="size-4" aria-hidden />
              {t('pages')}
            </button>
            <button type="button" className={cn('inline-flex items-center gap-1.5 rounded-full border border-border bg-surface px-3 py-1.5 text-sm hover:bg-surface-2 lg:hidden', compact && 'hidden')} onClick={() => setContentsOpen(true)}>
              <ListTree className="size-4" aria-hidden />
              {t('contents')}
            </button>
            <span className="hidden sm:contents">
              <ReadAloudControls reader={reader} />
              {!compact ? <IconButton icon={focus ? Minimize2 : Maximize2} label={focus ? t('focusExit') : t('focus')} onClick={() => setFocus((f) => !f)} pressed={focus} /> : null}
            </span>
            {!focus ? actions : null}
            {reader.state !== 'idle' ? (
              <span className="sm:hidden">
                <ReadAloudControls reader={reader} />
              </span>
            ) : null}
            <MoreMenu
              items={[
                ...(reader.supported && reader.state === 'idle' ? [{ label: t('readAloud'), icon: Volume2, onClick: () => reader.play() }] : []),
                ...menuItems,
              ]}
            />
          </div>
        </div>
        {autosave.conflictVersionId ? (
          <Banner tone="warning" onClose={autosave.dismissConflict}>
            {t('conflict')}{' '}
            <button type="button" className="font-semibold underline" onClick={() => onOpenVersion(autosave.conflictVersionId!)}>
              {t('seeOtherVersion')}
            </button>
          </Banner>
        ) : null}
        {autosave.refused ? <Banner tone="warning">{t('refused')}</Banner> : null}
        {autosave.problem ? <Banner tone="error">{t('problem', { message: autosave.problem })}</Banner> : null}

        <div className="flex flex-col gap-2 px-1">
          <textarea
            rows={1}
            className={cn('w-full resize-none overflow-hidden border-0 bg-transparent font-extrabold leading-tight tracking-tight placeholder:text-muted/50 focus:outline-none', compact ? 'text-2xl' : 'text-3xl sm:text-[2.6rem]')}
            placeholder={t('untitled')}
            aria-label={t('title')}
            value={title}
            maxLength={200}
            ref={(el) => {
              if (el) {
                el.style.height = 'auto'
                el.style.height = `${el.scrollHeight}px`
              }
            }}
            onChange={(e) => changeTitle(e.target.value.replace(/\n/g, ' '))}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                editor?.commands.focus('start')
              }
            }}
          />
          {meta}
        </div>

        {!focus ? tabs : null}
        {pages && !focus ? <PageEditor noteId={noteId} /> : null}
        <div role={contentPanel ? 'tabpanel' : undefined} id={contentPanel?.id} aria-labelledby={contentPanel?.labelledBy} hidden={showPanel || pages} className={showPanel || pages ? 'hidden' : 'flex min-w-0 max-w-full flex-col gap-4'}>
          {wide ? <EditorRail editor={editor} /> : null}
          <Toolbar editor={editor} sticky={compact ? 'top-0' : 'top-14'} />
          <div className={cn('lvn-editor relative min-w-0 max-w-full rounded-3xl border border-border bg-surface py-5 pl-10 pr-4 shadow-sm', compact ? 'sm:pl-12 sm:pr-5' : 'sm:py-6 sm:pl-14 sm:pr-10')}>
            {editor ? <CardHandle editor={editor} /> : null}
            {editor ? <SelectionMenu editor={editor} /> : null}
            <EditorContent editor={editor} />
          </div>
          <AddCardMenu editor={editor} noteId={noteId} />
          <p className="text-xs text-muted">{t('shortcuts')}</p>
        </div>
        {showPanel ? panel : null}
      </div>
      {wide && aside ? aside : null}

      <Dialog open={contentsOpen} onClose={() => setContentsOpen(false)} title={t('contents')}>
        <Outline editor={editor} onPick={() => setContentsOpen(false)} />
      </Dialog>
    </div>
  )
}

// ── Pieces ───────────────────────────────────────────────────────────────────────────────────────────────────

function SavePill({ status }: { status: SaveStatus }) {
  const t = useTranslations('notes.editor.status')
  const look: Record<SaveStatus, { icon: LucideIcon; className: string; spin?: boolean }> = {
    saved: { icon: Check, className: 'bg-emerald-500/10 text-emerald-700 dark:text-emerald-400' },
    pending: { icon: LoaderCircle, className: 'bg-surface-2 text-muted', spin: false },
    saving: { icon: LoaderCircle, className: 'bg-accent-soft text-accent', spin: true },
    offline: { icon: CloudOff, className: 'bg-amber-500/15 text-amber-800 dark:text-amber-300' },
    error: { icon: CircleAlert, className: 'bg-red-500/10 text-red-700 dark:text-red-400' },
  }
  const { icon: Icon, className, spin } = look[status]
  return (
    <p role="status" aria-live="polite" className={cn('inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-colors', className)}>
      <Icon className={cn('size-3.5', spin && 'animate-spin')} aria-hidden />
      {t(status)}
    </p>
  )
}

function Banner({ tone, children, onClose }: { tone: 'warning' | 'error'; children: React.ReactNode; onClose?: () => void }) {
  const t = useTranslations('notes.editor')
  return (
    <div role={tone === 'error' ? 'alert' : 'status'} className={cn('flex animate-rise items-start gap-3 rounded-2xl border px-4 py-3 text-sm', tone === 'error' ? 'border-red-600/30 bg-red-50 text-red-900 dark:bg-red-950/40 dark:text-red-200' : 'border-amber-500/40 bg-amber-50 text-amber-950 dark:bg-amber-950/30 dark:text-amber-100')}>
      <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden />
      <div className="flex-1">{children}</div>
      {onClose ? (
        <button type="button" className="text-xs underline" onClick={onClose}>
          {t('dismiss')}
        </button>
      ) : null}
    </div>
  )
}

function IconButton({ icon: Icon, label, onClick, pressed, disabled, className }: { icon: LucideIcon; label: string; onClick: () => void; pressed?: boolean; disabled?: boolean; className?: string }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      aria-pressed={pressed}
      disabled={disabled}
      onClick={onClick}
      className={cn('inline-flex size-9 shrink-0 items-center justify-center rounded-xl text-fg transition hover:bg-surface-2 active:scale-95 disabled:opacity-40 aria-pressed:bg-accent-soft aria-pressed:text-accent', className)}
    >
      <Icon className="size-[18px]" aria-hidden />
    </button>
  )
}

const MARKS: { mark: string; icon: LucideIcon; run: (e: Editor) => boolean }[] = [
  { mark: 'bold', icon: Bold, run: (e) => e.chain().focus().toggleBold().run() },
  { mark: 'italic', icon: Italic, run: (e) => e.chain().focus().toggleItalic().run() },
  { mark: 'underline', icon: Underline, run: (e) => e.chain().focus().toggleUnderline().run() },
  { mark: 'strike', icon: Strikethrough, run: (e) => e.chain().focus().toggleStrike().run() },
  { mark: 'code', icon: Code, run: (e) => e.chain().focus().toggleCode().run() },
  { mark: 'highlight', icon: Highlighter, run: (e) => e.chain().focus().toggleHighlight().run() },
]

function useMarks(editor: Editor | null) {
  return useEditorState({
    editor,
    selector: ({ editor: e }) => (e ? Object.fromEntries([...MARKS.map((m) => [m.mark, e.isActive(m.mark)]), ['link', e.isActive('link')], ['bulletList', e.isActive('bulletList')], ['orderedList', e.isActive('orderedList')]]) : {}) as Record<string, boolean>,
  })
}

function setLink(editor: Editor, t: ReturnType<typeof useTranslations>) {
  const previous = (editor.getAttributes('link').href as string | undefined) ?? ''
  const href = window.prompt(t('linkPrompt'), previous)
  if (href === null) return
  if (!href.trim()) editor.chain().focus().extendMarkRange('link').unsetLink().run()
  else if (SAFE_LINK.test(href.trim())) editor.chain().focus().extendMarkRange('link').setLink({ href: href.trim() }).run()
  else window.alert(t('linkInvalid'))
}

/** Formatting next to the selected words. */
function SelectionMenu({ editor }: { editor: Editor }) {
  const t = useTranslations('notes.editor')
  const active = useMarks(editor)
  return (
    <BubbleMenu
      editor={editor}
      shouldShow={({ editor: e, state }) => !state.selection.empty && e.isEditable && !e.isActive('codeCard') && !e.isActive('markdownCard') && !e.isActive('diagramCard') && state.selection.$from.depth > 1}
      className="flex items-center gap-0.5 rounded-2xl border border-border bg-surface p-1 shadow-xl shadow-black/10"
    >
      {MARKS.map((m) => (
        <IconButton key={m.mark} icon={m.icon} label={t(`marks.${m.mark}`)} pressed={!!active?.[m.mark]} onClick={() => m.run(editor)} className="size-8" />
      ))}
      <IconButton icon={Link2} label={t('marks.link')} pressed={!!active?.link} onClick={() => setLink(editor, t)} className="size-8" />
    </BubbleMenu>
  )
}

function Toolbar({ editor, sticky }: { editor: Editor | null; sticky: 'top-0' | 'top-14' }) {
  const t = useTranslations('notes.editor')
  const active = useMarks(editor)
  if (!editor) return null
  return (
    <div role="toolbar" aria-label={t('toolbar')} className={cn('sticky z-20 flex items-center gap-0.5 overflow-x-auto rounded-2xl border border-border bg-bg/85 p-1 shadow-sm backdrop-blur [scrollbar-width:none]', sticky)}>
      {MARKS.slice(0, 3).map((m) => (
        <IconButton key={m.mark} icon={m.icon} label={t(`marks.${m.mark}`)} pressed={!!active?.[m.mark]} onClick={() => m.run(editor)} />
      ))}
      <IconButton icon={Link2} label={t('marks.link')} pressed={!!active?.link} onClick={() => setLink(editor, t)} />
      <span className="mx-1 h-5 w-px bg-border" aria-hidden />
      <IconButton icon={List} label={t('bulletList')} pressed={!!active?.bulletList} onClick={() => editor.chain().focus().toggleBulletList().run()} />
      <IconButton icon={ListOrdered} label={t('orderedList')} pressed={!!active?.orderedList} onClick={() => editor.chain().focus().toggleOrderedList().run()} />
      <span className="mx-1 h-5 w-px bg-border" aria-hidden />
      <IconButton icon={ArrowUp} label={t('moveUp')} onClick={() => moveCard(editor, -1)} />
      <IconButton icon={ArrowDown} label={t('moveDown')} onClick={() => moveCard(editor, 1)} />
      <IconButton icon={Copy} label={t('duplicateCard')} onClick={() => duplicateCard(editor)} />
      <IconButton icon={Trash} label={t('deleteCard')} onClick={() => deleteCard(editor)} />
      <span className="ml-auto flex shrink-0 items-center gap-0.5">
        <IconButton icon={Undo2} label={t('undo')} onClick={() => editor.chain().focus().undo().run()} />
        <IconButton icon={Redo2} label={t('redo')} onClick={() => editor.chain().focus().redo().run()} />
      </span>
    </div>
  )
}

/**
 * The handle beside the card under the pointer (or holding the cursor): + adds a card below, the grip opens the card's
 * menu. Positioned against the editor's box; on touch screens it follows the cursor.
 */
function CardHandle({ editor }: { editor: Editor }) {
  const t = useTranslations('notes.editor')
  const uploadsOn = useUploadsEnabled()
  const [at, setAt] = useState<{ pos: number; top: number } | null>(null)
  const [menu, setMenu] = useState<'add' | 'card' | null>(null)
  const box = useRef<HTMLDivElement>(null)

  const place = useCallback(
    (pos: number | null) => {
      const container = box.current?.parentElement
      if (pos === null || !container) return
      const dom = editor.view.nodeDOM(pos) as HTMLElement | null
      if (!dom) return
      setAt({ pos, top: dom.getBoundingClientRect().top - container.getBoundingClientRect().top })
    },
    [editor],
  )

  useEffect(() => {
    const onSelection = () => {
      if (menu) return
      const card = currentCard(editor)
      if (card) place(card.pos)
    }
    const onMove = (e: MouseEvent) => {
      if (menu) return
      const hit = editor.view.posAtCoords({ left: Math.max(e.clientX, editor.view.dom.getBoundingClientRect().left + 8), top: e.clientY })
      if (!hit) return
      const $pos = editor.state.doc.resolve(hit.inside >= 0 ? hit.inside : hit.pos)
      place($pos.depth >= 1 ? $pos.before(1) : hit.inside >= 0 ? hit.inside : null)
    }
    editor.on('selectionUpdate', onSelection)
    editor.on('update', onSelection)
    const dom = editor.view.dom.parentElement?.parentElement
    dom?.addEventListener('mousemove', onMove)
    return () => {
      editor.off('selectionUpdate', onSelection)
      editor.off('update', onSelection)
      dom?.removeEventListener('mousemove', onMove)
    }
  }, [editor, menu, place])

  const act = (run: () => void) => {
    if (at) selectCard(editor, at.pos)
    run()
    setMenu(null)
  }
  const node = at ? editor.state.doc.nodeAt(at.pos) : null
  const convertible = node && ['textCard', 'headingCard', 'quoteCard', 'calloutCard'].includes(node.type.name)
  const menuItems = cardMenu(uploadsOn)

  return (
    <div ref={box} contentEditable={false} className="absolute left-1.5 z-10 flex flex-col items-center gap-0.5 transition-[top] duration-150 sm:left-3" style={{ top: (at?.top ?? 24) + 2, opacity: at ? 1 : 0 }}>
      <button type="button" aria-label={t('addCardBelow')} title={t('addCardBelow')} aria-expanded={menu === 'add'} className="grid size-7 place-items-center rounded-lg text-muted transition hover:bg-accent-soft hover:text-accent" onClick={() => setMenu((m) => (m === 'add' ? null : 'add'))}>
        <Plus className="size-4" aria-hidden />
      </button>
      <button type="button" aria-label={t('cardMenu')} title={t('cardMenu')} aria-expanded={menu === 'card'} className="grid size-7 cursor-grab place-items-center rounded-lg text-muted transition hover:bg-surface-2 hover:text-fg" onClick={() => setMenu((m) => (m === 'card' ? null : 'card'))}>
        <GripVertical className="size-4" aria-hidden />
      </button>
      {menu ? (
        <div className="absolute left-9 top-0 z-30 w-64 animate-rise rounded-2xl border border-border bg-surface p-1.5 shadow-2xl shadow-black/15" onKeyDown={(e) => e.key === 'Escape' && setMenu(null)}>
          {menu === 'add' ? (
            <ul className="grid max-h-80 grid-cols-1 overflow-y-auto">
              {menuItems.map((item) => (
                <li key={item.type}>
                  <button type="button" className="flex w-full flex-col rounded-xl px-3 py-1.5 text-left hover:bg-surface-2" onClick={() => act(() => insertCardAfter(editor, item.type))}>
                    <span className="text-sm font-medium">{t(`cards.${item.type}`)}</span>
                    <span className="text-xs text-muted">{t(`cardHints.${item.type}`)}</span>
                  </button>
                </li>
              ))}
            </ul>
          ) : (
            <div className="flex flex-col text-sm">
              <MenuItem icon={ArrowUp} label={t('moveUp')} onClick={() => act(() => moveCard(editor, -1))} />
              <MenuItem icon={ArrowDown} label={t('moveDown')} onClick={() => act(() => moveCard(editor, 1))} />
              <MenuItem icon={Copy} label={t('duplicateCard')} onClick={() => act(() => duplicateCard(editor))} />
              {convertible ? (
                <>
                  <p className="mt-1 flex items-center gap-2 px-3 pb-0.5 pt-1.5 text-xs font-semibold uppercase tracking-wide text-muted">
                    <WandSparkles className="size-3.5" aria-hidden />
                    {t('turnInto')}
                  </p>
                  {CONVERTIBLE.map((type: CardType) => (
                    <MenuItem key={type} label={t(`cards.${type}`)} onClick={() => act(() => convertCard(editor, type))} />
                  ))}
                </>
              ) : null}
              <span className="my-1 h-px bg-border" aria-hidden />
              <MenuItem icon={Trash} label={t('deleteCard')} danger onClick={() => act(() => deleteCard(editor))} />
            </div>
          )}
        </div>
      ) : null}
    </div>
  )
}

/** The page's actions on phones, behind one button. */
function MoreMenu({ items }: { items: { label: string; icon: LucideIcon; onClick: () => void; danger?: boolean }[] }) {
  const t = useTranslations('notes.editor')
  const [open, setOpen] = useState(false)
  if (!items.length) return null
  return (
    <div className="relative sm:hidden">
      <IconButton icon={Ellipsis} label={t('more')} pressed={open} onClick={() => setOpen((o) => !o)} className="border border-border bg-surface" />
      {open ? (
        <div className="absolute right-0 z-30 mt-2 flex w-52 animate-rise flex-col rounded-2xl border border-border bg-surface p-1.5 text-sm shadow-2xl shadow-black/15">
          {items.map((item) => (
            <MenuItem key={item.label} icon={item.icon} label={item.label} danger={item.danger} onClick={() => (setOpen(false), item.onClick())} />
          ))}
        </div>
      ) : null}
    </div>
  )
}

function MenuItem({ icon: Icon, label, onClick, danger }: { icon?: LucideIcon; label: string; onClick: () => void; danger?: boolean }) {
  return (
    <button type="button" onClick={onClick} className={cn('flex items-center gap-2 rounded-xl px-3 py-1.5 text-left hover:bg-surface-2', danger && 'text-red-600 dark:text-red-400')}>
      {Icon ? <Icon className="size-4" aria-hidden /> : <span className="size-4" aria-hidden />}
      {label}
    </button>
  )
}

function AddCardMenu({ editor, noteId }: { editor: Editor | null; noteId: string }) {
  const t = useTranslations('notes.editor')
  const tRecord = useTranslations('notes.record')
  const [open, setOpen] = useState(false)
  const [recording, setRecording] = useState(false)
  const uploadsOn = useUploadsEnabled()
  if (!editor) return null
  const add = (type: CardType) => {
    setOpen(false)
    editor.commands.focus('end')
    insertCardAfter(editor, type)
  }
  return (
    <div className="relative">
      <button type="button" aria-expanded={open} className="inline-flex items-center gap-2 rounded-full border border-dashed border-border px-4 py-2 text-sm font-medium text-muted transition hover:border-accent hover:bg-accent-soft hover:text-accent" onClick={() => setOpen((o) => !o)}>
        <Plus className="size-4" aria-hidden />
        {t('addCard')}
      </button>
      {open ? (
        <ul className="absolute z-30 mt-2 grid w-full max-w-xl animate-rise gap-1 rounded-2xl border border-border bg-surface p-2 shadow-2xl shadow-black/10 sm:grid-cols-2">
          {cardMenu(uploadsOn).map((item) => (
            <li key={item.type}>
              <button type="button" className="flex w-full flex-col rounded-xl px-3 py-2 text-left hover:bg-surface-2" onClick={() => add(item.type)}>
                <span className="text-sm font-medium">{t(`cards.${item.type}`)}</span>
                <span className="text-xs text-muted">{t(`cardHints.${item.type}`)}</span>
              </button>
            </li>
          ))}
          {/* A voice note (lvn-backend ADR-0062): recorded here, then an audio card like a dropped file. An upload, so only
              while uploads are on (ADR-0097). */}
          {uploadsOn ? <li>
            <button
              type="button"
              className="flex w-full flex-col rounded-xl px-3 py-2 text-left hover:bg-surface-2"
              onClick={() => {
                setOpen(false)
                setRecording(true)
              }}
            >
              <span className="flex items-center gap-1.5 text-sm font-medium">
                <Mic className="size-4 text-accent" aria-hidden />
                {tRecord('menu')}
              </span>
              <span className="text-xs text-muted">{tRecord('menuHint')}</span>
            </button>
          </li> : null}
        </ul>
      ) : null}
      <RecordDialog
        open={recording}
        noteId={noteId}
        onClose={() => setRecording(false)}
        onDone={(file) => {
          setRecording(false)
          editor.commands.focus('end')
          insertMediaCards(editor.view, [file])
        }}
      />
    </div>
  )
}

function Outline({ editor, onPick }: { editor: Editor | null; onPick?: () => void }) {
  const t = useTranslations('notes.editor')
  const headings = useEditorState({
    editor,
    selector: ({ editor: e }) => {
      const list: { pos: number; level: number; text: string }[] = []
      e?.state.doc.forEach((node, offset) => {
        if (node.type.name === 'headingCard') list.push({ pos: offset, level: node.attrs.level as number, text: node.textContent })
      })
      return list
    },
  })
  return (
    <div className="flex flex-col gap-1">
      <p className="px-2 text-xs font-semibold uppercase tracking-wider text-muted">{t('outline')}</p>
      {headings?.length ? (
        headings.map((h) => (
          <button
            key={h.pos}
            type="button"
            className="truncate rounded-lg px-2 py-1.5 text-left text-sm text-muted transition hover:bg-surface-2 hover:text-fg"
            style={{ paddingLeft: `${0.5 + (h.level - 1) * 0.75}rem` }}
            onClick={() => {
              editor?.chain().focus().setTextSelection(h.pos + 1).run()
              ;(editor?.view.nodeDOM(h.pos) as HTMLElement | null)?.scrollIntoView({ block: 'center', behavior: 'smooth' })
              onPick?.()
            }}
          >
            {h.text || t('untitledHeading')}
          </button>
        ))
      ) : (
        <p className="px-2 text-sm text-muted">{t('outlineEmpty')}</p>
      )}
    </div>
  )
}

/** The note's sections as board A's card rail (ADR-0076): each heading card, and Previous and Next between them. */
function EditorRail({ editor }: { editor: Editor | null }) {
  const headings = useEditorState({
    editor,
    selector: ({ editor: e }) => {
      const list: { pos: number; text: string }[] = []
      e?.state.doc.forEach((node, offset) => {
        if (node.type.name === 'headingCard') list.push({ pos: offset, text: node.textContent })
      })
      return list
    },
  })
  return (
    <CardRail
      sections={(headings ?? []).map((h) => ({ key: h.pos, text: h.text }))}
      onGo={(i) => {
        const h = headings?.[i]
        if (!h || !editor) return
        ;(editor.view.nodeDOM(h.pos) as HTMLElement | null)?.scrollIntoView({ block: 'center', behavior: 'smooth' })
      }}
    />
  )
}
