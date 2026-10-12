import { createTranslator } from 'next-intl'
import { describe, expect, it } from 'vitest'
import messages from '@/messages/en.json'
import { describeNotification } from '@/features/notifications/describe'
import { liveUrlFrom } from '@/lib/env'

const t = createTranslator({ locale: 'en', messages, namespace: 'notifications' }) as unknown as (key: string, values?: Record<string, string | number>) => string
const meera = { id: 'u1', displayName: 'Meera Iyer' }
const say = (n: Partial<Parameters<typeof describeNotification>[0]>) => describeNotification({ category: 'SHARE', path: '/notes/n1', data: null, actor: null, note: null, group: null, classroom: null, ...n }, t)

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
    expect(say({ category: 'FOLLOW', actor: meera })).toBe('Meera Iyer started following you')
    expect(say({ category: 'CONNECTION', actor: meera, data: { kind: 'REQUESTED' } })).toBe('Meera Iyer wants to connect with you')
    expect(say({ category: 'CONNECTION', actor: meera, data: { kind: 'ACCEPTED' } })).toBe('Meera Iyer accepted your connection request')
    const g = { id: 'g1', name: 'Algorithms study' }
    expect(say({ category: 'JOIN_REQUEST', actor: meera, group: g })).toBe('Meera Iyer asked to join Algorithms study')
    expect(say({ category: 'JOIN_DECISION', data: { decision: 'APPROVED' }, group: g })).toBe("You're in: Algorithms study accepted your request")
    expect(say({ category: 'JOIN_DECISION', data: { decision: 'REJECTED' }, group: null })).toBe("a group didn't accept your request")
    expect(say({ category: 'QUIZ_PUBLISHED' })).toBe('Something new for you')
  })

  it('says who commented or replied, and on what (lvn-backend ADR-0047)', () => {
    const note = { id: 'n1', title: 'Heaps' }
    expect(say({ category: 'COMMENT', actor: meera, note, data: { kind: 'COMMENT' } })).toBe('Meera Iyer commented on “Heaps”')
    expect(say({ category: 'COMMENT', actor: meera, note, data: { kind: 'REPLY' } })).toBe('Meera Iyer replied to your comment on “Heaps”')
    expect(say({ category: 'COMMENT', path: '/groups/g1', actor: meera, group: { id: 'g1', name: 'Algorithms study' }, data: { kind: 'COMMENT' } })).toBe('Meera Iyer commented in Algorithms study')
    expect(say({ category: 'COMMENT', path: '/classes/c1', actor: meera, classroom: { id: 'c1', name: 'Physics 9A' }, data: { kind: 'REPLY' } })).toBe('Meera Iyer replied to your comment in Physics 9A')
    expect(say({ category: 'COMMENT', actor: meera, data: { kind: 'COMMENT' } })).toBe('Meera Iyer commented on something you can no longer open')
  })

  it('names the class of a request, an answer, an invite or an announcement (lvn-backend ADR-0046)', () => {
    const c = { id: 'c1', name: 'Physics 9A' }
    const path = '/classes/c1'
    expect(say({ category: 'JOIN_REQUEST', path, actor: meera, classroom: c })).toBe('Meera Iyer asked to join Physics 9A')
    expect(say({ category: 'JOIN_DECISION', path, data: { decision: 'APPROVED' }, classroom: c })).toBe("You're in: Physics 9A accepted your request")
    // A class you were not let into is no longer shown to you by name.
    expect(say({ category: 'JOIN_DECISION', path, data: { decision: 'REJECTED' } })).toBe("Your request to join a class wasn't accepted")
    expect(say({ category: 'CLASSROOM_INVITE', path, actor: meera, classroom: c })).toBe('Meera Iyer invited you to Physics 9A')
    expect(say({ category: 'CLASSROOM_POST', path, actor: meera, classroom: c })).toBe('Meera Iyer posted an announcement in Physics 9A')
    expect(say({ category: 'CLASSROOM_POST', path, actor: meera })).toBe('Meera Iyer posted an announcement in a class')
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
