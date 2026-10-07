/* ============================================================
   AUTH — guest-only. The /core pages are the original
   LearnViaNotes notes as visitors saw them; accounts now belong
   to the new platform (lvn-backend ADR-0007), so sign-in is
   permanently "unavailable" here and every signed-in branch of
   these pages stays hidden — exactly the old guest experience.
   ============================================================ */

export interface AppUser {
  uid: string
  name: string
  email: string
  photoURL: string
  emailVerified: boolean
  provider: string
}

export type AuthState =
  | { status: 'loading' }
  | { status: 'unavailable' }
  | { status: 'signed-out' }
  | { status: 'signed-in'; user: AppUser }

const state: AuthState = { status: 'unavailable' }

export const getAuthState = (): AuthState => state
export const useAuth = (): AuthState => state
export const useUser = (): AppUser | null => null
