import { describe, expect, it } from 'vitest'
import { markdownText, parseInline, parseMarkdown } from '@/lib/markdown'

describe('Markdown for AI results', () => {
  it('reads a summary: a paragraph, then key points', () => {
    expect(parseMarkdown('Binary search halves the range.\n\n- Sorted input\n- O(log n) steps')).toEqual([
      { kind: 'paragraph', content: [{ kind: 'text', text: 'Binary search halves the range.' }] },
      { kind: 'list', ordered: false, start: 1, items: [[{ kind: 'paragraph', content: [{ kind: 'text', text: 'Sorted input' }] }], [{ kind: 'paragraph', content: [{ kind: 'text', text: 'O(log n) steps' }] }]] },
    ])
  })

  it('keeps an indented answer inside its numbered question (PRACTICE_QUESTIONS)', () => {
    const blocks = parseMarkdown('1. What does it need?\n\n   *Answer:* Sorted input.\n\n2. How fast is it?\n\n   *Answer:* O(log n).')
    expect(blocks).toHaveLength(1)
    const list = blocks[0] as Extract<(typeof blocks)[number], { kind: 'list' }>
    expect(list.ordered).toBe(true)
    expect(list.items).toHaveLength(2)
    expect(list.items[0]).toEqual([
      { kind: 'paragraph', content: [{ kind: 'text', text: 'What does it need?' }] },
      { kind: 'paragraph', content: [{ kind: 'em', children: [{ kind: 'text', text: 'Answer:' }] }, { kind: 'text', text: ' Sorted input.' }] },
    ])
  })

  it('reads bold terms, italics and code, nested in bold', () => {
    expect(parseInline('**Heap** — a tree; see `push()` and *why*')).toEqual([
      { kind: 'strong', children: [{ kind: 'text', text: 'Heap' }] },
      { kind: 'text', text: ' — a tree; see ' },
      { kind: 'code', text: 'push()' },
      { kind: 'text', text: ' and ' },
      { kind: 'em', children: [{ kind: 'text', text: 'why' }] },
    ])
    expect(parseInline('**the `key` part**')).toEqual([{ kind: 'strong', children: [{ kind: 'text', text: 'the ' }, { kind: 'code', text: 'key' }, { kind: 'text', text: ' part' }] }])
  })

  it('leaves underscores inside words and lone stars alone', () => {
    expect(parseInline('snake_case_name and 2 * 3 * 4')).toEqual([{ kind: 'text', text: 'snake_case_name and 2 * 3 * 4' }])
  })

  it('reads headings, nested lists and fenced code', () => {
    const blocks = parseMarkdown('## Heaps\n\n- Min heap\n  - smallest on top\n\n```js\nconst a = <b>\n```')
    expect(blocks[0]).toEqual({ kind: 'heading', level: 2, content: [{ kind: 'text', text: 'Heaps' }] })
    expect(blocks[1]).toMatchObject({ kind: 'list', items: [[{ kind: 'paragraph' }, { kind: 'list', items: [[{ kind: 'paragraph', content: [{ kind: 'text', text: 'smallest on top' }] }]] }]] })
    expect(blocks[2]).toEqual({ kind: 'code', text: 'const a = <b>' })
  })

  it('never turns text into markup', () => {
    expect(markdownText('<img src=x onerror=alert(1)> [link](javascript:alert(1))')).toBe('<img src=x onerror=alert(1)> [link](javascript:alert(1))')
  })
})
