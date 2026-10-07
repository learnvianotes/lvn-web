import { describe, expect, it } from 'vitest'
import { flatten, unflatten, type Content } from '@core-schema/content'
import { ConvertError, htmlToContent } from '@core-server/fromHtml'
import { compareContent } from '../../support/fidelity'

describe('htmlToContent', () => {
  it('turns a paragraph with inline formatting into nodes', () => {
    const content = htmlToContent('<p>Use <strong>sets</strong> for <code>in</code> checks.</p>', 'test')
    expect(content).toHaveLength(1)
    expect(content[0]!.type).toBe('paragraph')
    expect(content[0]!.children!.map((n) => n.type)).toEqual(['text', 'strong', 'text', 'code', 'text'])
  })

  it('refuses elements it does not know, so nothing is dropped silently', () => {
    expect(() => htmlToContent('<marquee>hi</marquee>', 'test')).toThrow(ConvertError)
  })

  it('refuses unexpected attributes', () => {
    expect(() => htmlToContent('<p onclick="x()">hi</p>', 'test')).toThrow(ConvertError)
  })

  it('round-trips through the flat encoding the old site stored', () => {
    const content = htmlToContent('<ul><li>one</li><li>two <em>three</em></li></ul>', 'test')
    expect(unflatten(flatten(content))).toEqual(content)
  })
})

describe('fidelity check', () => {
  const html = '<p>Use <strong>sets</strong> for fast lookups.</p>'

  it('accepts content that renders exactly like its source', () => {
    expect(compareContent(html, htmlToContent(html, 'test'))).toBeNull()
  })

  it('reports content that renders differently', () => {
    const content: Content = structuredClone(htmlToContent(html, 'test'))
    content[0]!.children![2]!.value = ' for slow lookups.'
    expect(compareContent(html, content)).toMatch(/first difference/)
  })
})
