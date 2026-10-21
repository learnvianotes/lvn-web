import { describe, expect, it } from 'vitest'

/** Search engines see only public pages: the signed-in app and the sign-in pages say noindex in every environment. */
describe('indexing', () => {
  it('keeps signed-in and sign-in pages out of search engines', async () => {
    for (const layout of [await import('@/app/(site)/(app)/layout'), await import('@/app/(site)/(auth)/layout')]) {
      expect(layout.metadata.robots).toEqual({ index: false, follow: false })
    }
  })
})
