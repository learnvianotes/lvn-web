'use client'

import { env } from '@/lib/env'

export type OAuthProvider = 'GITHUB' | 'LINKEDIN'

const KEY = 'lvn:oauth'
const SCOPES: Record<OAuthProvider, string> = { GITHUB: 'read:user user:email', LINKEDIN: 'openid profile email' }

const b64url = (bytes: Uint8Array) => btoa(String.fromCharCode(...bytes)).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
const random = (n: number) => b64url(crypto.getRandomValues(new Uint8Array(n)))

/** The redirect URI registered with GitHub and LinkedIn; lvn-backend accepts only those (OAUTH_REDIRECT_URIS). */
export const redirectUri = () => new URL('/oauth/callback', env.NEXT_PUBLIC_SITE_URL).toString()

export function oauthAvailable(provider: OAuthProvider): boolean {
  return provider === 'GITHUB'
    ? !!(env.NEXT_PUBLIC_GITHUB_CLIENT_ID && env.NEXT_PUBLIC_GITHUB_AUTHORIZE_URL)
    : !!(env.NEXT_PUBLIC_LINKEDIN_CLIENT_ID && env.NEXT_PUBLIC_LINKEDIN_AUTHORIZE_URL)
}

/**
 * Authorization Code + PKCE (§7.1): a random verifier stays in this tab; the provider sees only its SHA-256
 * challenge. A random state ties the callback to this attempt.
 */
export async function startOAuth(provider: OAuthProvider, next?: string): Promise<void> {
  const verifier = random(48)
  const state = random(24)
  const challenge = b64url(new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier))))
  sessionStorage.setItem(KEY, JSON.stringify({ provider, verifier, state, next }))
  const base = provider === 'GITHUB' ? env.NEXT_PUBLIC_GITHUB_AUTHORIZE_URL! : env.NEXT_PUBLIC_LINKEDIN_AUTHORIZE_URL!
  const url = new URL(base)
  url.search = new URLSearchParams({
    client_id: provider === 'GITHUB' ? env.NEXT_PUBLIC_GITHUB_CLIENT_ID! : env.NEXT_PUBLIC_LINKEDIN_CLIENT_ID!,
    redirect_uri: redirectUri(),
    response_type: 'code',
    scope: SCOPES[provider],
    state,
    code_challenge: challenge,
    code_challenge_method: 'S256',
  }).toString()
  window.location.assign(url.toString())
}

/** The pending attempt for this callback, if its state matches; consumed so it cannot be replayed. */
export function takeOAuthAttempt(state: string | null): { provider: OAuthProvider; verifier: string; next?: string } | null {
  const raw = sessionStorage.getItem(KEY)
  sessionStorage.removeItem(KEY)
  if (!raw || !state) return null
  const attempt = JSON.parse(raw) as { provider: OAuthProvider; verifier: string; state: string; next?: string }
  return attempt.state === state ? attempt : null
}
