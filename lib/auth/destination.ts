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

/**
 * Only same-site paths: an attacker-supplied `next` must not send people to another site after sign-in.
 *
 * `router.replace` parses the path with the WHATWG URL parser and, when the origin differs, assigns
 * `location`. That parser strips tab, newline, and carriage return, and turns `\` into `/`, so
 * `/%0A/evil.example` and `/\evil.example` become protocol-relative URLs. Reject those characters, then
 * require the parsed URL to stay on a dummy origin.
 */
export function safeNext(next?: string | null): string | null {
  if (!next || /[\u0000-\u001F\u007F\\]/.test(next)) return null
  if (!next.startsWith('/') || next.startsWith('//')) return null
  try {
    const url = new URL(next, 'https://lvn.invalid')
    if (url.origin !== 'https://lvn.invalid') return null
    const path = `${url.pathname}${url.search}${url.hash}`
    if (!path.startsWith('/') || path.startsWith('//')) return null
    return path
  } catch {
    return null
  }
}

/** `/` and `/?…` are the marketing page, whatever query it carries. */
function isLanding(path: string): boolean {
  const pathname = path.split(/[?#]/)[0] ?? path
  return pathname === '/' || pathname === ''
}
