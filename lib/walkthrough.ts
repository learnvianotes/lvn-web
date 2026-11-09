/**
 * First-run walkthrough, once per account on this browser.
 * The API has no "has seen the tour" field, so dismissal lives in localStorage, keyed by user id.
 * `pending` is set when a profile is created. Replay opens the tour again without clearing dismissal.
 */

const KEY = 'lvn.walkthrough'
export const WALKTHROUGH_EVENT = 'lvn:walkthrough'
/** Ask the phone drawer to open (`true`) or close (`false`) while the tour is spotlighting a nav item. */
export const TOUR_MENU_EVENT = 'lvn:tour-menu'

export type WalkthroughState = { pending: string | null; dismissed: string[] }

type Store = Pick<Storage, 'getItem' | 'setItem'>

const browserStore = (): Store | null => {
  try {
    return typeof window === 'undefined' ? null : window.localStorage
  } catch {
    return null
  }
}

const empty = (): WalkthroughState => ({ pending: null, dismissed: [] })

export function readWalkthrough(store: Store | null = browserStore()): WalkthroughState {
  if (!store) return empty()
  try {
    const raw = JSON.parse(store.getItem(KEY) ?? '') as Partial<WalkthroughState>
    const dismissed = Array.isArray(raw.dismissed) ? raw.dismissed.filter((id): id is string => typeof id === 'string' && id.length > 0).slice(-40) : []
    const pending = typeof raw.pending === 'string' && raw.pending.length > 0 ? raw.pending : null
    return { pending, dismissed }
  } catch {
    return empty()
  }
}

function write(state: WalkthroughState, store: Store | null) {
  store?.setItem(KEY, JSON.stringify(state))
}

/** Remember that this account just finished creating a profile, unless the tour was already dismissed here. */
export function queueWalkthrough(userId: string, store: Store | null = browserStore()): void {
  if (!userId) return
  const state = readWalkthrough(store)
  if (state.dismissed.includes(userId)) return
  write({ ...state, pending: userId }, store)
}

/** True when this account's profile was just created and the tour has not been skipped or finished here. */
export function shouldAutoShowWalkthrough(userId: string, store: Store | null = browserStore()): boolean {
  if (!userId) return false
  const state = readWalkthrough(store)
  return state.pending === userId && !state.dismissed.includes(userId)
}

/** Skip or finish: do not auto-show again for this account on this browser. */
export function dismissWalkthrough(userId: string, store: Store | null = browserStore()): void {
  if (!userId) return
  const state = readWalkthrough(store)
  const dismissed = state.dismissed.includes(userId) ? state.dismissed : [...state.dismissed, userId].slice(-40)
  write({ pending: state.pending === userId ? null : state.pending, dismissed }, store)
}

/** Asks the signed-in shell to open the tour. No-op until that shell is mounted. */
export function requestWalkthrough(): void {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new Event(WALKTHROUGH_EVENT))
}

/** Opens or closes the phone navigation drawer for the tour. Desktop ignores it. */
export function setTourMenu(open: boolean): void {
  if (typeof window === 'undefined') return
  window.dispatchEvent(new CustomEvent(TOUR_MENU_EVENT, { detail: open }))
}

/** Keyboard intent for the tour. Tab stays in the dialog; arrows move steps; Escape skips. */
export function tourKeyAction(key: string, shiftKey: boolean): 'skip' | 'next' | 'back' | 'tab-next' | 'tab-prev' | null {
  if (key === 'Escape') return 'skip'
  if (key === 'ArrowRight') return 'next'
  if (key === 'ArrowLeft') return 'back'
  if (key === 'Tab') return shiftKey ? 'tab-prev' : 'tab-next'
  return null
}
