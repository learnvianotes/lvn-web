/* ============================================================
   Fidelity check: does content, rendered by the app's own
   components, reproduce the source HTML?

   Both sides are parsed and reduced to a canonical form that
   keeps everything that matters — every element, class,
   attribute, text run and code block — and drops only what
   can't matter:
     • whitespace between blocks (see childItems)
     • attribute / class order, style formatting
     • UI chrome added by components (marked `data-ui`),
       `hidden` on inactive tabs, anchor ids
     • syntax-highlight markup inside code (text must match exactly)
   ============================================================ */

import { parseHTML } from 'linkedom'
import { renderToStaticMarkup } from 'react-dom/server'
import { createElement } from 'react'
import type { Content } from '../../../schema/content'
import { ContentView } from '../../../src/features/content/ContentView'
import { childItems } from './fromHtml'

const IGNORED_ATTRS = new Set(['hidden', 'id'])

function canonStyle(style: string) {
  return style
    .split(';')
    .map((d) => d.trim())
    .filter(Boolean)
    .map((d) => {
      const i = d.indexOf(':')
      return `${d.slice(0, i).trim().toLowerCase()}:${d.slice(i + 1).trim().replace(/\s+/g, ' ')}`
    })
    .sort()
    .join(';')
}

function canon(el: Element): string {
  if (el.hasAttribute('data-ui')) return ''
  const tag = el.tagName.toLowerCase()
  const attrs = [...el.attributes]
    .filter((a) => !IGNORED_ATTRS.has(a.name.toLowerCase()) && a.name !== 'data-ui')
    .map((a) => {
      const name = a.name.toLowerCase()
      if (name === 'class') return `class="${a.value.split(/\s+/).filter(Boolean).sort().join(' ')}"`
      if (name === 'style') return `style="${canonStyle(a.value)}"`
      return `${name}="${a.value}"`
    })
    .filter((a) => a !== 'class=""')
    .sort()
  const open = `<${tag}${attrs.length ? ' ' + attrs.join(' ') : ''}>`
  if (tag === 'pre') return `${open}${JSON.stringify(el.textContent ?? '')}</pre>`
  // Adjacent text runs are merged (the parser splits them around entities; React separates
  // them with comments) and the same whitespace rule as the converter is applied.
  let inner = ''
  for (const it of childItems(el)) inner += it.kind === 'text' ? it.value : canon(it.el)
  return `${open}${inner}</${tag}>`
}

export function canonFragment(html: string): string {
  const { document } = parseHTML(`<!doctype html><html><body><div id="__c">${html}</div></body></html>`)
  return canon(document.getElementById('__c') as unknown as Element)
}

/** Render content with the app's ContentView; returns the inner HTML of its wrapper. */
export function renderContent(content: Content): string {
  const html = renderToStaticMarkup(createElement(ContentView, { content }))
  const m = html.match(/^<div class="prose">([\s\S]*)<\/div>$/)
  if (!m) throw new Error('unexpected ContentView wrapper')
  return m[1]
}

/** null when identical; otherwise a short description of the first difference. */
export function compareContent(sourceHtml: string, content: Content): string | null {
  const a = canonFragment(sourceHtml)
  const b = canonFragment(renderContent(content))
  if (a === b) return null
  let i = 0
  while (i < a.length && a[i] === b[i]) i++
  const ctx = (s: string) => s.slice(Math.max(0, i - 80), i + 80).replace(/\n/g, '⏎')
  return `first difference at char ${i}\n    source:   …${ctx(a)}…\n    rendered: …${ctx(b)}…`
}
