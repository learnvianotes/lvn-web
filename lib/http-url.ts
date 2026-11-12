const CONTROL_OR_BACKSLASH = /[\u0000-\u001F\u007F\\]/

/**
 * An absolute http(s) URL, or mailto when asked. A `blob:` URL is allowed only for a file this page just created
 * (an upload preview). `javascript:`, `data:`, and protocol-relative URLs are not links.
 * Tab, newline, and `\` are rejected first: the URL parser strips or rewrites them into a different scheme or host.
 */
export function safeLinkHref(href: string | null | undefined, options?: { mailto?: boolean; blob?: boolean }): string | null {
  if (!href || CONTROL_OR_BACKSLASH.test(href)) return null
  try {
    const url = new URL(href)
    // The canonical URL, not the raw string: the parser strips or rewrites characters the raw value still has.
    if (url.username || url.password) return null
    if (url.protocol === 'http:' || url.protocol === 'https:') return url.href
    if (options?.mailto && url.protocol === 'mailto:') return url.href
    if (options?.blob && url.protocol === 'blob:') return url.href
    return null
  } catch {
    return null
  }
}
