import { Fragment, type ReactNode } from 'react'
import { parseMarkdown, type MdBlock, type MdInline } from '@/lib/markdown'
import { cn } from '@/lib/cn'

/** Markdown (AI results, Markdown cards) as React elements, never as HTML strings: see lib/markdown. */

/** How an answer's `[n]` citations show (Ask AI, lvn-backend ADR-0060); without it they stay text. */
type Cite = (n: number) => ReactNode
const CITATION = /\[(\d{1,2})\]/g

function withCitations(text: string, cite: Cite | undefined): ReactNode {
  if (!cite) return text
  const parts: ReactNode[] = []
  let last = 0
  for (const m of text.matchAll(CITATION)) {
    parts.push(text.slice(last, m.index))
    parts.push(<Fragment key={m.index}>{cite(Number(m[1]))}</Fragment>)
    last = m.index + m[0].length
  }
  if (!parts.length) return text
  parts.push(text.slice(last))
  return parts
}

function Inlines({ content, cite }: { content: MdInline[]; cite?: Cite }) {
  return (
    <>
      {content.map((n, i) => {
        switch (n.kind) {
          case 'text':
            return <Fragment key={i}>{withCitations(n.text, cite)}</Fragment>
          case 'code':
            return (
              <code key={i} className="rounded bg-surface-2 px-1 py-0.5 font-mono text-[0.9em]">
                {n.text}
              </code>
            )
          case 'strong':
            return (
              <strong key={i}>
                <Inlines content={n.children} cite={cite} />
              </strong>
            )
          case 'em':
            return (
              <em key={i}>
                <Inlines content={n.children} cite={cite} />
              </em>
            )
        }
      })}
    </>
  )
}

function Block({ block, cite }: { block: MdBlock; cite?: Cite }) {
  switch (block.kind) {
    case 'heading': {
      const H = `h${block.level + 2}` as 'h3' | 'h4' | 'h5'
      return (
        <H className={cn('font-bold tracking-tight', block.level === 1 ? 'text-xl' : block.level === 2 ? 'text-lg' : 'text-base')}>
          <Inlines content={block.content} cite={cite} />
        </H>
      )
    }
    case 'paragraph':
      return (
        <p>
          <Inlines content={block.content} cite={cite} />
        </p>
      )
    case 'code':
      return (
        <pre className="overflow-x-auto rounded-xl border border-border bg-surface-2 p-3 font-mono text-sm leading-relaxed">
          <code>{block.text}</code>
        </pre>
      )
    case 'list': {
      const List = block.ordered ? 'ol' : 'ul'
      return (
        <List className={block.ordered ? 'list-decimal pl-6' : 'list-disc pl-6'} start={block.ordered && block.start !== 1 ? block.start : undefined}>
          {block.items.map((item, i) => (
            <li key={i} className="[&>*+*]:mt-1.5">
              {item.map((b, j) => (
                <Block key={j} block={b} cite={cite} />
              ))}
            </li>
          ))}
        </List>
      )
    }
  }
}

export function Markdown({ source, className, cite }: { source: string; className?: string; cite?: Cite }) {
  return (
    <div className={className ?? 'flex flex-col gap-2.5'}>
      {parseMarkdown(source).map((b, i) => (
        <Block key={i} block={b} cite={cite} />
      ))}
    </div>
  )
}
