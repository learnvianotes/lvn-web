import { describe, expect, it } from 'vitest'
import { storagePutRequest } from '@/lib/upload-target'

const header = { name: 'content-type', value: 'image/png' }

describe('storage PUT targets', () => {
  it('allows a listed https origin in production and keeps the headers storage asked for', () => {
    const put = storagePutRequest(
      { uploadUrl: 'https://storage.example/put/id?X-Amz-Signature=abc', uploadHeaders: [header, { name: 'x-amz-acl', value: 'private' }, { name: 'content-length', value: '4' }] },
      { appEnv: 'production', storageOrigins: 'https://storage.example https://cdn.example' },
    )
    expect(put?.url).toBe('https://storage.example/put/id?X-Amz-Signature=abc')
    expect(put?.headers.map((item) => item.name)).toEqual(['content-type', 'x-amz-acl'])
  })

  it('refuses another host, cleartext, and a header that is not a header', () => {
    const env = { appEnv: 'production', storageOrigins: 'https://storage.example' }
    expect(storagePutRequest({ uploadUrl: 'https://evil.example/put', uploadHeaders: [header] }, env)).toBeNull()
    expect(storagePutRequest({ uploadUrl: 'http://storage.example/put', uploadHeaders: [header] }, env)).toBeNull()
    expect(storagePutRequest({ uploadUrl: 'javascript:alert(1)', uploadHeaders: [] }, env)).toBeNull()
    expect(storagePutRequest({ uploadUrl: 'https://user:pass@storage.example/put', uploadHeaders: [] }, env)).toBeNull()
    expect(storagePutRequest({ uploadUrl: 'https://storage.example/put', uploadHeaders: [{ name: 'content-type\r\nX', value: 'text/html' }] }, env)).toBeNull()
    expect(storagePutRequest({ uploadUrl: 'https://storage.example/put', uploadHeaders: [] }, { appEnv: 'production' })).toBeNull()
  })

  it('allows the local storage stand-in while developing', () => {
    expect(storagePutRequest({ uploadUrl: 'http://storage.test/put/1', uploadHeaders: [header] }, { appEnv: 'development' })?.url).toBe('http://storage.test/put/1')
  })
})
