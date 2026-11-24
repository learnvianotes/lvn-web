'use client'

import { NodeViewContent, NodeViewWrapper, type ReactNodeViewProps } from '@tiptap/react'
import { useTranslations } from 'next-intl'
import { useId } from 'react'
import { docText, inlineText, type Doc, type Inline } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { newCardId } from '../model/doc'

/**
 * Node views of the note editor: the small controls cards need beside their text (heading level, callout style, the
 * language of code), and forms for the structured cards. Fields edited here are plain text; a field nobody touches
 * keeps the rich content it came with.
 */

const textToInline = (text: string): Inline => (text ? [{ type: 'text', text }] : [])
const textToDoc = (text: string): Doc => ({
  type: 'doc',
  content: text.split('\n').map((line) => (line ? { type: 'paragraph', content: [{ type: 'text', text: line }] } : { type: 'paragraph' })),
})

const control = 'rounded-lg border border-border bg-surface px-2 py-1 text-sm text-fg focus-visible:border-accent focus-visible:outline-none'
const area = cn(control, 'min-h-[2.5rem] w-full resize-y leading-relaxed')

function Label({ children }: { children: string }) {
  return <span className="text-xs font-semibold text-muted">{children}</span>
}

function Field({ label, value, onChange, rows = 2, placeholder }: { label: string; value: string; onChange: (v: string) => void; rows?: number; placeholder?: string }) {
  const id = useId()
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id}>
        <Label>{label}</Label>
      </label>
      <textarea id={id} className={area} rows={rows} value={value} placeholder={placeholder} onChange={(e) => onChange(e.target.value)} />
    </div>
  )
}

export function HeadingView({ node, updateAttributes, editor }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const level = node.attrs.level as 1 | 2 | 3
  return (
    <NodeViewWrapper className="lvn-card group relative" data-card="heading">
      {editor.isEditable ? (
        <select
          contentEditable={false}
          aria-label={t('headingLevel')}
          className="absolute -left-14 top-1 hidden rounded-md border border-border bg-surface text-xs text-muted group-focus-within:block sm:block sm:opacity-0 sm:group-hover:opacity-100 sm:group-focus-within:opacity-100"
          value={level}
          onChange={(e) => updateAttributes({ level: Number(e.target.value) })}
        >
          <option value={1}>H1</option>
          <option value={2}>H2</option>
          <option value={3}>H3</option>
        </select>
      ) : null}
      <NodeViewContent<'h1' | 'h2' | 'h3'> as={`h${level}`} className={cn('font-semibold tracking-tight', level === 1 ? 'text-3xl' : level === 2 ? 'text-2xl' : 'text-xl')} />
    </NodeViewWrapper>
  )
}

export function QuoteView({ node, updateAttributes }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  return (
    <NodeViewWrapper as="blockquote" className="lvn-card border-l-4 border-accent/50 pl-4 italic" data-card="quote">
      <NodeViewContent />
      <input
        contentEditable={false}
        className="mt-1 w-full border-0 bg-transparent text-sm not-italic text-muted placeholder:text-muted/70 focus:outline-none"
        placeholder={t('attribution')}
        aria-label={t('attribution')}
        value={(node.attrs.attribution as string) ?? ''}
        onChange={(e) => updateAttributes({ attribution: e.target.value })}
      />
    </NodeViewWrapper>
  )
}

const CALLOUT_STYLES: Record<string, string> = {
  note: 'border-border bg-surface-2',
  info: 'border-sky-500/40 bg-sky-500/10',
  tip: 'border-emerald-500/40 bg-emerald-500/10',
  warning: 'border-amber-500/40 bg-amber-500/10',
  danger: 'border-red-500/40 bg-red-500/10',
}

export function CalloutView({ node, updateAttributes }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const variant = (node.attrs.variant as string) ?? 'note'
  return (
    <NodeViewWrapper as="aside" className={cn('lvn-card rounded-xl border p-3', CALLOUT_STYLES[variant])} data-card="callout">
      <div contentEditable={false} className="mb-1 flex items-center gap-2">
        <select aria-label={t('calloutStyle')} className={control} value={variant} onChange={(e) => updateAttributes({ variant: e.target.value })}>
          {Object.keys(CALLOUT_STYLES).map((v) => (
            <option key={v} value={v}>
              {t(`callout.${v}`)}
            </option>
          ))}
        </select>
        <input
          className="min-w-0 flex-1 border-0 bg-transparent font-semibold placeholder:text-muted focus:outline-none"
          placeholder={t('calloutTitle')}
          aria-label={t('calloutTitle')}
          value={(node.attrs.title as string) ?? ''}
          onChange={(e) => updateAttributes({ title: e.target.value })}
        />
      </div>
      <NodeViewContent />
    </NodeViewWrapper>
  )
}

export function CheckItemView({ node, updateAttributes }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const checked = !!node.attrs.checked
  return (
    <NodeViewWrapper as="li" className="flex items-start gap-2">
      <input
        contentEditable={false}
        type="checkbox"
        className="mt-1.5 size-4 accent-[var(--accent)]"
        aria-label={t('done')}
        checked={checked}
        onChange={(e) => updateAttributes({ checked: e.target.checked })}
      />
      <NodeViewContent className={cn('min-w-0 flex-1', checked && 'text-muted line-through')} />
    </NodeViewWrapper>
  )
}

export function CodeLikeView({ node, updateAttributes }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const kind = node.type.name
  return (
    <NodeViewWrapper className="lvn-card min-w-0 max-w-full rounded-xl border border-border bg-surface-2" data-card={kind}>
      <div contentEditable={false} className="flex items-center gap-2 border-b border-border px-3 py-1.5">
        {kind === 'codeCard' ? (
          <>
            <input className={cn(control, 'w-28 font-mono text-xs')} placeholder={t('language')} aria-label={t('language')} value={(node.attrs.language as string) ?? ''} onChange={(e) => updateAttributes({ language: e.target.value.toLowerCase().replace(/[^a-z0-9+#.-]/g, '') })} />
            <input className={cn(control, 'min-w-0 flex-1 font-mono text-xs')} placeholder={t('filename')} aria-label={t('filename')} value={(node.attrs.filename as string) ?? ''} onChange={(e) => updateAttributes({ filename: e.target.value })} />
          </>
        ) : (
          <Label>{t(kind === 'markdownCard' ? 'markdown' : 'diagram')}</Label>
        )}
      </div>
      <pre className="lvn-code-scroll p-3 font-mono text-sm leading-relaxed">
        <NodeViewContent<'code'> as="code" />
      </pre>
    </NodeViewWrapper>
  )
}

/** Wraps a structured card: a labelled box whose form edits the card's `data`. */
function AtomCard({ label, selected, children }: { label: string; selected: boolean; children: React.ReactNode }) {
  return (
    <NodeViewWrapper className={cn('lvn-card rounded-xl border bg-surface p-3', selected ? 'border-accent ring-2 ring-accent/30' : 'border-border')}>
      <div contentEditable={false} className="flex flex-col gap-2">
        <Label>{label}</Label>
        {children}
      </div>
    </NodeViewWrapper>
  )
}

/**
 * A change written onto a card's data as it is in the document now, found by the card's id. A view renders with the
 * node it was last given, so two quick edits in a row (the front, then the back) would otherwise write the first one's
 * old value back over it; and a view can be replaced under the person's fingers (a new card is given its id by a
 * follow-up transaction), so its own position may no longer point at the card, and an update through it is dropped.
 */
export function writeCard<T>({ editor, getPos, node }: Pick<ReactNodeViewProps, 'editor' | 'getPos' | 'node'>, change: (data: T) => T): void {
  const { state } = editor
  const id = node.attrs.id as string | null
  const pos = getPos()
  const here = typeof pos === 'number' ? state.doc.nodeAt(pos) : null
  let at: number | null = here && here.type === node.type && (!id || here.attrs.id === id) ? (pos as number) : null
  if (at === null && id) state.doc.forEach((card, offset) => void (at === null && card.type === node.type && card.attrs.id === id && (at = offset)))
  if (at === null) return
  const card = state.doc.nodeAt(at)!
  editor.view.dispatch(state.tr.setNodeMarkup(at, undefined, { ...card.attrs, data: change((card.attrs.data ?? node.attrs.data) as T) }))
}

type TableData = { hasHeaderRow: boolean; rows: Inline[][] }

export function TableView({ node, selected, editor, getPos }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const data = node.attrs.data as TableData
  const update = (change: (d: TableData) => TableData) => writeCard<TableData>({ editor, getPos, node }, change)
  const columns = data.rows[0]?.length ?? 1
  const setCell = (r: number, c: number, value: string) => update((d) => ({ ...d, rows: d.rows.map((row, i) => (i === r ? row.map((cell, j) => (j === c ? textToInline(value) : cell)) : row)) }))
  return (
    <AtomCard label={t('cards.table')} selected={selected}>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <tbody>
            {data.rows.map((row, r) => (
              <tr key={r}>
                {row.map((cell, c) => (
                  <td key={c} className="border border-border p-0">
                    <input
                      className={cn('w-full min-w-24 border-0 bg-transparent px-2 py-1.5 focus:bg-accent-soft focus:outline-none', r === 0 && data.hasHeaderRow && 'font-semibold')}
                      aria-label={t('cell', { row: r + 1, column: c + 1 })}
                      value={inlineText(cell)}
                      onChange={(e) => setCell(r, c, e.target.value)}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="flex flex-wrap gap-2 text-xs">
        <button type="button" className={control} onClick={() => update((d) => ({ ...d, rows: [...d.rows, Array.from({ length: d.rows[0]?.length ?? 1 }, () => [])] }))} disabled={data.rows.length >= 200}>
          {t('addRow')}
        </button>
        <button type="button" className={control} onClick={() => update((d) => ({ ...d, rows: d.rows.map((row) => [...row, []]) }))} disabled={columns >= 20}>
          {t('addColumn')}
        </button>
        <button type="button" className={control} onClick={() => update((d) => ({ ...d, rows: d.rows.slice(0, -1) }))} disabled={data.rows.length <= 1}>
          {t('removeRow')}
        </button>
        <button type="button" className={control} onClick={() => update((d) => ({ ...d, rows: d.rows.map((row) => row.slice(0, -1)) }))} disabled={columns <= 1}>
          {t('removeColumn')}
        </button>
        <label className="flex items-center gap-1.5">
          <input type="checkbox" checked={data.hasHeaderRow} onChange={(e) => update((d) => ({ ...d, hasHeaderRow: e.target.checked }))} />
          {t('headerRow')}
        </label>
      </div>
    </AtomCard>
  )
}

type QuestionData = { prompt: Doc; answer: Doc; hint?: Doc }

export function QuestionView({ node, selected, editor, getPos }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const data = node.attrs.data as QuestionData
  const set = (patch: Partial<QuestionData>) => writeCard<QuestionData>({ editor, getPos, node }, (d) => ({ ...d, ...patch }))
  return (
    <AtomCard label={t('cards.question')} selected={selected}>
      <Field label={t('prompt')} value={docText(data.prompt)} onChange={(v) => set({ prompt: textToDoc(v) })} />
      <Field label={t('answer')} value={docText(data.answer)} onChange={(v) => set({ answer: textToDoc(v) })} />
      <Field label={t('hint')} value={data.hint ? docText(data.hint) : ''} onChange={(v) => set({ hint: v ? textToDoc(v) : undefined })} rows={1} />
    </AtomCard>
  )
}

type QuizData = { question: Doc; choices: { id: string; content: Inline }[]; correct: string[]; multiple: boolean; explanation?: Doc }

export function QuizView({ node, selected, editor, getPos }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const data = node.attrs.data as QuizData
  const group = useId()
  const update = (change: (d: QuizData) => QuizData) => writeCard<QuizData>({ editor, getPos, node }, change)
  const toggle = (id: string, on: boolean) =>
    update((d) => {
      const correct = d.multiple ? (on ? [...d.correct, id] : d.correct.filter((c) => c !== id)) : [id]
      return { ...d, correct: correct.length ? correct : d.correct }
    })
  const nextId = (d: QuizData) => 'abcdefgh'.split('').find((l) => !d.choices.some((c) => c.id === l)) ?? newCardId().slice(-8)
  return (
    <AtomCard label={t('cards.quiz')} selected={selected}>
      <Field label={t('question')} value={docText(data.question)} onChange={(v) => update((d) => ({ ...d, question: textToDoc(v) }))} />
      <fieldset className="flex flex-col gap-1.5">
        <legend className="mb-1">
          <Label>{t('choices')}</Label>
        </legend>
        {data.choices.map((choice, i) => (
          <div key={choice.id} className="flex items-center gap-2">
            <input
              type={data.multiple ? 'checkbox' : 'radio'}
              name={group}
              aria-label={t('correctChoice', { n: i + 1 })}
              checked={data.correct.includes(choice.id)}
              onChange={(e) => toggle(choice.id, e.target.checked)}
            />
            <input className={cn(control, 'min-w-0 flex-1')} aria-label={t('choice', { n: i + 1 })} value={inlineText(choice.content)} onChange={(e) => update((d) => ({ ...d, choices: d.choices.map((c) => (c.id === choice.id ? { ...c, content: textToInline(e.target.value) } : c)) }))} />
            <button
              type="button"
              className="text-xs text-muted hover:text-fg disabled:opacity-40"
              disabled={data.choices.length <= 2}
              aria-label={t('removeChoice', { n: i + 1 })}
              onClick={() =>
                update((d) => {
                  const choices = d.choices.filter((c) => c.id !== choice.id)
                  const correct = d.correct.filter((c) => c !== choice.id)
                  return { ...d, choices, correct: correct.length ? correct : [choices[0]!.id] }
                })
              }
            >
              ✕
            </button>
          </div>
        ))}
      </fieldset>
      <div className="flex flex-wrap items-center gap-3 text-xs">
        <button type="button" className={control} disabled={data.choices.length >= 8} onClick={() => update((d) => ({ ...d, choices: [...d.choices, { id: nextId(d), content: [] }] }))}>
          {t('addChoice')}
        </button>
        <label className="flex items-center gap-1.5">
          <input type="checkbox" checked={data.multiple} onChange={(e) => update((d) => ({ ...d, multiple: e.target.checked, correct: e.target.checked ? d.correct : d.correct.slice(0, 1) }))} />
          {t('multipleAnswers')}
        </label>
      </div>
      <Field label={t('explanation')} value={data.explanation ? docText(data.explanation) : ''} onChange={(v) => update((d) => ({ ...d, explanation: v ? textToDoc(v) : undefined }))} rows={1} />
    </AtomCard>
  )
}

type FlashcardData = { front: Doc; back: Doc }

export function FlashcardView({ node, selected, editor, getPos }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  const data = node.attrs.data as FlashcardData
  return (
    <AtomCard label={t('cards.flashcard')} selected={selected}>
      <div className="grid gap-2 sm:grid-cols-2">
        <Field label={t('front')} value={docText(data.front)} onChange={(v) => writeCard<FlashcardData>({ editor, getPos, node }, (d) => ({ ...d, front: textToDoc(v) }))} rows={3} />
        <Field label={t('back')} value={docText(data.back)} onChange={(v) => writeCard<FlashcardData>({ editor, getPos, node }, (d) => ({ ...d, back: textToDoc(v) }))} rows={3} />
      </div>
    </AtomCard>
  )
}

export function OpaqueView({ node, selected }: ReactNodeViewProps) {
  const t = useTranslations('notes.editor')
  return (
    <AtomCard label={t('cards.other', { type: String(node.attrs.cardType) })} selected={selected}>
      <p className="text-sm text-muted">{t('notEditableHere')}</p>
    </AtomCard>
  )
}
