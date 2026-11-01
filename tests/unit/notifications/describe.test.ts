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

  it('tells a submitter what moderators decided about their resource (lvn-backend ADR-0074)', () => {
    expect(say({ category: 'RESOURCE', path: '/resources/r1', data: { decision: 'APPROVED' } })).toBe('Your resource is in the catalogue')
    expect(say({ category: 'RESOURCE', path: '/resources/r1', data: { decision: 'REJECTED' } })).toBe('Moderators did not approve your resource')
    expect(say({ category: 'RESOURCE', path: '/resources/r1', data: { kind: 'RECOMMENDED' }, actor: meera })).toBe('Meera Iyer recommended a resource to you')
    expect(say({ category: 'COMMENT', path: '/resources/r1', data: { kind: 'COMMENT' }, actor: meera })).toBe('Meera Iyer commented on your resource')
  })

  it('says who asked to be Rhythm buddies, and who agreed (lvn-backend ADR-0072)', () => {
    expect(say({ category: 'RHYTHM_BUDDY', path: '/rhythm', data: { kind: 'REQUESTED' }, actor: meera })).toBe('Meera Iyer asked you to be Rhythm buddies')
    expect(say({ category: 'RHYTHM_BUDDY', path: '/rhythm', data: { kind: 'ACCEPTED' }, actor: meera })).toBe('Meera Iyer is now your Rhythm buddy')
  })

  it('names in settings every category people can set (lvn-backend preferences.service SETTABLE)', () => {
    const settable = ['SHARE', 'COMMENT', 'FOLLOW', 'CONNECTION', 'JOIN_REQUEST', 'JOIN_DECISION', 'CLASSROOM_INVITE', 'CLASSROOM_POST', 'QUIZ_PUBLISHED', 'MENTOR_INVITE', 'DOUBT', 'MENTION', 'VERIFICATION', 'DATA_EXPORT', 'NOTES_IMPORT', 'REVISION_REMINDER', 'RHYTHM_BUDDY', 'RESOURCE']
    const labels = messages.settings.category as Record<string, string>
    expect(settable.filter((c) => !labels[c])).toEqual([])
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
    // An exam's revision task left today (lvn-backend ADR-0070); a category this build does not know says little.
    expect(say({ category: 'REVISION_REMINDER', data: { examName: 'Operating Systems', topics: 'Paging' } })).toBe('Today’s revision for Operating Systems is waiting')
    expect(say({ category: 'REVISION_REMINDER' })).toBe('Today’s revision is waiting')
    expect(say({ category: 'STREAK_AT_RISK' })).toBe('Something new for you')
    // An application to teach decided (lvn-backend ADR-0073).
    expect(say({ category: 'VERIFICATION', data: { kind: 'DECIDED', decision: 'APPROVED', purpose: 'TEACHER_ROLE' } })).toBe('You’re a verified teacher now: your classes can take students')
    expect(say({ category: 'VERIFICATION', data: { kind: 'DECIDED', decision: 'REJECTED', purpose: 'TEACHER_ROLE' } })).toBe('Your application to teach wasn’t approved; see why on Teach')
  })

  it('says who commented or replied, and on what (lvn-backend ADR-0047)', () => {
    const note = { id: 'n1', title: 'Heaps' }
    expect(say({ category: 'COMMENT', actor: meera, note, data: { kind: 'COMMENT' } })).toBe('Meera Iyer commented on “Heaps”')
    expect(say({ category: 'COMMENT', actor: meera, note, data: { kind: 'REPLY' } })).toBe('Meera Iyer replied to your comment on “Heaps”')
    expect(say({ category: 'COMMENT', path: '/groups/g1', actor: meera, group: { id: 'g1', name: 'Algorithms study' }, data: { kind: 'COMMENT' } })).toBe('Meera Iyer commented in Algorithms study')
    expect(say({ category: 'COMMENT', path: '/classes/c1', actor: meera, classroom: { id: 'c1', name: 'Physics 9A' }, data: { kind: 'REPLY' } })).toBe('Meera Iyer replied to your comment in Physics 9A')
    expect(say({ category: 'COMMENT', actor: meera, data: { kind: 'COMMENT' } })).toBe('Meera Iyer commented on something you can no longer open')
  })

  it('mentor invites and doubts name the workspace (lvn-backend ADR-0048)', () => {
    const group = { id: 'g1', name: 'Heap visualiser' }
    expect(say({ category: 'MENTOR_INVITE', actor: meera, group })).toBe('Meera Iyer asked you to mentor Heap visualiser')
    expect(say({ category: 'DOUBT', actor: meera, group, data: { kind: 'ASKED' } })).toBe('Meera Iyer asked a doubt in Heap visualiser')
    expect(say({ category: 'DOUBT', actor: meera, group, data: { kind: 'ANSWERED', byMentor: true } })).toBe('Meera Iyer answered your doubt in Heap visualiser')
    expect(say({ category: 'DOUBT', actor: meera, group, data: { kind: 'RESOLVED' } })).toBe('Meera Iyer marked your doubt in Heap visualiser resolved')
  })

  it('tells authors what moderators decided, where, never why (lvn-backend ADR-0051)', () => {
    const group = { id: 'g1', name: 'Heaps club' }
    const classroom = { id: 'c1', name: 'Physics 9A' }
    expect(say({ category: 'MODERATION', group, path: '/groups/g1', data: { kind: 'HIDDEN', entityType: 'GROUP_POST' } })).toBe('Moderators hid your post in Heaps club. Open it to see why.')
    expect(say({ category: 'MODERATION', classroom, path: '/classes/c1', data: { kind: 'REMOVED', entityType: 'COMMENT' } })).toBe('Moderators removed your comment in Physics 9A. Open it to see why.')
    expect(say({ category: 'MODERATION', note: { id: 'n1', title: 'Heaps' }, data: { kind: 'HIDDEN', entityType: 'COMMENT' } })).toBe('Moderators hid your comment on “Heaps”. Open it to see why.')
    expect(say({ category: 'MODERATION', classroom, path: '/classes/c1', data: { kind: 'WARNED', entityType: 'CLASSROOM_POST' } })).toBe('Moderators left a warning on your announcement in Physics 9A.')
    expect(say({ category: 'MODERATION', group, path: '/groups/g1/doubts/d1', data: { kind: 'RESTORED', entityType: 'DOUBT' } })).toBe('Moderators put your doubt in Heaps club back.')
    expect(say({ category: 'MODERATION', group, path: '/groups/g1', data: { kind: 'WARNED', entityType: 'GROUP' } })).toBe('Moderators left a warning on your group Heaps club.')
    expect(say({ category: 'MODERATION', path: '/groups/g1', data: { kind: 'REMOVED', entityType: 'GROUP' } })).toBe('Moderators removed your group. Open it to see why.')
    expect(say({ category: 'MODERATION', group, path: '/groups/g1', data: { kind: 'RESTORED', entityType: 'GROUP' } })).toBe('Moderators put your group Heaps club back.')
  })

  it('says who mentioned the viewer and where, never what they wrote (lvn-backend ADR-0054)', () => {
    expect(say({ category: 'MENTION', actor: meera, note: { id: 'n1', title: 'Heaps' }, path: '/notes/n1', data: { entityType: 'COMMENT' } })).toBe('Meera Iyer mentioned you in a comment on “Heaps”')
    expect(say({ category: 'MENTION', actor: meera, group: { id: 'g1', name: 'Heaps club' }, path: '/groups/g1', data: { entityType: 'GROUP_POST' } })).toBe('Meera Iyer mentioned you in a post in Heaps club')
    expect(say({ category: 'MENTION', actor: meera, path: '/groups/g1', data: { entityType: 'GROUP_POST' } })).toBe('Meera Iyer mentioned you somewhere you can no longer open')
  })

  it('tells a person about their own account: a warning, a suspension, and a suspension lifted (lvn-backend ADR-0053)', () => {
    const path = '/profile'
    expect(say({ category: 'MODERATION', path, data: { kind: 'WARNED', entityType: 'USER' } })).toBe('Moderators warned your account. Open your account to read why.')
    expect(say({ category: 'MODERATION', path, data: { kind: 'SUSPENDED', entityType: 'USER' } })).toBe('Moderators suspended your account. Open your account to see until when and why.')
    expect(say({ category: 'MODERATION', path, data: { kind: 'RESTORED', entityType: 'USER' } })).toBe('Your account’s suspension has ended early.')
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
    // A quiz published to the class (lvn-backend ADR-0064).
    expect(say({ category: 'QUIZ_PUBLISHED', path: '/classes/c1/quizzes/q1', actor: meera, classroom: c })).toBe('Meera Iyer published a quiz in Physics 9A')
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

describe('where a notification opens (lvn-backend ADR-0076)', () => {
  it('opens a comment or mention on a note in its Discussions tab, everything else at its path', async () => {
    const { notificationHref } = await import('@/features/notifications/describe')
    const note = '/notes/01920000-0000-7000-8000-00000000a001'
    expect(notificationHref({ category: 'COMMENT', path: note })).toBe(`${note}?tab=discussions`)
    expect(notificationHref({ category: 'MENTION', path: note })).toBe(`${note}?tab=discussions`)
    expect(notificationHref({ category: 'COMMENT', path: '/groups/g1' })).toBe('/groups/g1')
    expect(notificationHref({ category: 'SHARE', path: note })).toBe(note)
  })

  it('does not open an off-site path', async () => {
    const { notificationHref } = await import('@/features/notifications/describe')
    expect(notificationHref({ category: 'SHARE', path: 'https://evil.example' })).toBe('/notifications')
    expect(notificationHref({ category: 'SHARE', path: '//evil.example' })).toBe('/notifications')
    expect(notificationHref({ category: 'SHARE', path: '/\n/evil.example' })).toBe('/notifications')
  })
})
