/* ============================================================
   HTML → structured content (schema/content.ts).

   Input is the normalized HTML produced by extract.mjs (the
   vocabulary in sanitize.mjs). The conversion is strict: an
   element, class or attribute it doesn't know is an error, so
   nothing is ever dropped silently.
   ============================================================ */

import { parseHTML } from 'linkedom'
import type { Content, ContentNode, NodeType } from '@core-schema/content'

export class ConvertError extends Error {}

type El = Element

const classesOf = (el: El) => (el.getAttribute('class') ?? '').split(/\s+/).filter(Boolean)

/** Block containers: whitespace-only text next to a block (or at the edges) carries no meaning. */
export const BLOCK_TAGS = new Set([
  'section', 'div', 'p', 'ul', 'ol', 'li', 'figure', 'figcaption', 'pre', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
  'h3', 'h4', 'h5', 'details', 'summary', 'footer', 'svg',
])

export type Item = { kind: 'text'; value: string } | { kind: 'el'; el: El }

const isBlockEl = (it: Item | undefined) => it?.kind === 'el' && BLOCK_TAGS.has(it.el.tagName.toLowerCase())

/**
 * An element's children with adjacent text nodes merged (the parser splits text around
 * entities like &quot;) and comments dropped. Whitespace-only text is kept only between two
 * inline neighbours — at the edges of an element or next to a block it renders as nothing.
 * The same rule is used when verifying, so both sides agree.
 */
export function childItems(el: El): Item[] {
  const raw: Item[] = []
  for (const n of el.childNodes) {
    if (n.nodeType === 3) {
      const last = raw[raw.length - 1]
      if (last?.kind === 'text') last.value += n.textContent ?? ''
      else raw.push({ kind: 'text', value: n.textContent ?? '' })
    } else if (n.nodeType === 1) {
      raw.push({ kind: 'el', el: n as El })
    } else if (n.nodeType !== 8) {
      throw new ConvertError(`unexpected node type ${n.nodeType}`)
    }
  }
  return raw.filter((it, i) => {
    if (it.kind !== 'text' || it.value.trim()) return true
    const prev = raw[i - 1], next = raw[i + 1]
    return !!prev && !!next && !isBlockEl(prev) && !isBlockEl(next)
  })
}

const CLASS_TYPES: Record<string, NodeType> = {
  card: 'card', 'callout-label': 'calloutLabel', 'flow': 'flow', 'flow-node': 'flowNode', 'flow-arrow': 'flowArrow',
  step: 'step', 'step-num': 'stepNum', 'step-body': 'stepBody', 'step-title': 'stepTitle', 'step-desc': 'stepDesc',
  chips: 'chips', chip: 'chip', kv: 'kv', 'kv-key': 'kvKey', 'kv-value': 'kvValue', formula: 'formula',
  bits: 'bits', bit: 'bit', gantt: 'gantt', 'gantt-block': 'ganttBlock', 'gantt-scale': 'ganttScale',
  tabs: 'tabs', 'tab-panel': 'tabPanel',
}
/** Types that are normally `div`s but may appear as inline `span`s. */
const INLINE_CAPABLE = new Set<NodeType>(['chip', 'stepDesc', 'kvKey', 'kvValue'])
/** Types whose default tag is `span`. */
const SPAN_DEFAULT = new Set<NodeType>(['kvKey', 'kvValue'])

const INLINE_TAGS: Record<string, NodeType> = {
  strong: 'strong', em: 'em', u: 'u', code: 'code', sup: 'sup', sub: 'sub', small: 'small', br: 'br',
}

function fail(el: El, where: string, why: string): never {
  throw new ConvertError(`${where}: ${why} — <${el.tagName.toLowerCase()} class="${el.getAttribute('class') ?? ''}"> ${el.outerHTML.slice(0, 160)}`)
}

function allowOnly(el: El, where: string, allowed: string[]) {
  for (const a of el.attributes) if (a.name !== 'class' && !allowed.includes(a.name)) fail(el, where, `unexpected attribute "${a.name}"`)
}

function children(el: El, where: string): ContentNode[] {
  return childItems(el).map((it) => (it.kind === 'text' ? { type: 'text', value: it.value } : convert(it.el, where)))
}

function withStyle(node: ContentNode, el: El): ContentNode {
  const style = el.getAttribute('style')
  if (style) node.style = style
  return node
}

function convert(el: El, where: string): ContentNode {
  const tag = el.tagName.toLowerCase()
  const cls = classesOf(el)
  const one = (type: NodeType, extra: Partial<ContentNode> = {}): ContentNode => {
    const node: ContentNode = { type, ...extra }
    const kids = children(el, where)
    if (kids.length) node.children = kids
    return withStyle(node, el)
  }

  switch (tag) {
    case 'section':
      if (cls.join(' ') !== 'block') fail(el, where, 'section without class "block"')
      allowOnly(el, where, [])
      return one('section')
    case 'h3': case 'h4': case 'h5':
      if (cls.length) fail(el, where, 'heading with a class')
      allowOnly(el, where, [])
      return one('heading', { level: Number(tag[1]) })
    case 'p': {
      allowOnly(el, where, ['style'])
      const variant = cls.join(' ')
      if (variant && !['lead', 'muted', 'mono'].includes(variant)) fail(el, where, 'unknown paragraph class')
      return one('paragraph', variant ? { variant } : {})
    }
    case 'ul': case 'ol':
      if (cls.length) fail(el, where, 'list with a class')
      allowOnly(el, where, ['style'])
      return one('list', { ordered: tag === 'ol' })
    case 'li':
      if (cls.length) fail(el, where, 'li with a class')
      allowOnly(el, where, ['style'])
      return one('listItem')
    case 'figure': {
      if (cls.join(' ') !== 'code') fail(el, where, 'figure that is not a code block')
      allowOnly(el, where, ['data-lang'])
      const kids = [...el.children]
      const cap = kids.find((k) => k.tagName === 'FIGCAPTION')
      const pre = kids.find((k) => k.tagName === 'PRE')
      if (!pre || kids.length !== (cap ? 2 : 1)) fail(el, where, 'code figure must hold [figcaption] + pre')
      if (pre.children.length !== 1 || pre.children[0]!.tagName !== 'CODE') fail(pre, where, 'pre must hold exactly one <code>')
      const node: ContentNode = { type: 'codeBlock', value: pre.textContent ?? '' }
      const lang = el.getAttribute('data-lang')
      if (lang) node.lang = lang
      if (cap) node.label = cap.textContent ?? ''
      return node
    }
    case 'table': {
      const wrap = el.parentElement
      if (!wrap || classesOf(wrap).join(' ') !== 'table-wrap') fail(el, where, 'table outside .table-wrap')
      allowOnly(el, where, ['style'])
      return one('table')
    }
    case 'thead': allowOnly(el, where, []); return one('tableHead')
    case 'tbody': allowOnly(el, where, []); return one('tableBody')
    case 'tr': allowOnly(el, where, []); return one('tableRow')
    case 'td': case 'th': {
      if (cls.length) fail(el, where, 'table cell with a class')
      allowOnly(el, where, ['rowspan', 'colspan', 'style'])
      const extra: Partial<ContentNode> = {}
      if (tag === 'th') extra.header = true
      const rs = el.getAttribute('rowspan'), cs = el.getAttribute('colspan')
      if (rs) extra.rowspan = Number(rs)
      if (cs) extra.colspan = Number(cs)
      return one('tableCell', extra)
    }
    case 'details':
      if (cls.join(' ') !== 'qa') fail(el, where, 'details without class "qa"')
      allowOnly(el, where, [])
      return one('qa')
    case 'summary':
      allowOnly(el, where, [])
      return one('qaQuestion')
    case 'svg': {
      const attrs: Record<string, string> = {}
      for (const a of el.attributes) {
        if (!['viewBox', 'width', 'height', 'xmlns', 'viewbox'].includes(a.name)) fail(el, where, `unexpected svg attribute "${a.name}"`)
        attrs[a.name === 'viewbox' ? 'viewBox' : a.name] = a.value
      }
      return { type: 'svg', value: el.innerHTML, attrs }
    }
    case 'footer': {
      allowOnly(el, where, [])
      if (!cls.length) return one('footer')
      // A footer styled as a callout.
      if (cls[0] !== 'callout' || cls.length > 2) fail(el, where, 'footer with an unknown class')
      const variant = cls[1] ? cls[1].replace(/^callout--/, '') : 'plain'
      return one('footer', { variant })
    }
    case 'a': {
      allowOnly(el, where, ['href', 'target', 'rel'])
      return one('link', { href: el.getAttribute('href') ?? '' })
    }
    case 'i': {
      allowOnly(el, where, [])
      if (cls.includes('ti')) {
        const name = cls.find((c) => c.startsWith('ti-'))
        if (!name || cls.length !== 2 || el.childNodes.length) fail(el, where, 'malformed icon')
        return { type: 'icon', icon: name }
      }
      if (cls.length) fail(el, where, 'i with an unknown class')
      return one('i')
    }
    case 'span': {
      allowOnly(el, where, ['style'])
      if (!cls.length) return one('span')
      const type = CLASS_TYPES[cls.join(' ')]
      if (!type || !INLINE_CAPABLE.has(type)) fail(el, where, 'span with an unknown class')
      return one(type, SPAN_DEFAULT.has(type) ? {} : { inline: true })
    }
    case 'div': {
      allowOnly(el, where, ['style', ...(cls.includes('tab-panel') ? ['data-label'] : [])])
      if (!cls.length) return one('group')
      const key = cls.join(' ')
      if (key === 'table-wrap') {
        if (el.children.length !== 1 || el.children[0]!.tagName !== 'TABLE' || children(el, where).length !== 1) fail(el, where, '.table-wrap must hold exactly one table')
        return convert(el.children[0]!, where)
      }
      if (key === 'muted' || key === 'mono') return one('group', { variant: key })
      if (cls[0] === 'callout' && cls.length <= 2) {
        const variant = cls[1] ? cls[1].replace(/^callout--/, '') : 'plain'
        if (!['def', 'example', 'note', 'warn', 'good', 'bad', 'plain'].includes(variant)) fail(el, where, 'unknown callout variant')
        return one('callout', { variant })
      }
      if (cls[0] === 'grid') {
        if (key !== 'grid' && key !== 'grid grid--3') fail(el, where, 'unknown grid')
        return one('grid', { cols: key === 'grid' ? 2 : 3 })
      }
      if (key === 'tab-panel') return one('tabPanel', { label: el.getAttribute('data-label') ?? '' })
      const type = CLASS_TYPES[key]
      if (!type) fail(el, where, 'div with an unknown class')
      return one(type)
    }
    default: {
      const type = INLINE_TAGS[tag]
      if (!type) fail(el, where, 'unknown element')
      if (cls.length) fail(el, where, 'inline element with a class')
      allowOnly(el, where, [])
      if (type === 'br') return { type: 'br' }
      return one(type)
    }
  }
}

/** Convert one HTML fragment; `where` names it in error messages. */
export function htmlToContent(html: string, where: string): Content {
  const { document } = parseHTML(`<!doctype html><html><body><div id="__root">${html}</div></body></html>`)
  const root = document.getElementById('__root')!
  return children(root as unknown as El, where)
}
