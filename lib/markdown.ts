/**
 * The Markdown that AI results and Markdown cards use (lvn-backend ADR-0059), parsed to a tree React renders: headings,
 * paragraphs, bullet and numbered lists (nested by indenting), fenced code, **bold**, *italic* and `code`. Nothing in
 * it becomes HTML, so model output cannot inject markup; links stay as their words.
 */

export type MdInline = { kind: 'text' | 'code'; text: string } | { kind: 'strong' | 'em'; children: MdInline[] }
export type MdBlock =
  | { kind: 'heading'; level: 1 | 2 | 3; content: MdInline[] }
  | { kind: 'paragraph'; content: MdInline[] }
  | { kind: 'code'; text: string }
  | { kind: 'list'; ordered: boolean; start: number; items: MdBlock[][] }

const FENCE = /^\s*(```|~~~)/
const HEADING = /^(#{1,6})\s+(.*?)\s*#*\s*$/
const ITEM = /^ {0,3}([-*+]|(\d{1,9})[.)])\s+(.*)$/
const INDENT = /^( {2,}|\t)/

const isBlank = (line: string) => !line.trim()
const startsBlock = (line: string) => FENCE.test(line) || HEADING.test(line) || ITEM.test(line)

export function parseMarkdown(source: string): MdBlock[] {
  return blocks(source.replace(/\r\n?/g, '\n').split('\n'))
}

function blocks(lines: string[]): MdBlock[] {
  const out: MdBlock[] = []
  let para: string[] = []
  const flush = () => {
    if (para.length) out.push({ kind: 'paragraph', content: parseInline(para.join(' ').trim()) })
    para = []
  }
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!
    if (isBlank(line)) {
      flush()
      continue
    }
    if (FENCE.test(line)) {
      flush()
      const fence = line.trim().slice(0, 3)
      const code: string[] = []
      while (++i < lines.length && !lines[i]!.trim().startsWith(fence)) code.push(lines[i]!)
      out.push({ kind: 'code', text: code.join('\n') })
      continue
    }
    const heading = HEADING.exec(line)
    if (heading) {
      flush()
      out.push({ kind: 'heading', level: Math.min(heading[1]!.length, 3) as 1 | 2 | 3, content: parseInline(heading[2]!) })
      continue
    }
    const item = ITEM.exec(line)
    if (item) {
      flush()
      const ordered = item[2] !== undefined
      const list: Extract<MdBlock, { kind: 'list' }> = { kind: 'list', ordered, start: ordered ? Number(item[2]) : 1, items: [] }
      // Items of one kind in a row make one list; each item takes the indented (and lazily continued) lines after it.
      while (i < lines.length) {
        const m = ITEM.exec(lines[i]!)
        if (!m || (m[2] !== undefined) !== ordered) break
        const body = [m[3]!]
        let j = i + 1
        for (; j < lines.length; j++) {
          const next = lines[j]!
          if (INDENT.test(next)) body.push(next.replace(INDENT, ''))
          else if (isBlank(next) && j + 1 < lines.length && INDENT.test(lines[j + 1]!)) body.push('')
          else if (!isBlank(next) && !isBlank(lines[j - 1]!) && !startsBlock(next)) body.push(next)
          else break
        }
        list.items.push(blocks(body))
        i = j
        // A blank line between items keeps the list going.
        while (i < lines.length && isBlank(lines[i]!) && i + 1 < lines.length && ITEM.test(lines[i + 1]!)) i++
      }
      i--
      out.push(list)
      continue
    }
    para.push(line.trim())
  }
  flush()
  return out
}

const INLINE = /(`+)([\s\S]*?[^`])\1(?!`)|\*\*(?=\S)([\s\S]*?\S)\*\*|__(?=\S)([\s\S]*?\S)__|\*(?=[^\s*])([\s\S]*?[^\s*])\*|(?<![\p{L}\p{N}])_(?=[^\s_])([\s\S]*?[^\s_])_(?![\p{L}\p{N}])/u

export function parseInline(text: string): MdInline[] {
  const out: MdInline[] = []
  let rest = text
  while (rest) {
    const m = INLINE.exec(rest)
    if (!m) {
      out.push({ kind: 'text', text: rest })
      break
    }
    if (m.index) out.push({ kind: 'text', text: rest.slice(0, m.index) })
    if (m[1]) out.push({ kind: 'code', text: m[2]!.trim() || m[2]! })
    else if (m[3] !== undefined || m[4] !== undefined) out.push({ kind: 'strong', children: parseInline(m[3] ?? m[4]!) })
    else out.push({ kind: 'em', children: parseInline(m[5] ?? m[6]!) })
    rest = rest.slice(m.index + m[0].length)
  }
  return out
}

/** The words alone, for read aloud and for comparing in tests. */
export function markdownText(source: string): string {
  const inline = (xs: MdInline[]): string => xs.map((x) => ('text' in x ? x.text : inline(x.children))).join('')
  const block = (b: MdBlock): string => (b.kind === 'code' ? b.text : b.kind === 'list' ? b.items.map((i) => i.map(block).join('\n')).join('\n') : inline(b.content))
  return parseMarkdown(source).map(block).join('\n')
}
