import type { TopicOutline } from './schema'

/** Consecutive topics sharing a `group` (e.g. "Foundations"), in catalog order. */
export function groupTopics(topics: TopicOutline[]): { group: string; topics: TopicOutline[] }[] {
  const out: { group: string; topics: TopicOutline[] }[] = []
  for (const topic of topics) {
    const last = out.at(-1)
    if (last && last.group === topic.group) last.topics.push(topic)
    else out.push({ group: topic.group, topics: [topic] })
  }
  return out
}
