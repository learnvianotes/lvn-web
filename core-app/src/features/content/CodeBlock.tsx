/* A code block: syntax-highlighted, with a copy button (UI only → data-ui). */

import { useMemo, useState } from 'react'
import { highlight } from '@core/shared/lib/highlight'

interface Props {
  code: string
  lang?: string
  caption?: string
}

export function CodeBlock({ code, lang, caption }: Props) {
  const html = useMemo(() => highlight(code, lang), [code, lang])
  const [copied, setCopied] = useState(false)
  const copy = () => {
    void navigator.clipboard?.writeText(code).then(() => {
      setCopied(true)
      window.setTimeout(() => setCopied(false), 1500)
    })
  }
  return (
    <figure className="code" data-lang={lang}>
      {caption !== undefined && <figcaption>{caption}</figcaption>}
      <pre><code className="hljs" dangerouslySetInnerHTML={{ __html: html }} /></pre>
      <button type="button" className="copy-btn" data-ui onClick={copy}>{copied ? 'Copied' : 'Copy'}</button>
    </figure>
  )
}
