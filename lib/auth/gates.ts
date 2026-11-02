/**
 * Names the public `unverifiedGatedActions` list uses by default (contracts 0.74.0).
 * The query is `[String!]!`. An admin can add other dotted names; those stay generic.
 */
export const DEFAULT_GATED_ACTIONS = ['note.publish', 'note.share', 'contest.enter', 'payout.request', 'ai.bulk', 'resource.submit'] as const

const KNOWN = new Set<string>(DEFAULT_GATED_ACTIONS)

export function isKnownGatedAction(action: string): boolean {
  return KNOWN.has(action)
}

type GateViewer = {
  emailVerified?: boolean | null
  globalRole?: string | null
  viewerNeedsVerification?: boolean | null
} | null | undefined

/**
 * Hide verify prompts when `viewerNeedsVerification` is false.
 * When that field is missing or null, a platform admin is the fallback.
 */
export function skipsVerificationPrompt(viewer: GateViewer): boolean {
  if (!viewer) return false
  if (typeof viewer.viewerNeedsVerification === 'boolean') return !viewer.viewerNeedsVerification
  return viewer.globalRole === 'PLATFORM_ADMIN'
}

/**
 * The public gate list applies only while this person still needs to verify and the sign-in email is unconfirmed.
 * A missing email flag is not treated as unverified.
 */
export function holdsVerification(viewer: GateViewer): boolean {
  if (!viewer || skipsVerificationPrompt(viewer)) return false
  return viewer.emailVerified === false
}

/** True when this viewer is held and the public list includes the action name. */
export function isGated(viewer: GateViewer, actions: readonly string[] | null | undefined, action: string): boolean {
  if (!holdsVerification(viewer)) return false
  return !!actions?.includes(action)
}

/** Public visibility follows public_notes_require_verification. Other visibility changes are not a gate. */
export function publicVisibilityHeld(viewer: GateViewer, publicNotesRequireVerification: boolean | null | undefined): boolean {
  return !!publicNotesRequireVerification && holdsVerification(viewer)
}
