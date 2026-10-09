import type { CardType } from '@/lib/contracts/domain/enums'
import { useTranslations } from 'next-intl'
import { cardAnchor, type CardAnchor, type Doc, type Inline } from '@/lib/contracts/validation'
import { cn } from '@/lib/cn'
import { FlashcardCardView, QuestionCardView, QuizCardView } from './interactive'
import { MediaBlock } from './MediaBlock'
import { InlineText, RichDoc } from './RichText'

/**
 * One card, read-only (readers, version previews, the public note page). The content was validated by the API; a card
 * of a type this build does not know is skipped.
 */

const CALLOUT: Record<string, string> = {
  note: 'border-border bg-surface-2',
  info: 'border-sky-500/40 bg-sky-500/10',
  tip: 'border-emerald-500/40 bg-emerald-500/10',
  warning: 'border-amber-500/40 bg-amber-500/10',
  danger: 'border-red-500/40 bg-red-500/10',
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any -- card content is checked per type by the API
type Any = any

/**
 * `onAnchor` opens the PDF a card came from (lvn-backend ADR-0040); without it the card only says which page.
 */
export function CardView({ id, type, content, highlighted, onAnchor }: { id: string; type: CardType; content: unknown; highlighted?: boolean; onAnchor?: (anchor: CardAnchor, cardId: string) => void }) {
  const t = useTranslations('notes.editor')
  const c = content as Any
  const body = (() => {
    switch (type) {
      case 'text':
        return <RichDoc doc={c.doc as Doc} />
      case 'heading': {
        const H = `h${c.level}` as 'h1' | 'h2' | 'h3'
        return (
          <H id={`card-${id}`} className={cn('scroll-mt-20 font-bold tracking-tight', c.level === 1 ? 'text-3xl' : c.level === 2 ? 'text-2xl' : 'text-xl')}>
            <InlineText content={c.content as Inline} />
          </H>
        )
      }
      case 'quote':
        return (
          <blockquote className="border-l-4 border-accent/50 pl-4 italic">
            <RichDoc doc={c.doc as Doc} />
            {c.attribution ? <footer className="mt-1 text-sm not-italic text-muted">— {c.attribution}</footer> : null}
          </blockquote>
        )
      case 'callout':
        return (
          <aside className={cn('rounded-xl border p-3', CALLOUT[c.variant as string])}>
            {c.title ? <p className="mb-1 font-semibold">{c.title}</p> : null}
            <RichDoc doc={c.doc as Doc} />
          </aside>
        )
      case 'checklist':
        return (
          <ul className="flex flex-col gap-1">
            {(c.items as { id: string; checked: boolean; content: Inline }[]).map((item) => (
              <li key={item.id} className="flex items-start gap-2">
                <input type="checkbox" checked={item.checked} readOnly disabled className="mt-1.5 size-4" aria-label={item.checked ? 'done' : 'not done'} />
                <span className={cn(item.checked && 'text-muted line-through')}>
                  <InlineText content={item.content} />
                </span>
              </li>
            ))}
          </ul>
        )
      case 'code':
      case 'markdown':
      case 'diagram':
        return (
          <figure className="overflow-hidden rounded-xl border border-border bg-surface-2">
            {type === 'code' && (c.filename || c.language) ? <figcaption className="border-b border-border px-3 py-1.5 font-mono text-xs text-muted">{c.filename || c.language}</figcaption> : null}
            <pre className="overflow-x-auto p-3 font-mono text-sm leading-relaxed">
              <code>{type === 'code' ? c.code : c.source}</code>
            </pre>
            {type === 'diagram' && c.caption ? (
              <figcaption className="px-3 pb-2 text-sm text-muted">
                <InlineText content={c.caption as Inline} />
              </figcaption>
            ) : null}
          </figure>
        )
      case 'table': {
        const rows = c.rows as Inline[][]
        const [head, ...rest] = c.hasHeaderRow ? rows : [null, ...rows]
        return (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              {head ? (
                <thead>
                  <tr>
                    {head.map((cell, i) => (
                      <th key={i} className="border border-border bg-surface-2 px-2 py-1.5 text-left font-semibold">
                        <InlineText content={cell} />
                      </th>
                    ))}
                  </tr>
                </thead>
              ) : null}
              <tbody>
                {rest.map((row, r) => (
                  <tr key={r}>
                    {row!.map((cell, i) => (
                      <td key={i} className="border border-border px-2 py-1.5">
                        <InlineText content={cell} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )
      }
      case 'question':
        return <QuestionCardView content={c} />
      case 'quiz':
        return <QuizCardView content={c} />
      case 'flashcard':
        return <FlashcardCardView content={c} />
      case 'image':
      case 'video':
      case 'audio':
      case 'file':
        return <MediaBlock type={type} content={c} />
      default:
        return null
    }
  })()
  if (!body) return null
  const anchor = cardAnchor(content)
  return (
    <section data-card-id={id} data-card-type={type} className={cn('flex flex-col rounded-lg transition-colors', highlighted && 'bg-accent-soft ring-2 ring-accent/30')}>
      {body}
      {anchor ? (
        onAnchor ? (
          <button type="button" className="lvn-anchor-chip mt-1.5" title={anchor.quote} onClick={() => onAnchor(anchor, id)}>
            ↗ {t('anchorPage', { page: anchor.page })}
          </button>
        ) : (
          <span className="mt-1 self-end text-xs text-muted">{t('fromPage', { page: anchor.page })}</span>
        )
      ) : null}
    </section>
  )
}
