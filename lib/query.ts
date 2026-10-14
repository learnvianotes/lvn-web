import { CombinedGraphQLErrors } from '@apollo/client/errors'

/** The API's answers that mean "not there for you" (lvn-backend libs/graphql errors.ts): no such id, a malformed one, not allowed. */
const NOT_THERE = new Set(['NOT_FOUND', 'FORBIDDEN', 'VALIDATION'])

/**
 * Whether a failed query was the API saying the thing is not there for this person, which a page shows as not found;
 * anything else (no connection, a server error) is a failure to load, shown with a way to try again.
 */
export const isNotThere = (error: unknown) => CombinedGraphQLErrors.is(error) && error.errors.some((e) => NOT_THERE.has(String(e.extensions?.code)))
