/* SVG drawings from the content pipeline. The markup is inserted as HTML, so anything scriptable is removed first. */

import { parseHTML } from 'linkedom'

const DROP = new Set(['script', 'foreignobject', 'iframe', 'object', 'embed', 'link', 'meta', 'style'])

/** A fragment (`#id`) or an absolute web/mail URL. `javascript:` and `data:` are not. */
function safeRef(value: string): boolean {
  const v = value.trim()
  if (v.startsWith('#') && !/[\s<>"']/.test(v)) return true
  if (/[\u0000-\u001F\u007F\\]/.test(v)) return false
  return /^(https?:|mailto:)/i.test(v)
}

/** `url(#id)` may stay. Any other url() or a scriptable scheme may not. */
function dangerousValue(value: string): boolean {
  if (/javascript:|vbscript:|data:/i.test(value)) return true
  return /url\s*\(\s*['"]?(?!#)/i.test(value)
}

/**
 * SVG inner markup safe to assign as HTML. Fragment references (`url(#marker)`, `href="#id"`) are kept.
 * Scripts, foreignObject, event handlers, and scriptable URLs are removed.
 */
export function sanitizeSvgMarkup(html: string): string {
  const { document } = parseHTML(`<svg xmlns="http://www.w3.org/2000/svg">${html}</svg>`)
  const root = document.querySelector('svg')
  if (!root) return ''
  for (const el of [...root.querySelectorAll('*')]) {
    if (DROP.has(el.tagName.toLowerCase())) {
      el.remove()
      continue
    }
    for (const attr of [...el.attributes]) {
      const name = attr.name.toLowerCase()
      if (name.startsWith('on') || dangerousValue(attr.value)) {
        el.removeAttribute(attr.name)
        continue
      }
      if ((name === 'href' || name.endsWith(':href') || name === 'src') && !safeRef(attr.value)) el.removeAttribute(attr.name)
    }
  }
  return root.innerHTML
}
