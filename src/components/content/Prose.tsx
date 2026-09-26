/* ============================================================
   Prose — renders normalized content HTML (see
   scripts/content/sanitize.mjs for the vocabulary) and enhances
   it: code highlighting + copy buttons, and tab widgets.
   The HTML comes from our own extraction pipeline, never from users.
   ============================================================ */

import { useLayoutEffect, useRef } from 'react'
import { highlight } from '@/lib/highlight'

export function Prose({ html, className = '' }: { html: string; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)

  useLayoutEffect(() => {
    const root = ref.current
    if (!root) return
    enhanceCode(root)
    enhanceTabs(root)
  }, [html])

  return <div ref={ref} className={`prose ${className}`} dangerouslySetInnerHTML={{ __html: html }} />
}

function enhanceCode(root: HTMLElement) {
  for (const fig of root.querySelectorAll<HTMLElement>('figure.code:not([data-ready])')) {
    fig.dataset.ready = ''
    const code = fig.querySelector('code')
    if (!code) continue
    const text = code.textContent ?? ''
    code.innerHTML = highlight(text, fig.dataset.lang)
    code.classList.add('hljs')
    const btn = document.createElement('button')
    btn.className = 'copy-btn'
    btn.type = 'button'
    btn.textContent = 'Copy'
    btn.addEventListener('click', () => {
      void navigator.clipboard?.writeText(text).then(() => {
        btn.textContent = 'Copied'
        setTimeout(() => (btn.textContent = 'Copy'), 1500)
      })
    })
    fig.appendChild(btn)
  }
}

function enhanceTabs(root: HTMLElement) {
  for (const tabs of root.querySelectorAll<HTMLElement>('.tabs:not([data-ready])')) {
    tabs.dataset.ready = ''
    const panels = [...tabs.querySelectorAll<HTMLElement>(':scope > .tab-panel')]
    const bar = document.createElement('div')
    bar.className = 'tab-bar'
    bar.setAttribute('role', 'tablist')
    const select = (i: number) => {
      panels.forEach((p, j) => (p.hidden = i !== j))
      bar.querySelectorAll('button').forEach((b, j) => b.setAttribute('aria-selected', String(i === j)))
    }
    panels.forEach((p, i) => {
      const b = document.createElement('button')
      b.type = 'button'
      b.setAttribute('role', 'tab')
      b.textContent = p.dataset.label ?? `Tab ${i + 1}`
      b.addEventListener('click', () => select(i))
      bar.appendChild(b)
    })
    tabs.prepend(bar)
    select(0)
  }
}
