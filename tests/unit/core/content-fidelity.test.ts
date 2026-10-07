import { readFileSync } from 'node:fs'
import path from 'node:path'
import { describe, expect, it } from 'vitest'
import { PROBLEM_RICH_FIELDS } from '@core-schema/content'
import { legacyCatalog, legacyProblems, legacyTopic } from '@core-server/content'
import { compareContent } from '../../support/fidelity'

/**
 * Every page of /core must read exactly as on the old site: each HTML fragment in content-build/,
 * converted to structured content and rendered by the old app's own ContentView, has to reproduce
 * the source HTML (the check the old seeder ran before every Firestore write).
 */

const read = <T>(...parts: string[]) => JSON.parse(readFileSync(path.join('content-build', ...parts), 'utf8')) as T

type SourceProblem = Record<string, unknown> & { id: string; naive?: { html: string }; optimal?: { html: string }; extra?: { html: string }[] }

describe.each(legacyCatalog().subjects.map((s) => [s.id, s] as const))('%s', (_id, subject) => {
  it('renders every fragment exactly like the source HTML', () => {
    const diffs: string[] = []
    const check = (where: string, html: string, content: Parameters<typeof compareContent>[1]) => {
      const diff = compareContent(html, content)
      if (diff) diffs.push(`${where}: ${diff}`)
    }
    for (const t of subject.topics) {
      if (subject.kind === 'notes') {
        const src = read<{ html: string }>('topics', subject.id, `${t.id}.json`)
        check(`${subject.id}/${t.id}`, src.html, legacyTopic(subject.id, t.id)!.content)
        continue
      }
      const sources = new Map(read<{ problems: SourceProblem[] }>('problems', `${t.id}.json`).problems.map((p) => [p.id, p]))
      for (const p of legacyProblems(subject.id, t.id)!) {
        const src = sources.get(p.id)!
        for (const f of PROBLEM_RICH_FIELDS) if (src[f]) check(`${p.id}.${f}`, src[f] as string, p[f]!)
        if (src.naive?.html) check(`${p.id}.naive`, src.naive.html, p.naive!.content)
        if (src.optimal?.html) check(`${p.id}.optimal`, src.optimal.html, p.optimal!.content)
        src.extra?.forEach((x, i) => check(`${p.id}.extra[${i}]`, x.html, p.extra![i]!.content))
      }
    }
    expect(diffs.slice(0, 5)).toEqual([])
  })
})
