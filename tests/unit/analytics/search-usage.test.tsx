// @vitest-environment happy-dom
import { act } from 'react'
import { createRoot } from 'react-dom/client'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useSearch } from '@/features/search/useSearch'

;(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true

const state = vi.hoisted(() => ({ notes: [] as unknown[] }))
const analytics = vi.hoisted(() => ({ track: vi.fn(), noResults: vi.fn() }))

vi.mock('@apollo/client/react', () => ({
  useQuery: (_doc: unknown, options: { skip?: boolean }) =>
    options.skip
      ? { data: undefined, loading: false }
      : { data: { search: { notes: state.notes, people: [], topics: [], groups: [], classrooms: [], resources: [], notesCursor: null } }, loading: false, fetchMore: vi.fn(), refetch: vi.fn() },
}))
vi.mock('@/lib/learning', () => ({ track: vi.fn() }))
vi.mock('@/lib/analytics', async (orig) => ({ ...(await orig<typeof import('@/lib/analytics')>()), trackUsage: analytics.track, trackSearchNoResults: analytics.noResults }))

function Probe({ query, scopes }: { query: string; scopes?: ('NOTES' | 'PEOPLE')[] }) {
  useSearch(query, 10, {}, scopes)
  return null
}

describe('search usage events', () => {
  afterEach(() => {
    vi.useRealTimers()
    analytics.track.mockReset()
    analytics.noResults.mockReset()
  })

  async function search(query: string, scopes?: ('NOTES' | 'PEOPLE')[]) {
    vi.useFakeTimers()
    const root = createRoot(document.createElement('div'))
    await act(async () => root.render(<Probe query={query} scopes={scopes} />))
    await act(async () => vi.advanceTimersByTime(250))
    return root
  }

  it('reports a search that found nothing once, with its scope and word count only', async () => {
    state.notes = []
    const root = await search('  krebs cycle steps ', ['NOTES'])
    expect(analytics.track).toHaveBeenCalledWith('search', { scope: 'notes', wordCount: 3 })
    expect(analytics.noResults).toHaveBeenCalledTimes(1)
    expect(analytics.noResults).toHaveBeenCalledWith('notes', 3)
    expect(JSON.stringify([analytics.track.mock.calls, analytics.noResults.mock.calls])).not.toMatch(/krebs|cycle/)
    await act(async () => root.render(<Probe query="  krebs cycle steps " scopes={['NOTES']} />))
    expect(analytics.noResults).toHaveBeenCalledTimes(1)
    act(() => root.unmount())
  })

  it('says nothing more when something was found', async () => {
    state.notes = [{ id: 'n1' }]
    const root = await search('photosynthesis')
    expect(analytics.track).toHaveBeenCalledWith('search', { scope: 'all', wordCount: 1 })
    expect(analytics.noResults).not.toHaveBeenCalled()
    act(() => root.unmount())
  })
})
