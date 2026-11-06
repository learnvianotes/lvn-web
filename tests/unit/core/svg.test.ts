import { describe, expect, it } from 'vitest'
import { sanitizeSvgMarkup } from '@core/features/content/svg'

const drawing = `<defs><marker id="rag-arrow" viewBox="0 0 10 10"><path d="M 0 1 L 10 5 L 0 9 z" /></marker></defs><path d="M 0 0 L 10 10" marker-end="url(#rag-arrow)" stroke="var(--red)" />`

describe('SVG drawings', () => {
  it('keeps a diagram and drops script, foreignObject, and scriptable URLs', () => {
    const html = sanitizeSvgMarkup(`${drawing}<script>alert(1)</script><a href="javascript:alert(1)">x</a><image xlink:href="javascript:alert(1)" /><foreignObject><iframe src="https://evil.example"></iframe></foreignObject><path stroke="url(https://evil.example/log)" />`)
    expect(html).toContain('url(#rag-arrow)')
    expect(html).toContain('var(--red)')
    expect(html.toLowerCase()).not.toContain('<script')
    expect(html.toLowerCase()).not.toContain('javascript:')
    expect(html.toLowerCase()).not.toContain('foreignobject')
    expect(html.toLowerCase()).not.toContain('iframe')
    expect(html).not.toContain('evil.example')
  })
})
