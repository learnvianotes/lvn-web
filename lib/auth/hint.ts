/**
 * A mark that this browser has signed in. It is not a credential and grants nothing: the access token stays in
 * memory and the refresh token stays in its HttpOnly cookie. The mark only lets `/` stay blank until Home opens,
 * instead of painting the landing page and then leaving it.
 */
export const SIGNED_IN_HINT_KEY = 'lvn.signed-in'

/** Hide the landing before paint only on `/`, and only when this browser has signed in. */
export function shouldHoldLanding(pathname: string, hint: string | null): boolean {
  return pathname === '/' && hint === '1'
}

/**
 * Runs from `<head>` before first paint. Inline on purpose: a stylesheet can arrive after the first paint, and an
 * inline visibility hides the page even then. Keep it in step with `shouldHoldLanding` and `releaseLandingPaint`.
 */
export function landingHoldScript(): string {
  const key = JSON.stringify(SIGNED_IN_HINT_KEY)
  return `try{if(location.pathname==='/'&&localStorage.getItem(${key})==='1'){document.documentElement.dataset.landing='away';document.documentElement.style.visibility='hidden'}}catch(e){}`
}

/** The same hide the head script applies, for a client navigation to `/` (the head script does not run again). */
export function holdLandingPaint(): void {
  if (typeof document === 'undefined') return
  document.documentElement.dataset.landing = 'away'
  document.documentElement.style.visibility = 'hidden'
}

/** Shows the page again. Home and every other address call this; so does `/` once the session is known to be gone. */
export function releaseLandingPaint(): void {
  if (typeof document === 'undefined') return
  delete document.documentElement.dataset.landing
  document.documentElement.style.visibility = ''
}
