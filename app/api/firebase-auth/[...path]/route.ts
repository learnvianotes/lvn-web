import { proxyFirebaseAuth } from '@/lib/auth/firebase-auth-proxy'

/**
 * Firebase's auth helper, served on this origin. next.config.ts rewrites /__/auth/* here so the browser never
 * sees a redirect to firebaseapp.com. The global frame-ancestors 'none' header does not apply to /__/auth
 * (lib/security-headers.ts); this response allows the sign-in page to frame the helper.
 */
export const dynamic = 'force-dynamic'

async function handle(request: Request, context: { params: Promise<{ path: string[] }> }): Promise<Response> {
  const { path } = await context.params
  const url = new URL(request.url)
  return proxyFirebaseAuth({
    projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
    segments: path,
    search: url.search,
    method: request.method,
    requestHeaders: request.headers,
    body: request.method === 'POST' ? await request.arrayBuffer() : null,
  })
}

export const GET = handle
export const HEAD = handle
export const POST = handle
