import { createTranslator } from 'next-intl'
import { describe, expect, it } from 'vitest'
import messages from '@/messages/en.json'
import { describeNotification } from '@/features/notifications/describe'
import { liveUrlFrom } from '@/lib/env'

const t = createTranslator({ locale: 'en', messages, namespace: 'notifications' }) as unknown as (key: string, values?: Record<string, string | number>) => string
const meera = { id: 'u1', displayName: 'Meera Iyer' }
const say = (n: Partial<Parameters<typeof describeNotification>[0]>) => describeNotification({ category: 'SHARE', data: null, actor: null, note: null, ...n }, t)

describe('notification sentences (lvn-backend ADR-0042)', () => {
  it('names who shared which note, and says so when the note is gone', () => {
    expect(say({ actor: meera, note: { id: 'n1', title: 'Heaps' } })).toBe('Meera Iyer shared “Heaps” with you')
    expect(say({ actor: meera, note: { id: 'n1', title: '' } })).toBe('Meera Iyer shared “Untitled note” with you')
    expect(say({ actor: meera })).toBe('Meera Iyer shared a note with you that you can no longer open')
    expect(say({})).toBe('Someone shared a note with you that you can no longer open')
  })

  it('tells verification requests and decisions apart, never naming platform admins', () => {
    expect(say({ category: 'VERIFICATION', data: { kind: 'REQUESTED' }, actor: meera })).toBe('Meera Iyer asked you to verify their account')
    expect(say({ category: 'VERIFICATION', data: { kind: 'DECIDED', decision: 'APPROVED' }, actor: meera })).toBe('Meera Iyer verified your account')
    expect(say({ category: 'VERIFICATION', data: { kind: 'DECIDED', decision: 'APPROVED' } })).toBe('Your account is verified')
    expect(say({ category: 'VERIFICATION', data: { kind: 'DECIDED', decision: 'REJECTED' } })).toMatch(/^Your verification was not accepted/)
  })

  it('counts an import in words, leaving out what is zero', () => {
    expect(say({ category: 'NOTES_IMPORT', data: { created: 1, skipped: 0, failed: 0 } })).toBe('Your import is done: 1 note added')
    expect(say({ category: 'NOTES_IMPORT', data: { created: 4, skipped: 2, failed: 1 } })).toBe('Your import is done: 4 notes added, 2 skipped, 1 could not be read')
    expect(say({ category: 'DATA_EXPORT' })).toBe('Your data export is ready to download')
    expect(say({ category: 'COMMENT' })).toBe('Something new for you')
  })
})

describe('liveUrlFrom', () => {
  const api = 'https://api.example.in/graphql'
  it('uses NEXT_PUBLIC_LIVE_URL, derives it only in development, and is off elsewhere', () => {
    expect(liveUrlFrom({ NEXT_PUBLIC_APP_ENV: 'production', NEXT_PUBLIC_API_URL: api, NEXT_PUBLIC_LIVE_URL: 'wss://live.example.in/graphql/live' })).toBe('wss://live.example.in/graphql/live')
    expect(liveUrlFrom({ NEXT_PUBLIC_APP_ENV: 'development', NEXT_PUBLIC_API_URL: 'http://localhost:4000/graphql', NEXT_PUBLIC_LIVE_URL: undefined })).toBe('ws://localhost:4000/graphql/live')
    expect(liveUrlFrom({ NEXT_PUBLIC_APP_ENV: 'production', NEXT_PUBLIC_API_URL: api, NEXT_PUBLIC_LIVE_URL: undefined })).toBeNull()
  })
})
