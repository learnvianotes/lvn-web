/* ============================================================
   CodeTabs — one solution in Python / C++ / Java / JavaScript.
   The chosen language is remembered across problems. Missing
   languages stay visible (disabled) so the gap is obvious.
   ============================================================ */

import { useEffect, useMemo, useState } from 'react'
import { Check, Copy } from 'lucide-react'
import type { CodeLang } from '@core/features/catalog/types'
import { highlight } from '@core/shared/lib/highlight'
import { get, set } from '@core/services/storage'

const LANGS: { id: CodeLang; label: string }[] = [
  { id: 'py', label: 'Python' },
  { id: 'cpp', label: 'C++' },
  { id: 'java', label: 'Java' },
  { id: 'js', label: 'JavaScript' },
]

// Shared across all CodeTabs on the page.
let preferred: CodeLang = get<CodeLang>('code-lang') ?? 'py'
const subscribers = new Set<(l: CodeLang) => void>()

export function CodeTabs({ code }: { code: Partial<Record<CodeLang, string>> }) {
  const [lang, setLang] = useState<CodeLang>(preferred)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    const sub = (l: CodeLang) => setLang(l)
    subscribers.add(sub)
    return () => { subscribers.delete(sub) }
  }, [])

  const available = LANGS.filter((l) => code[l.id])
  const active = code[lang] ? lang : available[0]?.id
  const html = useMemo(() => (active ? highlight(code[active]!, active) : ''), [code, active])

  if (!available.length) return null

  const choose = (l: CodeLang) => {
    preferred = l
    set('code-lang', l)
    subscribers.forEach((s) => s(l))
  }
  const copy = () => {
    void navigator.clipboard?.writeText(code[active!]!).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    })
  }

  return (
    <div className="code-tabs">
      <div className="code-tabs-bar" role="tablist">
        {LANGS.map((l) => (
          <button
            key={l.id}
            role="tab"
            aria-selected={l.id === active}
            disabled={!code[l.id]}
            title={code[l.id] ? undefined : `${l.label} solution not available yet`}
            onClick={() => choose(l.id)}
          >
            {l.label}
          </button>
        ))}
        <button className="code-copy" onClick={copy} aria-label="Copy code">
          {copied ? <Check size={14} /> : <Copy size={14} />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>
      {lang !== active && (
        <p className="code-note">{LANGS.find((l) => l.id === lang)?.label} isn’t available for this solution yet.</p>
      )}
      <pre><code className="hljs" dangerouslySetInnerHTML={{ __html: html }} /></pre>
    </div>
  )
}
