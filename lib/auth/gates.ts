/** Actions the public `unverifiedGatedActions` query can name. Matches UnverifiedGatedAction. */
export const GATED_ACTIONS = [
  'PUBLISH_NOTE',
  'SHARE_NOTE',
  'COMMENT',
  'FOLLOW',
  'JOIN_GROUP',
  'JOIN_CLASS',
  'ASK_AI',
  'POST',
  'UPLOAD',
  'REACT',
] as const

export type GatedActionName = (typeof GATED_ACTIONS)[number]

type GateViewer = { emailVerified?: boolean | null; globalRole?: string | null } | null | undefined

/**
 * The public gate list applies only while the sign-in email is unconfirmed.
 * Platform admins are never held back, and a missing flag is not treated as unverified.
 */
export function holdsVerification(viewer: GateViewer): boolean {
  if (!viewer || viewer.globalRole === 'PLATFORM_ADMIN') return false
  return viewer.emailVerified === false
}

/** True when this viewer is held and the public list includes the action. */
export function isGated(viewer: GateViewer, actions: readonly string[] | null | undefined, action: string): boolean {
  if (!holdsVerification(viewer)) return false
  return !!actions?.includes(action)
}
