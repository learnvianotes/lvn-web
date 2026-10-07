import { z } from 'zod'

/**
 * Shape of content-build/catalog.json — the output of the content pipeline (scripts/content/extract.mjs).
 * Parsed with Zod at build time so a malformed export fails the build, not a reader's page.
 */

const difficulty = z.enum(['Easy', 'Medium', 'Hard'])

export const topicOutline = z.object({
  id: z.string(),
  title: z.string(),
  group: z.string().default(''),
  headings: z.array(z.string()).default([]),
  problems: z.array(z.object({ id: z.string(), lc: z.number(), title: z.string(), difficulty })).optional(),
})

export const subject = z.object({
  id: z.string(),
  category: z.string(),
  title: z.string(),
  icon: z.string(),
  kind: z.enum(['notes', 'problems']),
  description: z.string(),
  order: z.number(),
  itemCount: z.number(),
  topics: z.array(topicOutline),
})

export const catalog = z.object({
  version: z.number(),
  generatedAt: z.string(),
  categories: z.array(z.object({ id: z.string(), title: z.string() })),
  subjects: z.array(subject),
})

export type Catalog = z.infer<typeof catalog>
export type Subject = z.infer<typeof subject>
export type TopicOutline = z.infer<typeof topicOutline>
