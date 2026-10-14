import { CombinedGraphQLErrors, ServerError } from '@apollo/client/errors'
import { describe, expect, it } from 'vitest'
import { isNotThere } from '@/lib/query'

const answered = (code: string) => new CombinedGraphQLErrors({ data: null, errors: [{ message: 'x', extensions: { code } }] })

describe('isNotThere: "not found" only when the API said so', () => {
  it('is the API saying no such thing, a malformed id, or not for this person', () => {
    for (const code of ['NOT_FOUND', 'FORBIDDEN', 'VALIDATION']) expect(isNotThere(answered(code)), code).toBe(true)
  })

  it('is not a failure to ask: no connection, a server error, an unexpected answer', () => {
    expect(isNotThere(answered('INTERNAL'))).toBe(false)
    expect(isNotThere(answered('UNAVAILABLE'))).toBe(false)
    expect(isNotThere(new CombinedGraphQLErrors({ data: null, errors: [{ message: 'no code' }] }))).toBe(false)
    expect(isNotThere(new ServerError('Response not successful: Received status code 500', { response: new Response(null, { status: 500 }), bodyText: '' }))).toBe(false)
    expect(isNotThere(new TypeError('Failed to fetch'))).toBe(false)
    expect(isNotThere(undefined)).toBe(false)
  })
})
