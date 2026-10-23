/** The signed-in app: Home lists what the person is studying. The landing page is only for visitors. */
export const APP_HOME = '/home'

/** Where to go after signing in: registration details first, then the page they came from, else Home. */
export function afterSignIn(user: { registrationComplete: boolean }, next?: string | null): string {
  if (!user.registrationComplete) return `/sign-up/details${next ? `?next=${encodeURIComponent(next)}` : ''}`
  return signedInDestination(next)
}

/**
 * A finished account's destination. A deep link in `next` wins. The landing page does not: sending them there would
 * only bounce straight to Home.
 */
export function signedInDestination(next?: string | null): string {
  const dest = safeNext(next)
  if (!dest || isLanding(dest)) return APP_HOME
  return dest
}

/** Only same-site paths: an attacker-supplied `next` must not send people to another site after sign-in. */
export function safeNext(next?: string | null): string | null {
  if (!next || !next.startsWith('/') || next.startsWith('//') || next.startsWith('/\\')) return null
  return next
}

/** `/` and `/?…` are the marketing page, whatever query it carries. */
function isLanding(path: string): boolean {
  const pathname = path.split(/[?#]/)[0] ?? path
  return pathname === '/' || pathname === ''
}
