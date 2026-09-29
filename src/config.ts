/* ============================================================
   APP CONFIG — the few values you may want to change.
   ============================================================ */

export const APP_NAME = 'LearnViaNotes'

/**
 * Google Apps Script web-app URL that appends feedback to a Google Sheet.
 * Setup: docs/feedback-google-sheets.md. Empty = the form explains it isn't set up yet.
 */
export const FEEDBACK_URL = 'https://script.google.com/macros/s/AKfycbwbtuRhZWjI0lrGsT4z1CJSbJmGIPZ8sPnI1tYUGq5WKZ-DNq-PGBAGN6CN0sa2XTwU/exec'

/** Google AdSense client id (ca-pub-…). Empty = no ads and no ad script. */
export const ADSENSE_CLIENT = ''

/**
 * Sign-in providers shown on the login page, in order. Add one only after enabling it in
 * Firebase console → Authentication → Sign-in method (docs/auth-setup.md).
 * Email + password is always shown.
 */
export const AUTH_PROVIDERS: ('google' | 'github' | 'linkedin')[] = ['google']

/**
 * Domains where the site runs on Firebase Hosting. On these, sign-in uses the site's own domain
 * (its built-in /__/auth/handler) instead of <project>.firebaseapp.com, so mobile browsers that block
 * cross-site storage (Safari, newer Chrome/Firefox) can finish redirect sign-ins.
 * Each one needs its https://<domain>/__/auth/handler added as an authorized redirect URI of the
 * Google OAuth client (docs/auth-setup.md → "Sign-in on your own domain").
 */
// Empty until the redirect URIs are added to the OAuth client Firebase actually uses
// (client id 761935379919-92vi63rnkfrq5vqi5jphehsg2sd4jg7b…). Then: ['www.learnvianotes.in', 'learnvianote.web.app']
export const SAME_SITE_AUTH_DOMAINS: string[] = []
