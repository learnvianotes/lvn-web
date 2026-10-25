/**
 * An account the API will not sign in (lvn-backend PR #27).
 * `AGE_RESTRICTED` is the age gate. A blocked sign-in carries `supportEmail` on the user error.
 */

export type AgeHold = { supportEmail: string; kind: 'age' | 'blocked' }

type Problem = { code: string; message?: string; supportEmail?: string | null }

export function ageHoldFromProblems(problems: Problem[] | null | undefined): AgeHold | null {
  const age = problems?.find((problem) => problem.code === 'AGE_RESTRICTED')
  if (age) return { supportEmail: age.supportEmail?.trim() ?? '', kind: 'age' }
  const blocked = problems?.find((problem) => problem.supportEmail?.trim())
  if (!blocked?.supportEmail) return null
  return { supportEmail: blocked.supportEmail.trim(), kind: 'blocked' }
}
