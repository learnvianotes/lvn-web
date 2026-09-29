/* ============================================================
   CONTENT PIPELINE — HTML normalizer
   Converts legacy, per-subject markup into the small
   content vocabulary styled by src/styles/prose.css:

     callout (+ callout--def|example|note|warn|good|bad), callout-label
     grid (+ grid--3), card, flow, flow-node, flow-arrow,
     chips, chip, step, step-num, step-body, step-title, step-desc,
     kv, kv-key, kv-value, lead, formula, bits, bit, gantt, gantt-block,
     code (figure), tabs, tab-panel[data-label], qa (details),
     table-wrap, ti ti-* (Tabler icons)

   Anything not in the vocabulary is dropped (class removed),
   so content always renders with the app's own design.
   ============================================================ */

/** legacy class -> new classes */
const CLASS_MAP = {
  def: 'callout callout--def', 'def-card': 'callout callout--def',
  example: 'callout callout--example', scenario: 'callout callout--example',
  'highlight-box': 'callout callout--note', 'learn-box': 'callout callout--note', note: 'callout callout--note',
  takeaway: 'callout callout--note', 'tip-item': 'callout callout--note', 'divider-note': 'callout callout--note',
  'estimate-box': 'callout callout--note', highlight: 'callout callout--note',
  'warning-box': 'callout callout--warn', warn: 'callout callout--warn', danger: 'callout callout--warn',
  pros: 'callout callout--good', 'pc-pro': 'callout callout--good', ok: 'callout callout--good', do: 'callout callout--good',
  cons: 'callout callout--bad', 'pc-con': 'callout callout--bad', dont: 'callout callout--bad',
  proscons: 'callout',
  label: 'callout-label', 'pc-head': 'callout-label', 'col-title': 'callout-label', 'cell-title': 'callout-label',
  'method-label': 'callout-label',
  'card-grid': 'grid', g2: 'grid', grid2: 'grid', 'pros-cons': 'grid', 'toc-cards': 'grid', 'metric-row-4': 'grid grid--3',
  'card-grid-3': 'grid grid--3', g3: 'grid grid--3', grid3: 'grid grid--3', g4: 'grid grid--3',
  card: 'card', 'gv-card': 'card', 'toc-card': 'card', metric: 'card', 'layer-row': 'card', 'method-item': 'card',
  flow: 'flow', 'dia-pipeline': 'flow', 'inh-tree': 'flow',
  node: 'flow-node', 'flow-box': 'flow-node', 'dia-box': 'flow-node', 'tree-box': 'flow-node',
  arrow: 'flow-arrow', 'flow-arrow': 'flow-arrow', 'dia-arrow': 'flow-arrow',
  chips: 'chips', 'complexity-badges': 'chips', 'tag-row': 'chips', 'complexity-row': 'chips',
  chip: 'chip', 'related-chip': 'chip', method: 'chip', 'badge-time': 'chip', 'badge-space': 'chip',
  'badge-green': 'chip', 'badge-red': 'chip', 'c-badge': 'chip',
  'step-row': 'step', 'sc-row': 'step', 'step-num': 'step-num', 'step-body': 'step-body',
  'step-title': 'step-title', 'step-desc': 'step-desc', 'sc-desc': 'step-desc',
  'estimate-row': 'kv',
  subtitle: 'lead', 'page-subtitle': 'lead', psub: 'lead', lead: 'lead',
  'math-formula': 'formula', 'math-block': 'formula',
  bitviz: 'bits', bitcell: 'bit',
  'gantt-chart': 'gantt', 'gantt-block': 'gantt-block', 'gantt-scale': 'gantt-scale',
  hl: 'callout callout--note', tn: 'chip', fb: 'flow-node', fa: 'flow-arrow',
  'matrix-grid': 'grid grid--3', 'matrix-cell': 'card',
  'dia-sub': 'muted', 'metric-lbl': 'muted', 'cell-desc': 'muted',
  // Sheet 150 problem sections
  'io-grid': 'grid', 'io-label': 'callout-label', 'io-example': 'card', 'io-example-label': 'callout-label',
  'io-in': 'mono', 'io-out': 'mono', 'io-comment': 'muted',
  'expected-box': 'callout callout--example', 'expected-box-label': 'callout-label',
}

/** Elements removed entirely (page chrome duplicated by the app). */
const REMOVE_SELECTORS = [
  'script', 'style', 'link', 'meta', 'noscript', 'button',
  '.topic-nav-bar', '.eyebrow', '.pagetitle', '.page-title', '.ptitle', '.ptag', '.page-tag',
  '.copy-btn', '.lang-tabs', '.code-header',
]

/** Inline style properties allowed through (layout only; colors come from the theme). */
const STYLE_ALLOW = new Set([
  'display', 'flex', 'flex-direction', 'flex-wrap', 'flex-grow', 'flex-shrink', 'flex-basis',
  'grid-template-columns', 'grid-column', 'gap', 'width', 'min-width', 'max-width',
  'align-items', 'justify-content', 'text-align', 'white-space',
])

const LANG_ALIASES = {
  python: 'py', py: 'py', 'python 3': 'py', cpp: 'cpp', 'c++': 'cpp', java: 'java',
  javascript: 'js', js: 'js', sql: 'sql', bash: 'bash', shell: 'bash', json: 'json', go: 'go',
}

export function normalizeLang(raw = '') {
  const key = raw.toLowerCase().replace(/implementation|code|solution/g, '').trim()
  return LANG_ALIASES[key] ?? (Object.entries(LANG_ALIASES).find(([k]) => key.startsWith(k))?.[1] ?? '')
}

function filterStyle(style) {
  return style
    .split(';')
    .map((d) => d.trim())
    .filter((d) => {
      const [prop, ...rest] = d.split(':')
      if (!prop || !rest.length) return false
      const value = rest.join(':')
      return STYLE_ALLOW.has(prop.trim().toLowerCase()) && !/var\(|#|rgb|hsl/i.test(value)
    })
    .join('; ')
}

/** Text of a <pre>/<code>-ish element, turning <br> into newlines. */
export function codeText(el) {
  for (const br of el.querySelectorAll('br')) br.replaceWith('\n')
  return el.textContent.replace(/ /g, ' ').replace(/^\n+|\s+$/g, '')
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

/**
 * Convert tab widgets (`tab('page','id',this)` / `polyTab('id',this)`)
 * into <div class="tabs"><div class="tab-panel" data-label>…</div></div>.
 */
function convertTabs(root, doc) {
  const buttons = [...root.querySelectorAll('[onclick*="tab("], [onclick*="Tab("]')]
  const groups = new Map()
  for (const btn of buttons) {
    const m = btn.getAttribute('onclick').match(/(?:^|\W)(tab|polyTab)\(\s*'([^']+)'(?:\s*,\s*'([^']+)')?/)
    if (!m) continue
    const panelId = m[1] === 'polyTab' ? `poly-${m[2]}` : `${m[2]}-${m[3]}`
    const bar = btn.parentElement
    if (!groups.has(bar)) groups.set(bar, [])
    groups.get(bar).push({ label: btn.textContent.trim(), panelId })
  }
  for (const [bar, tabs] of groups) {
    const wrap = doc.createElement('div')
    wrap.setAttribute('class', 'tabs')
    for (const { label, panelId } of tabs) {
      const panel = root.querySelector(`[id="${panelId}"]`) ?? doc.getElementById(panelId)
      if (!panel) continue
      const p = doc.createElement('div')
      p.setAttribute('class', 'tab-panel')
      p.setAttribute('data-label', label)
      while (panel.firstChild) p.appendChild(panel.firstChild)
      panel.remove()
      wrap.appendChild(p)
    }
    bar.replaceWith(wrap)
  }
}

/** Q&A accordions → native <details class="qa">. */
function convertQA(root, doc) {
  for (const card of root.querySelectorAll('.qa-card')) {
    const q = card.querySelector('.qa-question')
    const a = card.querySelector('.qa-answer')
    if (!q || !a) continue
    const details = doc.createElement('details')
    details.setAttribute('class', 'qa')
    const summary = doc.createElement('summary')
    summary.textContent = q.textContent.trim()
    const body = doc.createElement('div')
    while (a.firstChild) body.appendChild(a.firstChild)
    details.append(summary, body)
    card.replaceWith(details)
  }
}

/** All code containers → <figure class="code" data-lang><figcaption/><pre><code/></pre></figure>. */
function convertCode(root, doc) {
  const make = (text, lang, caption) => {
    const fig = doc.createElement('figure')
    fig.setAttribute('class', 'code')
    if (lang) fig.setAttribute('data-lang', lang)
    if (caption) {
      const cap = doc.createElement('figcaption')
      cap.textContent = caption
      fig.appendChild(cap)
    }
    const pre = doc.createElement('pre')
    pre.innerHTML = `<code>${escapeHtml(text)}</code>`
    fig.appendChild(pre)
    return fig
  }
  for (const box of root.querySelectorAll('.code-block-container')) {
    const caption = box.querySelector('.code-lang')?.textContent.trim() ?? ''
    const pre = box.querySelector('pre')
    if (!pre) { box.remove(); continue }
    box.replaceWith(make(codeText(pre), normalizeLang(caption), caption.replace(/\s*implementation$/i, '')))
  }
  for (const box of root.querySelectorAll('.code, .code-block')) {
    if (box.closest('figure.code')) continue
    const inner = box.querySelector('pre') ?? box
    box.replaceWith(make(codeText(inner), '', ''))
  }
  for (const pre of root.querySelectorAll('pre')) {
    if (pre.closest('figure.code')) continue
    pre.replaceWith(make(codeText(pre), '', ''))
  }
}

/**
 * Normalize a content fragment in place and return its HTML.
 * @param {Element} root  element whose *children* are the content
 */
export function normalizeFragment(root, doc) {
  for (const sel of REMOVE_SELECTORS) for (const el of root.querySelectorAll(sel)) el.remove()

  convertTabs(root, doc)
  convertQA(root, doc)
  convertCode(root, doc)

  // Heading-like divs → real headings.
  for (const el of root.querySelectorAll('.section-title, .schema-table-title, div.sec')) {
    const h = doc.createElement('h3')
    h.innerHTML = el.innerHTML
    el.replaceWith(h)
  }
  for (const el of root.querySelectorAll('div.h4, span.h4, p.h4')) {
    const h = doc.createElement('h4')
    h.innerHTML = el.innerHTML
    el.replaceWith(h)
  }
  for (const el of root.querySelectorAll('.inline-code, .mono')) {
    const c = doc.createElement('code')
    c.textContent = el.textContent
    // Keep structural elements (table cells, list items…) and put the code inside them.
    if (['TD', 'TH', 'LI', 'P', 'DIV'].includes(el.tagName)) {
      el.removeAttribute('class')
      el.replaceChildren(c)
    } else {
      el.replaceWith(c)
    }
  }
  for (const row of root.querySelectorAll('.estimate-row')) {
    row.querySelector('.label')?.setAttribute('class', 'kv-key')
    row.querySelector('.value')?.setAttribute('class', 'kv-value')
  }

  // Tables scroll horizontally on small screens.
  for (const table of root.querySelectorAll('table')) {
    if (table.parentElement?.classList.contains('table-wrap')) continue
    const wrap = doc.createElement('div')
    wrap.setAttribute('class', 'table-wrap')
    table.replaceWith(wrap)
    wrap.appendChild(table)
  }

  for (const el of root.querySelectorAll('*')) {
    // Class mapping
    const cls = el.getAttribute('class')
    if (cls !== null) {
      const legacy = cls.split(/\s+/).filter(Boolean)
      const keep = new Set()
      for (const c of legacy) {
        if (c === 'ti' || c.startsWith('ti-')) keep.add(c)
        else if (CLASS_MAP[c]) CLASS_MAP[c].split(' ').forEach((x) => keep.add(x))
        else if (['kv-key', 'kv-value', 'tabs', 'tab-panel', 'qa', 'code', 'table-wrap', 'callout', 'callout-label'].includes(c)) keep.add(c)
      }
      if (el.tagName === 'FIGURE' && legacy.includes('code')) keep.clear(), keep.add('code')
      if (keep.size) el.setAttribute('class', [...keep].join(' '))
      else el.removeAttribute('class')
    }
    // Attribute hygiene
    for (const attr of [...el.attributes]) {
      const name = attr.name.toLowerCase()
      // ids are meaningless in the app — except inside SVG drawings, where markers/gradients are referenced by url(#id).
      if (name.startsWith('on') || (name === 'id' && !el.closest('svg')) || name === 'tabindex' || name.startsWith('aria-') && name !== 'aria-label') {
        el.removeAttribute(attr.name)
      } else if (name === 'style') {
        const s = filterStyle(attr.value)
        s ? el.setAttribute('style', s) : el.removeAttribute('style')
      } else if (name === 'href') {
        const v = attr.value.trim()
        if (/^(https?:|mailto:)/i.test(v)) {
          el.setAttribute('target', '_blank')
          el.setAttribute('rel', 'noopener noreferrer')
        } else {
          // Legacy intra-page links have no meaning in the new app → unwrap.
          const span = doc.createElement('span')
          while (el.firstChild) span.appendChild(el.firstChild)
          el.replaceWith(span)
          break
        }
      }
    }
  }

  // Markdown images pasted with inline base64 data render as walls of text — drop them.
  for (const el of root.querySelectorAll('p, div, span, li')) {
    if (!el.children.length && /!\[[^\]]*\]\(data:image\//.test(el.textContent)) el.textContent = el.textContent.replace(/!\[[^\]]*\]\(data:image\/[^)]*\)/g, '')
  }

  // Remove empty wrappers left behind — but not empty cells of a grid (e.g. the corner of a
  // confusion matrix): removing one would shift every following cell into the wrong column.
  for (const el of [...root.querySelectorAll('div, span, p')].reverse()) {
    if (el.parentElement?.classList.contains('grid')) continue
    if (!el.textContent.trim() && !el.querySelector('i, img, svg, br, hr, code')) el.remove()
  }

  // Collapse markup whitespace, but never inside <pre> (code indentation).
  return root.innerHTML
    .replace(/<!--[\s\S]*?-->/g, '')
    .split(/(<pre[\s\S]*?<\/pre>)/)
    .map((part) => (part.startsWith('<pre') ? part : markdownBold(part.replace(/\s*\n\s*/g, '\n').replace(/[ \t]{2,}/g, ' '))))
    .join('')
    .trim()
}

/** Some legacy text contains literal **bold** markdown; render it (never inside <code>). */
function markdownBold(html) {
  return html
    .split(/(<code[\s\S]*?<\/code>)/)
    .map((p) => (p.startsWith('<code') ? p : p.replace(/\*\*(\S(?:[^*<]*?\S)?)\*\*/g, '<strong>$1</strong>')))
    .join('')
}

/**
 * Wrap every titled section of a topic in <section class="block">:
 *  - a plain <div> whose first child is an <h3> becomes the block itself
 *  - top-level <h3>s start a block that runs until the next heading/block
 * Content before the first heading (intro/lead) stays outside.
 */
export function sectionize(html, parseHTML) {
  const { document: doc } = parseHTML(`<div id="root">${html}</div>`)
  const root = doc.getElementById('root')
  for (const div of root.querySelectorAll('div')) {
    if (!div.getAttribute('class') && div.firstElementChild?.tagName === 'H3' && !div.parentElement.closest('.block')) {
      const section = doc.createElement('section')
      section.setAttribute('class', 'block')
      while (div.firstChild) section.appendChild(div.firstChild)
      div.replaceWith(section)
    }
  }
  // Topics without top-level <h3> sections use <h4> as their section headings.
  const top = [...root.children]
  const level = top.some((n) => n.tagName === 'H3' || n.getAttribute?.('class') === 'block') ? 'H3' : 'H4'
  let current = null
  for (const node of [...root.childNodes]) {
    const isHeading = node.tagName === level
    const isBlock = node.tagName === 'SECTION' && node.getAttribute('class') === 'block'
    if (isHeading) {
      current = doc.createElement('section')
      current.setAttribute('class', 'block')
      node.replaceWith(current)
      current.appendChild(node)
    } else if (isBlock) {
      current = null
    } else if (current) {
      current.appendChild(node)
    }
  }
  return root.innerHTML
}

/** Collapse whitespace in a text node. */
export function cleanText(s = '') {
  return s.replace(/\s+/g, ' ').trim()
}
