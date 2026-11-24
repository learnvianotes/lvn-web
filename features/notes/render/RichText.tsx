import Link from 'next/link'
import { Fragment, type ReactNode } from 'react'
import type { BlockNode, Doc, Inline, Mark } from '@/lib/contracts/validation'
import { safeLinkHref } from '@/lib/http-url'

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
        return <mark className="rounded bg-warn/70 px-0.5 text-fg">{inner}</mark>
      case 'subscript':
        return <sub>{inner}</sub>
      case 'superscript':
        return <sup>{inner}</sup>
      case 'link': {
        // The API validates links. Check again here: a stored javascript: or data: URL would run in this page.
        const href = safeLinkHref(mark.attrs.href, { mailto: true })
        if (!href) return inner
        return (
          <a href={href} rel="nofollow ugc noopener" target="_blank" className="text-accent underline underline-offset-2">
            {inner}
          </a>
        )
      }
      default:
        return inner
    }
  }, text)
}

/** Comments and posts link `@handle` to the person's profile (lvn-backend ADR-0054); note content does not. */
const MENTION = /(^|[^A-Za-z0-9@.])@([A-Za-z0-9]{3,40})\b/g

function withMentions(text: string): ReactNode {
  const parts: ReactNode[] = []
  let last = 0
  for (const m of text.matchAll(MENTION)) {
    const at = m.index! + m[1]!.length
    parts.push(text.slice(last, at))
    parts.push(
      <Link key={at} href={`/u/${m[2]!.toLowerCase()}`} className="font-semibold text-accent hover:underline">
        @{m[2]}
      </Link>,
    )
    last = at + 1 + m[2]!.length
  }
  if (!parts.length) return text
  parts.push(text.slice(last))
  return parts
}

export function InlineText({ content, mentions = false }: { content: Inline | undefined; mentions?: boolean }) {
  return (
    <>
      {(content ?? []).map((n, i) => (
        <Fragment key={i}>{n.type === 'hardBreak' ? <br /> : withMarks(mentions && !n.marks?.some((m) => m.type === 'link' || m.type === 'code') ? withMentions(n.text) : n.text, n.marks)}</Fragment>
      ))}
    </>
  )
}

function Block({ node, mentions }: { node: BlockNode; mentions: boolean }) {
  if (node.type === 'paragraph') {
    return (
      <p className="min-h-[1.5em]">
        <InlineText content={node.content} mentions={mentions} />
      </p>
    )
  }
  const List = node.type === 'bulletList' ? 'ul' : 'ol'
  return (
    <List className={node.type === 'bulletList' ? 'list-disc pl-6' : 'list-decimal pl-6'} start={node.type === 'orderedList' ? node.attrs?.start : undefined}>
      {node.content.map((item, i) => (
        <li key={i}>
          <Blocks nodes={item.content} mentions={mentions} />
        </li>
      ))}
    </List>
  )
}

function Blocks({ nodes, mentions }: { nodes: readonly BlockNode[]; mentions: boolean }) {
  return (
    <>
      {nodes.map((n, i) => (
        <Block key={i} node={n} mentions={mentions} />
      ))}
    </>
  )
}

export function RichDoc({ doc, className, mentions = false }: { doc: Doc | undefined; className?: string; mentions?: boolean }) {
  return (
    <div className={className ?? 'flex flex-col gap-2'}>
      <Blocks nodes={doc?.content ?? []} mentions={mentions} />
    </div>
  )
}
