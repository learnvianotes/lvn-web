/** Where to go after signing in: registration details first, then the page the learner came from, else their profile. */
export function afterSignIn(user: { registrationComplete: boolean }, next?: string | null): string {
  if (!user.registrationComplete) return `/sign-up/details${next ? `?next=${encodeURIComponent(next)}` : ''}`
  return safeNext(next) ?? '/profile'
}

/** Only same-site paths: an attacker-supplied `next` must not send people to another site after sign-in. */
export function safeNext(next?: string | null): string | null {
  if (!next || !next.startsWith('/') || next.startsWith('//') || next.startsWith('/\\')) return null
  return next
}
