/**
 * An account the API will not activate because of age (lvn-backend PR #27, still landing).
 * `AGE_RESTRICTED` is the sign-up failure. `AGE_BLOCKED` is the same account signing in later.
 * The support address is the email in that error's message until the schema names a field for it.
 */

const EMAIL = /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i

export type AgeHold = { supportEmail: string }

export function ageHoldFromProblems(problems: { code: string; message: string }[] | null | undefined): AgeHold | null {
  const hit = problems?.find((problem) => problem.code === 'AGE_RESTRICTED' || problem.code === 'AGE_BLOCKED')
  if (!hit) return null
  return { supportEmail: hit.message.match(EMAIL)?.[0] ?? '' }
}
