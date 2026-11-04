import { describe, expect, it, vi } from 'vitest'
import { createUsageTracker, type UsageSender } from '@/lib/analytics/usage'
import { featureOfPath, normalizeAppVersion, schemaProps, searchScopeOf, USAGE_FEATURES, wordCountOf } from '@/lib/analytics/usage-events'

const at = '2026-11-05T00:00:00.000Z'

function tracker(appVersion: string | null = '0.1.0') {
  const send = vi.fn<UsageSender>(async () => undefined)
  const t = createUsageTracker({ send, signedIn: () => true, now: () => at, appVersion })
  return { t, send, sent: () => send.mock.calls.flatMap((c) => c[0].events) }
}

describe('usage events v2 (lvn-backend ADR-0107)', () => {
  it('never sends free text: the new events keep only their fixed values', async () => {
    const { t, sent } = tracker()
    t.setPreference(false)
    t.track('search_no_results', { scope: 'notes', wordCount: 3, query: 'organic chemistry notes', words: 'organic chemistry notes' })
    t.track('feature_use', { feature: 'pdf_viewer', title: 'My private note', path: '/notes/123' })
    t.track('quiz_start', { kind: 'shared', name: 'Asha' })
    t.track('search', { scope: 'all', wordCount: 2, query: 'secret words' })
    await t.flush()
    const events = sent()
    expect(events.map((e) => e.props)).toEqual([{ scope: 'notes', wordCount: 3 }, { feature: 'pdf_viewer' }, { kind: 'shared' }, { scope: 'all', wordCount: 2 }])
    expect(JSON.stringify(events)).not.toMatch(/organic|private|Asha|secret|\/notes/)
  })

  it('drops an event the API would refuse, so the rest of the batch still goes', async () => {
    const { t, sent } = tracker()
    t.setPreference(false)
    t.track('feature_use', { feature: 'not_a_feature' })
    t.track('feature_use', {})
    t.track('quiz_start', { kind: 'exam' })
    t.track('search_no_results', { scope: 'notes' })
    t.track('search_no_results', { scope: 'web', wordCount: 1 })
    t.track('search_no_results', { scope: 'notes', wordCount: 1.5 })
    t.track('page_view')
    await t.flush()
    expect(sent().map((e) => e.name)).toEqual(['page_view'])
  })

  it('caps the word count and counts words without keeping them', () => {
    expect(wordCountOf('  one two   three ')).toBe(3)
    expect(wordCountOf('')).toBe(0)
    expect(wordCountOf(Array.from({ length: 50 }, (_, i) => `w${i}`).join(' '))).toBe(20)
    expect(schemaProps('search_no_results', { scope: 'all', wordCount: 99 })).toEqual({ scope: 'all', wordCount: 20 })
    expect(searchScopeOf(undefined)).toBe('all')
    expect(searchScopeOf(['NOTES'])).toBe('notes')
    expect(searchScopeOf(['NOTES', 'PEOPLE'])).toBe('all')
  })

  it('sends feature_use once per feature per page session, and quiz_start once per kind per page view', async () => {
    const { t, sent } = tracker()
    t.setPreference(false)
    t.feature('notes_editor')
    t.feature('notes_editor')
    t.feature('read_aloud')
    t.quizStart('note')
    t.quizStart('note')
    t.track('page_view')
    t.feature('notes_editor')
    t.quizStart('note')
    t.quizStart('practice')
    await t.flush()
    expect(sent().map((e) => `${e.name}:${Object.values(e.props ?? {}).join()}`)).toEqual([
      'feature_use:notes_editor',
      'feature_use:read_aloud',
      'quiz_start:note',
      'page_view:',
      'quiz_start:note',
      'quiz_start:practice',
    ])
  })

  it('respects the opt-out for the new events too', async () => {
    const { t, send } = tracker()
    t.setPreference(true)
    t.feature('groups')
    t.quizStart('class')
    t.searchNoResults('people', 2)
    await t.flush()
    expect(send).not.toHaveBeenCalled()
    expect(t.pending().usage).toBe(0)
  })

  it('drops what was held when the person turns out to have opted out', async () => {
    const { t, send } = tracker()
    t.feature('groups')
    t.searchNoResults('people', 2)
    t.setPreference(true)
    await t.flush()
    expect(send).not.toHaveBeenCalled()
  })

  it('puts the same valid build version on every event, and none when it is not a version', async () => {
    const withVersion = tracker('0.1.0')
    withVersion.t.setPreference(false)
    withVersion.t.track('page_view')
    withVersion.t.feature('search')
    await withVersion.t.flush()
    expect(withVersion.sent().map((e) => e.appVersion)).toEqual(['0.1.0', '0.1.0'])

    const without = tracker(null)
    without.t.setPreference(false)
    without.t.track('page_view')
    await without.t.flush()
    expect(without.sent()[0]).not.toHaveProperty('appVersion')

    expect(normalizeAppVersion('v1.4.2')).toBe('1.4.2')
    expect(normalizeAppVersion('1.4.2-beta.1+abc123')).toBe('1.4.2-beta.1+abc123')
    expect(normalizeAppVersion('web')).toBeNull()
    expect(normalizeAppVersion('1')).toBeNull()
    expect(normalizeAppVersion(`1.0.0-${'x'.repeat(40)}`)).toBeNull()
  })

  it('maps feature pages to their feature and leaves other pages alone', () => {
    expect(featureOfPath('/groups/abc/doubts/def')).toBe('doubts')
    expect(featureOfPath('/groups/abc')).toBe('groups')
    expect(featureOfPath('/classes/abc/quizzes/q1')).toBe('class_quiz')
    expect(featureOfPath('/classes')).toBe('classroom')
    expect(featureOfPath('/quiz/tok')).toBe('shared_quiz')
    expect(featureOfPath('/review')).toBe('flashcards_review')
    expect(featureOfPath('/exams/1')).toBe('exam_plan')
    expect(featureOfPath('/profile/notifications')).toBe('settings')
    expect(featureOfPath('/profile')).toBe('profile')
    expect(featureOfPath('/notes/abc')).toBeNull()
    expect(featureOfPath('/home')).toBeNull()
    for (const path of ['/groups', '/search', '/ask', '/resources']) expect(USAGE_FEATURES).toContain(featureOfPath(path))
  })
})
