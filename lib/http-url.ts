const CONTROL_OR_BACKSLASH = /[\u0000-\u001F\u007F\\]/

/**
 * An absolute http(s) URL, or mailto when asked. `javascript:`, `data:`, and protocol-relative URLs are not links.
 * Tab, newline, and `\` are rejected first: the URL parser strips or rewrites them into a different scheme or host.
 */
export function safeLinkHref(href: string | null | undefined, options?: { mailto?: boolean }): string | null {
  if (!href || CONTROL_OR_BACKSLASH.test(href)) return null
  try {
    const url = new URL(href)
    if (url.protocol === 'http:' || url.protocol === 'https:') return href
    if (options?.mailto && url.protocol === 'mailto:') return href
    return null
  } catch {
    return null
  }
}
