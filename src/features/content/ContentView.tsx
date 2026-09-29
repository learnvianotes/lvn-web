/* ============================================================
   ContentView — renders structured content (schema/content.ts)
   with one small component per node type. The markup and class
   names match the prose styles (shared/styles/prose.css), so every
   subject looks the same in light and dark mode.

   Interactive pieces (code blocks, tabs) are their own components;
   everything they add purely for the UI carries `data-ui` so tools
   that compare content with its source can ignore it.
   ============================================================ */

import { createContext, useContext, useMemo, type ReactNode } from 'react'
import type { Content, ContentNode } from '@schema/content'
import { CodeBlock } from './CodeBlock'
import { Tabs } from './Tabs'
import { parseStyle } from './style'
import { sectionAnchors } from './query'

/** Anchor ids (`sec-N`) for top-level sections — the study kit links to them. */
const AnchorContext = createContext<Map<ContentNode, string> | null>(null)

interface Props {
  content: Content
  className?: string
  /** give top-level sections `sec-N` ids (one per page) */
  anchors?: boolean
}

export function ContentView({ content, className = '', anchors = false }: Props) {
  const ids = useMemo(() => (anchors ? new Map(sectionAnchors(content).map((a) => [a.node, a.id])) : null), [content, anchors])
  return (
    <AnchorContext.Provider value={ids}>
      <div className={`prose ${className}`.trim()}>{renderAll(content)}</div>
    </AnchorContext.Provider>
  )
}

function renderAll(nodes: ContentNode[] | undefined): ReactNode {
  return nodes?.map((n, i) => <Node key={i} node={n} />)
}

const cx = (...c: (string | false | undefined)[]) => c.filter(Boolean).join(' ') || undefined

function Node({ node: n }: { node: ContentNode }): ReactNode {
  const anchors = useContext(AnchorContext)
  const kids = renderAll(n.children)
  const style = n.style ? parseStyle(n.style) : undefined

  switch (n.type) {
    /* inline */
    case 'text': return n.value
    case 'strong': return <strong>{kids}</strong>
    case 'em': return <em>{kids}</em>
    case 'i': return <i>{kids}</i>
    case 'u': return <u>{kids}</u>
    case 'code': return <code>{kids}</code>
    case 'sup': return <sup>{kids}</sup>
    case 'sub': return <sub>{kids}</sub>
    case 'small': return <small>{kids}</small>
    case 'span': return <span style={style}>{kids}</span>
    case 'br': return <br />
    case 'icon': return <i className={`ti ${n.icon}`} />
    case 'link': return <a href={n.href} target="_blank" rel="noopener noreferrer">{kids}</a>

    /* blocks */
    case 'section': return <section className="block">{kids}</section>
    case 'heading': {
      const H = `h${n.level ?? 3}` as 'h3' | 'h4' | 'h5'
      return <H id={anchors?.get(n)}>{kids}</H>
    }
    case 'paragraph': return <p className={n.variant} style={style}>{kids}</p>
    case 'group': return <div className={n.variant} style={style}>{kids}</div>
    case 'list': return n.ordered ? <ol style={style}>{kids}</ol> : <ul style={style}>{kids}</ul>
    case 'listItem': return <li style={style}>{kids}</li>
    case 'codeBlock': return <CodeBlock code={n.value ?? ''} lang={n.lang} caption={n.label} />
    case 'callout': return <div className={cx('callout', n.variant !== 'plain' && `callout--${n.variant}`)} style={style}>{kids}</div>
    case 'calloutLabel': return <div className="callout-label" style={style}>{kids}</div>
    case 'grid': return <div className={n.cols === 3 ? 'grid grid--3' : 'grid'} style={style}>{kids}</div>
    case 'card': return <div className="card" style={style}>{kids}</div>
    case 'table': return <div className="table-wrap"><table style={style}>{kids}</table></div>
    case 'tableHead': return <thead>{kids}</thead>
    case 'tableBody': return <tbody>{kids}</tbody>
    case 'tableRow': return <tr>{kids}</tr>
    case 'tableCell': {
      const Cell = n.header ? 'th' : 'td'
      return <Cell rowSpan={n.rowspan} colSpan={n.colspan} style={style}>{kids}</Cell>
    }
    case 'tabs':
      return (
        <Tabs
          panels={(n.children ?? []).map((p) => ({
            label: p.label ?? '',
            id: anchors?.get(p),
            style: p.style ? parseStyle(p.style) : undefined,
            content: renderAll(p.children),
          }))}
        />
      )
    case 'tabPanel': return <div id={anchors?.get(n)} className="tab-panel" data-label={n.label} style={style}>{kids}</div>
    case 'qa': return <details className="qa">{kids}</details>
    case 'qaQuestion': return <summary>{kids}</summary>
    case 'svg': return <svg {...svgAttrs(n.attrs)} dangerouslySetInnerHTML={{ __html: n.value ?? '' }} />
    case 'footer': return <footer className={n.variant ? cx('callout', n.variant !== 'plain' && `callout--${n.variant}`) : undefined}>{kids}</footer>
    default: {
      const cls = CLASS_OF[n.type]
      if (!cls) return null
      const Tag = n.inline || SPAN_TYPES.has(n.type) ? 'span' : 'div'
      return <Tag className={cls} style={style}>{kids}</Tag>
    }
  }
}

/** Simple styled containers: node type → class name. */
const CLASS_OF: Partial<Record<ContentNode['type'], string>> = {
  flow: 'flow', flowNode: 'flow-node', flowArrow: 'flow-arrow',
  step: 'step', stepNum: 'step-num', stepBody: 'step-body', stepTitle: 'step-title', stepDesc: 'step-desc',
  chips: 'chips', chip: 'chip', kv: 'kv', kvKey: 'kv-key', kvValue: 'kv-value', formula: 'formula',
  bits: 'bits', bit: 'bit', gantt: 'gantt', ganttBlock: 'gantt-block', ganttScale: 'gantt-scale',
}
const SPAN_TYPES = new Set<ContentNode['type']>(['kvKey', 'kvValue'])

function svgAttrs(attrs: Record<string, string> | undefined) {
  const out: Record<string, string> = {}
  for (const [k, v] of Object.entries(attrs ?? {})) if (k !== 'xmlns') out[k] = v
  return out
}
