import { safeNext } from '@/lib/auth/destination'
import { useSession } from '@/state/session'

/** Roles the API asks for a code before admin tools (MFA_ENFORCED_ROLES). Students and teachers are not among them. */
export const ADMIN_MFA_ROLES = ['PLATFORM_ADMIN', 'MANAGER'] as const

export function isAdminMfaRole(role: string | null | undefined): boolean {
  return role === 'PLATFORM_ADMIN' || role === 'MANAGER'
}

/** Where the email-code screen lives. It is not a settings section. */
export const ADMIN_VERIFY_PATH = '/admin/verify'

/**
 * Remembers whether this admin session still needs a code. A non-admin never gets the flag, even when the API
 * reports mfaRequired for an opt-in that has no screen yet.
 */
export function noteSessionMfa(role: string | null | undefined, mfaRequired: boolean): void {
  useSession.setState((state) => {
    const nextRole = role ?? state.role
    const pending = mfaRequired && isAdminMfaRole(nextRole)
    return { role: nextRole, mfaPending: pending, mfaVerified: pending ? false : state.mfaVerified }
  })
}

/** The code was accepted in this tab. Admin pages open even if an older status response arrives later. */
export function noteMfaVerified(role: string | null | undefined): void {
  useSession.setState((state) => ({ role: role ?? state.role, mfaPending: false, mfaVerified: true }))
}

/** The code screen, remembering the page to open once the code is accepted. */
export function adminVerifyPath(next: string): string {
  const safe = safeNext(next) ?? '/admin'
  if (safe === ADMIN_VERIFY_PATH || safe.startsWith(`${ADMIN_VERIFY_PATH}?`) || safe.startsWith(`${ADMIN_VERIFY_PATH}#`)) return safe
  return `${ADMIN_VERIFY_PATH}?next=${encodeURIComponent(safe)}`
}

export type MfaProblemKind = 'wrong' | 'expired' | 'locked' | 'used' | 'rate' | 'other'

/** Turns the API's VALIDATION and RATE_LIMITED messages into the sentence the code screen shows. */
export function classifyMfaProblem(message: string, code?: string | null): MfaProblemKind {
  if (code === 'RATE_LIMITED' || /too many codes/i.test(message)) return 'rate'
  const text = message.toLowerCase()
  if (text.includes('expired')) return 'expired'
  if (text.includes('too many attempts')) return 'locked'
  if (text.includes('already been used')) return 'used'
  if (text.includes('incorrect') || text.includes('not valid')) return 'wrong'
  return 'other'
}

export function retryAfterSeconds(retryAfter: number | null | undefined): number | null {
  if (typeof retryAfter !== 'number' || !Number.isFinite(retryAfter) || retryAfter <= 0) return null
  return Math.ceil(retryAfter)
}

const MFA_CODES = new Set(['ADMIN_MFA_REQUIRED', 'MFA_REQUIRED'])

/** True when an admin operation refused to run until a code is entered. */
export function isMfaRequiredError(error: unknown): boolean {
  return graphqlCodes(error).some((code) => MFA_CODES.has(code))
}

/** The running API does not know the MFA fields yet. Admin pages keep working; the server is not enforcing a code. */
export function isUnknownMfaField(error: unknown): boolean {
  const messages = graphqlMessages(error)
  return messages.some((message) => /Cannot query field ["'](mfaRequired|mfaFactors|mfaStatus|adminActivity|adminActivitySummary)["']/.test(message))
}

export function graphqlCodes(error: unknown): string[] {
  const record = error as { errors?: { extensions?: { code?: string } }[]; graphQLErrors?: { extensions?: { code?: string } }[] } | null
  const list = record?.errors ?? record?.graphQLErrors ?? []
  return list.map((item) => String(item.extensions?.code ?? '')).filter(Boolean)
}

function graphqlMessages(error: unknown): string[] {
  const record = error as { errors?: { message?: string }[]; message?: string } | null
  const list = record?.errors?.map((item) => item.message ?? '') ?? []
  if (record?.message) list.push(record.message)
  return list
}
