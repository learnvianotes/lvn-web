import { expect, it } from 'vitest'
import { groupTopics } from './group'

it('groups consecutive topics and keeps catalog order', () => {
  const t = (id: string, group: string) => ({ id, title: id, group, headings: [] })
  expect(groupTopics([t('a', 'X'), t('b', 'X'), t('c', 'Y'), t('d', 'X')]).map((g) => [g.group, g.topics.map((x) => x.id)])).toEqual([
    ['X', ['a', 'b']],
    ['Y', ['c']],
    ['X', ['d']],
  ])
})
