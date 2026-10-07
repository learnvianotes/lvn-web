/**
 * localStorage key for the reader's theme, shared with the /core pages (core-app/src/shared/lib/theme.ts):
 * the old site's key, so a returning reader keeps their choice. The value is JSON ("light" / "dark"),
 * as core-app's storage service writes it. Read by the pre-paint script in app/(site)/layout.tsx.
 */
export const THEME_KEY = 'cnote:theme'
