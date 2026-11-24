import { CombinedGraphQLErrors } from '@apollo/client/errors'

/** GraphQL codes whose message is written for the person signing in (invite-only, a bad token, a limit). */
const SHOWN = new Set(['FORBIDDEN', 'UNAUTHENTICATED', 'RATE_LIMITED'])

/**
 * The sentence to show when exchanging a Google token fails. The API's own message for a refusal or a token it
 * could not verify; anything else stays the generic sentence, so an internal error is not quoted on the form.
 */
export function googleSignInProblem(error: unknown, fallback: string): string {
  if (!CombinedGraphQLErrors.is(error)) return fallback
  const message = error.errors.find((item) => SHOWN.has(String(item.extensions?.code ?? '')))?.message.trim()
  return message || fallback
}
