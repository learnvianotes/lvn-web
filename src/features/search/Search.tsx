/* ============================================================
   Search — finds subjects, topics (incl. their headings) and
   problems in the catalog. Press "/" or ⌘K to focus.
   ============================================================ */

import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search as SearchIcon, X } from 'lucide-react'
import { useCatalog } from '@/features/catalog/hooks'
import type { Catalog } from '@/features/catalog/types'
import { track } from '@/features/telemetry/track'

interface Entry {
  kind: 'Subject' | 'Topic' | 'Problem'
  title: string
  context: string
  to: string
  title_lc: string
  text: string
}

function buildIndex(catalog: Catalog): Entry[] {
  const out: Entry[] = []
  const add = (e: Omit<Entry, 'title_lc' | 'text'>, extra = '') =>
    out.push({ ...e, title_lc: e.title.toLowerCase(), text: `${e.title} ${e.context} ${extra}`.toLowerCase() })

  for (const s of catalog.subjects) {
    add({ kind: 'Subject', title: s.title, context: s.description, to: `/${s.id}` })
    for (const t of s.topics) {
      add({ kind: 'Topic', title: t.title, context: s.title, to: `/${s.id}/${t.id}` }, `${t.group} ${(t.headings ?? []).join(' ')} ${t.keywords ?? ''}`)
      for (const p of t.problems ?? []) {
        add({ kind: 'Problem', title: p.title, context: `LC ${p.lc} · ${t.title}`, to: `/${s.id}/${t.id}#${p.id}` }, `${p.lc} ${p.difficulty}`)
      }
    }
  }
  return out
}

function search(index: Entry[], q: string): Entry[] {
  const terms = q.toLowerCase().split(/\s+/).filter(Boolean)
  if (!terms.length) return []
  const rank = (e: Entry) =>
    e.title_lc.startsWith(terms[0]) ? 0 : terms.every((t) => e.title_lc.includes(t)) ? 1 : 2
  return index
    .filter((e) => terms.every((t) => e.text.includes(t)))
    .sort((a, b) => rank(a) - rank(b))
    .slice(0, 12)
}

export function Search() {
  const { data: catalog } = useCatalog()
  const index = useMemo(() => (catalog ? buildIndex(catalog) : []), [catalog])
  const [query, setQuery] = useState('')
  const [open, setOpen] = useState(false) // results visible
  const [expanded, setExpanded] = useState(false) // mobile: input shown
  const [active, setActive] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const rootRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const results = useMemo(() => search(index, query), [index, query])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const typing = e.target instanceof HTMLElement && e.target.closest('input, textarea, [contenteditable]')
      if ((e.key === '/' && !typing) || (e.key === 'k' && (e.metaKey || e.ctrlKey))) {
        e.preventDefault()
        setExpanded(true)
        requestAnimationFrame(() => inputRef.current?.focus())
      }
    }
    const onClick = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) { setOpen(false); setExpanded(false) }
    }
    window.addEventListener('keydown', onKey)
    document.addEventListener('mousedown', onClick)
    return () => { window.removeEventListener('keydown', onKey); document.removeEventListener('mousedown', onClick) }
  }, [])

  const go = (e: Entry) => {
    track('search', { l: query.trim(), i: e.to, v: results.length })
    navigate(e.to)
    setQuery('')
    setOpen(false)
    setExpanded(false)
    inputRef.current?.blur()
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') { e.preventDefault(); setActive((i) => Math.min(i + 1, results.length - 1)) }
    else if (e.key === 'ArrowUp') { e.preventDefault(); setActive((i) => Math.max(i - 1, 0)) }
    else if (e.key === 'Enter' && results[active]) go(results[active])
    else if (e.key === 'Escape') { setOpen(false); setExpanded(false); inputRef.current?.blur() }
  }

  return (
    <div className={`search ${expanded ? 'is-expanded' : ''}`} ref={rootRef}>
      <button
        className="icon-btn search-toggle"
        aria-label="Search"
        onClick={() => { setExpanded(true); requestAnimationFrame(() => inputRef.current?.focus()) }}
      >
        <SearchIcon size={18} />
      </button>
      <div className="search-field">
        <SearchIcon size={16} className="search-icon" aria-hidden />
        <input
          ref={inputRef}
          type="search"
          placeholder="Search topics, problems…"
          aria-label="Search topics and problems"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setOpen(true); setActive(0) }}
          onFocus={() => setOpen(true)}
          onKeyDown={onKeyDown}
          role="combobox"
          aria-expanded={open && results.length > 0}
          aria-controls="search-results"
        />
        {query ? (
          <button className="search-clear" aria-label="Clear search" onClick={() => { setQuery(''); inputRef.current?.focus() }}>
            <X size={14} />
          </button>
        ) : (
          <kbd className="search-kbd">/</kbd>
        )}
        <button className="search-cancel" onClick={() => { setQuery(''); setOpen(false); setExpanded(false) }}>
          Cancel
        </button>
      </div>
      {open && query.trim() && (
        <ul className="search-results" id="search-results" role="listbox">
          {results.length === 0 && <li className="search-empty">No matches for “{query}”</li>}
          {results.map((r, i) => (
            <li key={r.kind + r.to} role="option" aria-selected={i === active}>
              <button
                className={`search-result ${i === active ? 'is-active' : ''}`}
                onMouseEnter={() => setActive(i)}
                onClick={() => go(r)}
              >
                <span className="search-kind">{r.kind}</span>
                <span className="search-title">{r.title}</span>
                <span className="search-context">{r.context}</span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
