/**
 * Same-origin Firebase auth helper (Google sign-in on a host that is not firebaseapp.com).
 *
 * Chrome and Safari partition storage on *.firebaseapp.com, so a popup or redirect that finishes there
 * never hands the result back. The browser loads /__/auth on this site; we fetch the helper from the
 * project's own firebaseapp.com host and return it here, including a redirect to accounts.google.com.
 * NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN stays that firebaseapp.com host — it is the upstream, not this site.
 */

const PROJECT_ID = /^[a-z][a-z0-9-]{4,28}[a-z0-9]$/
/** Playwright's stand-in project. It must not become a request to a real Firebase host. */
const E2E_PROJECT = 'lvn-e2e'
const SEGMENT = /^[A-Za-z0-9._-]{1,80}$/

/** What the helper document is allowed to do. The site's own policy (frame-ancestors 'none') must not be added on top. */
export const FIREBASE_AUTH_HELPER_CSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' https://apis.google.com https://www.gstatic.com https://www.google.com https://accounts.google.com",
  "style-src 'self' 'unsafe-inline' https://accounts.google.com",
  "img-src 'self' data: https://*.google.com https://*.gstatic.com https://*.googleusercontent.com",
  "connect-src 'self' https://*.googleapis.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.gstatic.com",
  "frame-src 'self' https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.gstatic.com",
  "form-action 'self' https://accounts.google.com https://*.google.com https://*.firebaseapp.com",
  "frame-ancestors 'self'",
  "base-uri 'self'",
  "object-src 'none'",
].join('; ')

export const FIREBASE_AUTH_HELPER_HEADERS: { key: string; value: string }[] = [
  { key: 'Content-Security-Policy', value: FIREBASE_AUTH_HELPER_CSP },
  { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
]

const REDIRECT_HOST = /(^|\.)((accounts\.google|google|googleapis|gstatic|googleusercontent)\.com)$/

/** The firebaseapp.com URL for this helper path, or null when the project or the path must not be proxied. */
export function firebaseAuthUpstream(projectId: string | undefined, segments: string[], search: string): URL | null {
  const id = projectId?.trim() ?? ''
  if (id === E2E_PROJECT || !PROJECT_ID.test(id)) return null
  if (segments.length === 0 || segments.length > 4 || segments.some((segment) => !SEGMENT.test(segment) || segment.includes('..'))) return null
  if (search.length > 2048 || (search !== '' && !search.startsWith('?')) || /[\r\n]/.test(search)) return null
  return new URL(`https://${id}.firebaseapp.com/__/auth/${segments.join('/')}${search}`)
}

/**
 * Where a helper redirect may send the browser. A hop back to this project's /__/auth stays on our origin.
 * Anything else is refused so the proxy cannot be an open redirect.
 */
/** A relative /__/auth path with no parent-directory segment. */
function safeAuthPath(location: string): string | null {
  const path = location.split(/[?#]/)[0] ?? ''
  if (!path.startsWith('/__/auth/') || path.includes('\\')) return null
  if (path.split('/').some((segment) => segment === '..' || segment === '.')) return null
  return location
}

export function rewriteFirebaseLocation(location: string, projectId: string): string | null {
  if (location.startsWith('/')) return safeAuthPath(location)
  let url: URL
  try {
    url = new URL(location)
  } catch {
    return null
  }
  if (url.protocol !== 'https:') return null
  const host = url.hostname.toLowerCase()
  if (host === `${projectId}.firebaseapp.com`) return safeAuthPath(`${url.pathname}${url.search}`)
  if (REDIRECT_HOST.test(host)) return url.toString()
  return null
}

export async function proxyFirebaseAuth(input: {
  projectId: string | undefined
  segments: string[]
  search: string
  method: string
  requestHeaders: Headers
  body: ArrayBuffer | null
  fetchImpl?: typeof fetch
}): Promise<Response> {
  if (input.method !== 'GET' && input.method !== 'HEAD' && input.method !== 'POST') return new Response(null, { status: 405 })
  const upstream = firebaseAuthUpstream(input.projectId, input.segments, input.search)
  if (!upstream) return new Response(null, { status: 404 })

  const headers = new Headers()
  const accept = input.requestHeaders.get('accept')
  const contentType = input.requestHeaders.get('content-type')
  if (accept) headers.set('accept', accept)
  if (contentType && input.method === 'POST') headers.set('content-type', contentType)

  let response: Response
  try {
    response = await (input.fetchImpl ?? fetch)(upstream, {
      method: input.method,
      headers,
      body: input.method === 'POST' ? input.body : undefined,
      redirect: 'manual',
      cache: 'no-store',
      signal: AbortSignal.timeout(15_000),
    })
  } catch {
    return new Response(null, { status: 502 })
  }

  const out = new Headers()
  const type = response.headers.get('content-type')
  if (type) out.set('content-type', type)
  if (input.method === 'POST') out.set('cache-control', 'no-store')
  else out.set('cache-control', response.headers.get('cache-control') ?? 'no-store')
  for (const header of FIREBASE_AUTH_HELPER_HEADERS) out.set(header.key, header.value)
  out.set('x-content-type-options', 'nosniff')
  out.set('referrer-policy', 'strict-origin-when-cross-origin')

  if (response.status >= 300 && response.status < 400) {
    const location = response.headers.get('location')
    const rewritten = location ? rewriteFirebaseLocation(location, input.projectId!.trim()) : null
    if (!rewritten) return new Response(null, { status: 502 })
    out.set('location', rewritten)
    return new Response(null, { status: response.status, headers: out })
  }

  return new Response(input.method === 'HEAD' ? null : response.body, { status: response.status, headers: out })
}
