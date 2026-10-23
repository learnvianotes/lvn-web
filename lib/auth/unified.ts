/** EMAIL, then the providers, in the order the account page lists them. */
export const SIGN_IN_METHOD_ORDER = ['EMAIL', 'GOOGLE', 'GITHUB', 'LINKEDIN'] as const

export type SignInMethodId = (typeof SIGN_IN_METHOD_ORDER)[number]

/**
 * Continue with Google is shown only when this deployment has Firebase and an admin has left Google on.
 * When the authSettings query cannot be read (an API from before that field), signInOptions.google still decides.
 */
export function googleButtonVisible(input: {
  firebaseConfigured: boolean
  googleSignInEnabled: boolean | null | undefined
  signInOptionsGoogle?: boolean
  authSettingsFailed?: boolean
}): boolean {
  if (!input.firebaseConfigured) return false
  if (input.authSettingsFailed && input.googleSignInEnabled == null) return input.signInOptionsGoogle === true
  return input.googleSignInEnabled === true
}

/**
 * Sign-up found a verified account with this email and no password (for example one made with Google).
 * A CONFLICT still means "sign in instead": that account already has a password.
 */
export function isEmailLinkPending(payload: {
  emailLinkPending?: boolean | null
  session?: unknown
  userErrors?: { code?: string | null }[] | null
}): boolean {
  if (payload.session) return false
  if (payload.userErrors?.some((error) => error.code === 'CONFLICT')) return false
  return payload.emailLinkPending === true
}

/** The viewer's linked methods, in display order. Null (as on a sign-in response) and unknowns list nothing. */
export function linkedSignInMethods(methods: readonly string[] | null | undefined): SignInMethodId[] {
  if (!methods?.length) return []
  const have = new Set(methods)
  return SIGN_IN_METHOD_ORDER.filter((method) => have.has(method))
}
