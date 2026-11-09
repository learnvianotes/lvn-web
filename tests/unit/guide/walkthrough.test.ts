import { describe, expect, it } from 'vitest'
import { dismissWalkthrough, queueWalkthrough, readWalkthrough, shouldAutoShowWalkthrough, tourKeyAction } from '@/lib/walkthrough'

function memory() {
  const data = new Map<string, string>()
  return {
    getItem: (key: string) => data.get(key) ?? null,
    setItem: (key: string, value: string) => {
      data.set(key, value)
    },
  }
}

describe('first-run walkthrough storage', () => {
  it('shows once after a profile is created, and not again after skip or finish', () => {
    const store = memory()
    expect(shouldAutoShowWalkthrough('user-a', store)).toBe(false)
    queueWalkthrough('user-a', store)
    expect(shouldAutoShowWalkthrough('user-a', store)).toBe(true)
    expect(shouldAutoShowWalkthrough('user-b', store)).toBe(false)
    dismissWalkthrough('user-a', store)
    expect(shouldAutoShowWalkthrough('user-a', store)).toBe(false)
    queueWalkthrough('user-a', store)
    expect(readWalkthrough(store).pending).toBe(null)
    expect(shouldAutoShowWalkthrough('user-a', store)).toBe(false)
  })

  it('keeps a second account pending on the same browser', () => {
    const store = memory()
    queueWalkthrough('user-a', store)
    dismissWalkthrough('user-a', store)
    queueWalkthrough('user-b', store)
    expect(shouldAutoShowWalkthrough('user-b', store)).toBe(true)
    expect(readWalkthrough(store).dismissed).toEqual(['user-a'])
  })

  it('ignores a broken stored value', () => {
    const store = memory()
    store.setItem('lvn.walkthrough', '{')
    expect(readWalkthrough(store)).toEqual({ pending: null, dismissed: [] })
  })
})

describe('tour keys', () => {
  it('maps Escape, arrows and Tab, and leaves other keys alone', () => {
    expect(tourKeyAction('Escape', false)).toBe('skip')
    expect(tourKeyAction('ArrowRight', false)).toBe('next')
    expect(tourKeyAction('ArrowLeft', false)).toBe('back')
    expect(tourKeyAction('Tab', false)).toBe('tab-next')
    expect(tourKeyAction('Tab', true)).toBe('tab-prev')
    expect(tourKeyAction('Enter', false)).toBe(null)
  })
})
