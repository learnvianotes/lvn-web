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
