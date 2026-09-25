/* ============================================================
   CodeBlock — Sheet 150
   Multi-language tabbed code viewer.
   Receives code as plain strings from Firebase — never
   hardcodes problem-specific content.
   Supported tabs: Python · C++ · Java · JavaScript
   ============================================================ */

import { useState } from 'react'
import { Copy, Check } from 'lucide-react'
import type { CodeLanguage } from '@/types/sheet150'

const LANGUAGE_LABELS: Record<CodeLanguage, string> = {
  py:   'Python',
  cpp:  'C++',
  java: 'Java',
  js:   'JavaScript',
}

// Ordered tab display
const LANGUAGE_ORDER: CodeLanguage[] = ['py', 'cpp', 'java', 'js']

interface CodeBlockProps {
  code: Partial<Record<CodeLanguage, string>>
}

export function CodeBlock({ code }: CodeBlockProps) {
  // Build list of available languages in preferred display order
  const available = LANGUAGE_ORDER.filter((lang) => code[lang])

  const [activeTab, setActiveTab] = useState<CodeLanguage>(available[0] ?? 'py')
  const [copied, setCopied] = useState(false)

  if (available.length === 0) return null

  const activeCode = code[activeTab] ?? ''

  function handleCopy() {
    navigator.clipboard.writeText(activeCode).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 1800)
    }).catch(() => {})
  }

  return (
    <div className="s150-codeblock">
      {/* Tab bar */}
      <div className="s150-codeblock__tabs" role="tablist" aria-label="Language">
        {available.map((lang) => (
          <button
            key={lang}
            role="tab"
            aria-selected={lang === activeTab}
            aria-controls={`code-panel-${lang}`}
            id={`code-tab-${lang}`}
            className={`s150-codeblock__tab ${lang === activeTab ? 's150-codeblock__tab--active' : ''}`}
            onClick={() => setActiveTab(lang)}
          >
            {LANGUAGE_LABELS[lang]}
          </button>
        ))}

        {/* Copy button — spacer pushes it to the right */}
        <div className="s150-codeblock__tab-spacer" aria-hidden="true" />
        <button
          className="s150-codeblock__copy-btn"
          onClick={handleCopy}
          aria-label="Copy code to clipboard"
          title="Copy code"
        >
          {copied ? (
            <>
              <Check size={13} aria-hidden="true" />
              <span>Copied</span>
            </>
          ) : (
            <>
              <Copy size={13} aria-hidden="true" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>

      {/* Code panel */}
      <div
        className="s150-codeblock__panel"
        role="tabpanel"
        id={`code-panel-${activeTab}`}
        aria-labelledby={`code-tab-${activeTab}`}
      >
        <pre className="s150-codeblock__pre">
          <code>{activeCode}</code>
        </pre>
      </div>
    </div>
  )
}
