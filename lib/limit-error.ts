import { CombinedGraphQLErrors } from '@apollo/client/errors'

/** Plan limits and the invite-only allowlist both come back as these codes, with a message written for a person. */
const REFUSAL = new Set(['RATE_LIMITED', 'FORBIDDEN'])

export function isLimitCode(code: string | null | undefined): boolean {
  return code === 'RATE_LIMITED' || code === 'FORBIDDEN'
}

export function limitMessageFromUserErrors(errors: readonly { code?: string | null; message: string }[] | null | undefined): string | null {
  return errors?.find((error) => isLimitCode(error.code))?.message ?? null
}

/** The message on a GraphQL error when the API refused for a plan limit or a similar guard, instead of a generic failure. */
export function refusalMessage(error: unknown): string | null {
  if (!CombinedGraphQLErrors.is(error)) return null
  const hit = error.errors.find((item) => REFUSAL.has(String(item.extensions?.code ?? '')))
  return hit?.message ?? null
}
