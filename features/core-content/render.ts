import hljs from 'highlight.js'
import { parseHTML } from 'linkedom'

/**
 * Turns pipeline HTML (content-build/, already sanitised by scripts/content/sanitize.mjs) into
 * the markup the /core pages ship: highlighted code, accessible tab sets and anchored section
 * headings. Runs at build time only — readers download HTML and CSS, no highlighter.
 */

export interface Heading {
  id: string
  text: string
}

export interface Rendered {
  html: string
  headings: Heading[]
}

const LANG: Record<string, string> = {
  py: 'python', js: 'javascript', ts: 'typescript', cpp: 'cpp', c: 'c', java: 'java',
  sql: 'sql', bash: 'bash', sh: 'bash', json: 'json',
}

export const LANG_LABEL: Record<string, string> = { py: 'Python', cpp: 'C++', java: 'Java', js: 'JavaScript' }

export function escapeHtml(text: string): string {
  return text.replace(/[&<>"']/g, (c) => `&${{ '&': 'amp', '<': 'lt', '>': 'gt', '"': 'quot', "'": '#39' }[c]};`)
}

export function slugify(text: string): string {
  return text.toLowerCase().normalize('NFKD').replace(/[^\p{L}\p{N}]+/gu, '-').replace(/^-+|-+$/g, '') || 'section'
}

function highlight(code: string, lang: string | null): string {
  const language = lang ? LANG[lang] : undefined
  return language ? hljs.highlight(code, { language, ignoreIllegals: true }).value : escapeHtml(code)
}

/** @param idPrefix keeps tab ids unique when several fragments share one page */
export function renderContent(html: string, idPrefix = 'c'): Rendered {
  const { document } = parseHTML(`<!doctype html><html><body><main>${html}</main></body></html>`)
  const root = document.querySelector('main')!

  for (const figure of root.querySelectorAll('figure.code')) {
    const code = figure.querySelector('pre > code')
    if (!code) continue
    const lang = figure.getAttribute('data-lang')
    code.innerHTML = highlight(code.textContent ?? '', lang)
    code.setAttribute('class', `hljs${lang ? ` language-${LANG[lang] ?? lang}` : ''}`)
    figure.querySelector('pre')?.setAttribute('tabindex', '0')
  }

  root.querySelectorAll('.tabs').forEach((tabs, t) => {
    const panels = [...tabs.children].filter((el) => el.classList.contains('tab-panel'))
    if (panels.length < 2) return
    tabs.setAttribute('data-tabs', '')
    const bar = document.createElement('div')
    bar.setAttribute('class', 'tab-bar')
    bar.setAttribute('role', 'tablist')
    panels.forEach((panel, i) => {
      const label = panel.getAttribute('data-label') ?? `Tab ${i + 1}`
      const tabId = `${idPrefix}-t${t}-${i}`
      const button = document.createElement('button')
      button.setAttribute('type', 'button')
      button.setAttribute('role', 'tab')
      button.setAttribute('id', tabId)
      button.setAttribute('aria-controls', `${tabId}-panel`)
      button.setAttribute('aria-selected', String(i === 0))
      button.setAttribute('tabindex', i === 0 ? '0' : '-1')
      button.setAttribute('data-label', label)
      button.textContent = label
      bar.appendChild(button)
      panel.setAttribute('role', 'tabpanel')
      panel.setAttribute('id', `${tabId}-panel`)
      panel.setAttribute('aria-labelledby', tabId)
      if (i > 0) panel.setAttribute('hidden', '')
    })
    tabs.insertBefore(bar, tabs.firstChild)
  })

  const headings: Heading[] = []
  const used = new Set<string>()
  for (const h of root.querySelectorAll('section.block > h3')) {
    const text = (h.textContent ?? '').trim()
    let id = slugify(text)
    for (let n = 2; used.has(id); n++) id = `${slugify(text)}-${n}`
    used.add(id)
    h.setAttribute('id', id)
    headings.push({ id, text })
  }

  // Wide tables scroll sideways; keyboard users need to be able to focus them to scroll.
  for (const wrap of root.querySelectorAll('.table-wrap')) {
    wrap.setAttribute('tabindex', '0')
    wrap.setAttribute('role', 'region')
    wrap.setAttribute('aria-label', 'Table')
  }

  for (const a of root.querySelectorAll('a[href^="http"]')) {
    a.setAttribute('rel', 'noopener nofollow ugc')
    a.setAttribute('target', '_blank')
  }

  return { html: root.innerHTML, headings }
}

/** A solution's code in every language as one tab set, rendered like the notes' code tabs. */
export function codeTabsHtml(code: Record<string, string>): string {
  const panels = Object.entries(code)
    .filter(([, src]) => src.trim())
    .map(([lang, src]) => {
      const label = LANG_LABEL[lang] ?? lang
      return `<div class="tab-panel" data-label="${escapeHtml(label)}"><figure class="code" data-lang="${escapeHtml(lang)}"><figcaption>${escapeHtml(label)}</figcaption><pre><code>${escapeHtml(src)}</code></pre></figure></div>`
    })
  return panels.length ? `<div class="tabs">${panels.join('')}</div>` : ''
}
