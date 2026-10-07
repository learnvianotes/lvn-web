import { z } from 'zod'

/**
 * Shape of content-build/ — the output of the content pipeline (scripts/content/extract.mjs).
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

export const topic = z.object({
  subjectId: z.string(),
  id: z.string(),
  title: z.string(),
  group: z.string().default(''),
  order: z.number(),
  html: z.string(),
})

const solution = z.object({
  title: z.string(),
  html: z.string(),
  code: z.record(z.string(), z.string()),
  complexity: z.array(z.string()).default([]),
})

export const problem = z.object({
  id: z.string(),
  lc: z.number(),
  title: z.string(),
  difficulty,
  leetcodeUrl: z.string(),
  youtubeUrl: z.string().default(''),
  statement: z.string(),
  understanding: z.string().default(''),
  naive: solution.optional(),
  intuition: z.string().default(''),
  approach: z.string().default(''),
  optimal: solution.optional(),
  takeaway: z.string().default(''),
  similar: z.array(z.object({ title: z.string(), difficulty: z.string(), lc: z.number().optional(), url: z.string() })).default([]),
  order: z.number(),
})

export const problemSet = z.object({ categoryId: z.string(), title: z.string(), problems: z.array(problem) })

export type Catalog = z.infer<typeof catalog>
export type Subject = z.infer<typeof subject>
export type TopicOutline = z.infer<typeof topicOutline>
export type Topic = z.infer<typeof topic>
export type Problem = z.infer<typeof problem>
export type ProblemSet = z.infer<typeof problemSet>
export type Solution = z.infer<typeof solution>
