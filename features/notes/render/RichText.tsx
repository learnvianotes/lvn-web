import { Fragment, type ReactNode } from 'react'
import type { BlockNode, Doc, Inline, Mark } from '@/lib/contracts/validation'

/**
 * Card rich text as React elements — never as HTML strings (web addendum: user notes are rendered through components).
 * Works on the server (public note pages) and in the browser. Links leave with rel="nofollow ugc noopener".
 */

function withMarks(text: ReactNode, marks: Mark[] | undefined): ReactNode {
  return (marks ?? []).reduceRight<ReactNode>((inner, mark) => {
    switch (mark.type) {
      case 'bold':
        return <strong>{inner}</strong>
      case 'italic':
        return <em>{inner}</em>
      case 'underline':
        return <u>{inner}</u>
      case 'strike':
        return <s>{inner}</s>
      case 'code':
        return <code className="rounded bg-surface-2 px-1 py-0.5 font-mono text-[0.9em]">{inner}</code>
      case 'highlight':
        return <mark className="rounded bg-amber-200/70 px-0.5 text-fg dark:bg-amber-400/30">{inner}</mark>
      case 'subscript':
        return <sub>{inner}</sub>
      case 'superscript':
        return <sup>{inner}</sup>
      case 'link':
        return (
          <a href={mark.attrs.href} rel="nofollow ugc noopener" target="_blank" className="text-accent underline underline-offset-2">
            {inner}
          </a>
        )
      default:
        return inner
    }
  }, text)
}

export function InlineText({ content }: { content: Inline | undefined }) {
  return (
    <>
      {(content ?? []).map((n, i) => (
        <Fragment key={i}>{n.type === 'hardBreak' ? <br /> : withMarks(n.text, n.marks)}</Fragment>
      ))}
    </>
  )
}

function Block({ node }: { node: BlockNode }) {
  if (node.type === 'paragraph') {
    return (
      <p className="min-h-[1.5em]">
        <InlineText content={node.content} />
      </p>
    )
  }
  const List = node.type === 'bulletList' ? 'ul' : 'ol'
  return (
    <List className={node.type === 'bulletList' ? 'list-disc pl-6' : 'list-decimal pl-6'} start={node.type === 'orderedList' ? node.attrs?.start : undefined}>
      {node.content.map((item, i) => (
        <li key={i}>
          <Blocks nodes={item.content} />
        </li>
      ))}
    </List>
  )
}

function Blocks({ nodes }: { nodes: readonly BlockNode[] }) {
  return (
    <>
      {nodes.map((n, i) => (
        <Block key={i} node={n} />
      ))}
    </>
  )
}

export function RichDoc({ doc, className }: { doc: Doc | undefined; className?: string }) {
  return (
    <div className={className ?? 'flex flex-col gap-2'}>
      <Blocks nodes={doc?.content ?? []} />
    </div>
  )
}
