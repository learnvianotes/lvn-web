'use client'

import { Search } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useSession } from '@/state/session'
import { OPEN_SEARCH_EVENT } from './SearchPalette'

/** The header's search: opens the palette where the app is loaded, otherwise the search page. */
export function SearchButton({ label }: { label: string }) {
  const router = useRouter()
  const signedIn = useSession((s) => s.status === 'signed-in')
  if (!signedIn) return null
  return (
    <button
      type="button"
      aria-label={label}
      title={`${label} (Ctrl+K)`}
      onClick={() => {
        // A palette on the page cancels the event; without one, go to the search page.
        if (window.dispatchEvent(new Event(OPEN_SEARCH_EVENT, { cancelable: true }))) router.push('/search')
      }}
      className="inline-flex items-center gap-2 rounded-lg px-2 py-2 text-sm font-medium text-muted hover:bg-surface-2 hover:text-fg sm:rounded-full sm:border sm:border-border sm:px-3 sm:py-1.5"
    >
      <Search className="size-4" aria-hidden />
      <span className="hidden sm:inline">{label}</span>
      <kbd className="hidden rounded border border-border px-1 text-[10px] lg:inline">Ctrl K</kbd>
    </button>
  )
}
