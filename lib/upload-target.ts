/**
 * Where a pre-signed upload may go. The API names the URL; the browser still has to refuse one that is not storage.
 * A college ID, a note file, or a voice recording must not be PUT to whatever host a response names.
 */

export type StoragePutEnv = {
  /** development allows any http(s) host (local storage and tests). sandbox and production require the allowlist. */
  appEnv: string
  /** Space-separated origins, the same list as NEXT_PUBLIC_STORAGE_ORIGINS. */
  storageOrigins?: string
}

export type StoragePut = { url: string; headers: { name: string; value: string }[] }

const HEADER_NAME = /^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$/

/** Shown when the address or a header is not one this app will send. */
export const STORAGE_PUT_REFUSED = 'The file could not be uploaded. Storage address was refused.'

function allowedOrigin(origin: string, env: StoragePutEnv): boolean {
  const strict = env.appEnv === 'production' || env.appEnv === 'sandbox'
  const listed = env.storageOrigins?.trim().split(/\s+/).filter(Boolean) ?? []
  if (strict) return listed.includes(origin)
  return true
}

/**
 * The PUT this app will send, or null when the address or a header must not be used.
 * Content-Length is dropped: browsers set it and refuse a script-supplied value.
 */
export function storagePutRequest(
  intent: { uploadUrl: string; uploadHeaders: { name: string; value: string }[] },
  env: StoragePutEnv,
): StoragePut | null {
  if (/[\u0000-\u001F\u007F\\]/.test(intent.uploadUrl)) return null
  let url: URL
  try {
    url = new URL(intent.uploadUrl)
  } catch {
    return null
  }
  if (url.username || url.password) return null
  const https = url.protocol === 'https:'
  const httpDev = url.protocol === 'http:' && env.appEnv !== 'production' && env.appEnv !== 'sandbox'
  if (!https && !httpDev) return null
  if (!allowedOrigin(url.origin, env)) return null
  const headers: { name: string; value: string }[] = []
  for (const header of intent.uploadHeaders) {
    if (header.name.toLowerCase() === 'content-length') continue
    if (!HEADER_NAME.test(header.name) || /[\r\n]/.test(header.value)) return null
    headers.push(header)
  }
  return { url: url.toString(), headers }
}
