import { describe, expect, it } from 'vitest'
import { codeTabsHtml, escapeHtml, renderContent, slugify } from './render'

describe('renderContent', () => {
  it('highlights code by data-lang and leaves program output plain', () => {
    const { html } = renderContent(
      '<figure class="code" data-lang="py"><pre><code>def f(): return 1 &lt; 2</code></pre></figure>' +
        '<figure class="code" data-lang="text"><pre><code>&lt;b&gt;</code></pre></figure>',
    )
    expect(html).toContain('<span class="hljs-keyword">def</span>')
    expect(html).toContain('&lt;b&gt;')
    expect(html).not.toContain('<b>')
  })

  it('turns tab panels into an accessible tab set with only the first panel visible', () => {
    const { html } = renderContent(
      '<div class="tabs"><div class="tab-panel" data-label="Python">a</div><div class="tab-panel" data-label="Java">b</div></div>',
      'x',
    )
    expect(html).toContain('role="tablist"')
    const tag = (id: string) => html.match(new RegExp(`<[^>]*id="${id}"[^>]*>`))?.[0] ?? ''
    expect(tag('x-t0-0')).toContain('aria-selected="true"')
    expect(tag('x-t0-0-panel')).not.toContain('hidden')
    expect(tag('x-t0-1-panel')).toContain('hidden')
  })

  it('anchors section headings with unique ids', () => {
    const { headings } = renderContent(
      '<section class="block"><h3><i class="ti ti-bulb"></i>Big-O table</h3></section><section class="block"><h3>Big-O table</h3></section>',
    )
    expect(headings).toEqual([
      { id: 'big-o-table', text: 'Big-O table' },
      { id: 'big-o-table-2', text: 'Big-O table' },
    ])
  })

  it('marks outbound links nofollow', () => {
    expect(renderContent('<p><a href="https://example.com">x</a></p>').html).toContain('rel="noopener nofollow ugc"')
  })
})

describe('helpers', () => {
  it('escapes HTML and slugifies', () => {
    expect(escapeHtml(`<a href="x">'&'</a>`)).toBe('&lt;a href=&quot;x&quot;&gt;&#39;&amp;&#39;&lt;/a&gt;')
    expect(slugify('Loop pattern: nested & sequential')).toBe('loop-pattern-nested-sequential')
  })

  it('builds code tabs only for languages that have code', () => {
    const html = codeTabsHtml({ py: 'x = 1', cpp: '', java: 'int x;' })
    expect(html).toContain('data-label="Python"')
    expect(html).toContain('data-label="Java"')
    expect(html).not.toContain('C++')
  })
})
