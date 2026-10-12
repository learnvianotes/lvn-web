import { USER } from './notes-api'

/** People in the mocked API (lvn-backend ADR-0043, ADR-0044): the profiles in profiles.json and the viewer's relation to them. */
export const MEERA = '01920000-0000-7000-8000-0000000000e1'
export const RAVI = '01920000-0000-7000-8000-0000000000e2'
export const can = (over: Record<string, boolean> = {}) => ({ __typename: 'RelationActions', follow: true, unfollow: false, removeFollower: false, block: true, unblock: false, restrict: true, unrestrict: false, requestConnection: false, respondToConnection: false, removeConnection: false, ...over })
export const relation = (over: Record<string, unknown> = {}, actions: Record<string, boolean> = {}) => ({ __typename: 'Relation', following: false, followedBy: false, blocked: false, restricted: false, connected: false, pendingConnection: null, viewerCan: can(actions), ...over })
export const profileRelation = (rel: unknown, viewerId = USER, id = MEERA, verified = true) => ({ userByHandle: { __typename: 'User', id, followerCount: id === viewerId ? 12 : null, followingCount: id === viewerId ? 3 : null, relation: rel }, viewer: { __typename: 'User', id: viewerId, verified } })
