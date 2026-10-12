import { serverEnv } from '@/lib/server-env'

/**
 * One-click unsubscribe (RFC 8058, lvn-backend ADR-0050): mail clients POST "List-Unsubscribe=One-Click" here, and
 * the API turns off the kind of email the token names. Only POST changes anything; a GET goes to the page that asks.
 */
export async function POST(request: Request): Promise<Response> {
  const token = new URL(request.url).searchParams.get('t') ?? ''
  const res = await fetch(serverEnv.apiUrl, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ query: 'mutation ($token: String!) { unsubscribeEmail(input: { token: $token }) { kind userErrors { message } } }', variables: { token } }),
    cache: 'no-store',
  }).catch(() => null)
  const body = (await res?.json().catch(() => null)) as { data?: { unsubscribeEmail?: { kind: string | null } } } | null
  return new Response(null, { status: body?.data?.unsubscribeEmail?.kind ? 200 : 400 })
}

export function GET(request: Request): Response {
  const url = new URL(request.url)
  return Response.redirect(new URL(`/unsubscribe?t=${encodeURIComponent(url.searchParams.get('t') ?? '')}`, url), 303)
}
