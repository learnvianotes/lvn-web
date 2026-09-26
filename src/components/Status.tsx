/* Loading / error / not-found states shared by every page. */

import { Link } from 'react-router-dom'
import { NotFoundError } from '@/content/source'

export function Loading({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="state" role="status">
      <span className="spinner" aria-hidden />
      <span>{label}</span>
    </div>
  )
}

/**
 * A page that exists in the catalog but whose content failed to load.
 * (Real unknown pages are handled by NotFound before anything is loaded.)
 */
export function LoadError({ error, retry }: { error: Error; retry?: () => void }) {
  return (
    <div className="state">
      <p className="state-title">Couldn’t load this content</p>
      <p className="state-text">
        {error instanceof NotFoundError
          ? 'It may be updating right now — please try again in a moment.'
          : navigator.onLine ? error.message : 'You’re offline and this page hasn’t been saved for offline use yet.'}
      </p>
      {retry && <button className="btn" onClick={retry}>Try again</button>}
    </div>
  )
}

export function NotFound() {
  return (
    <div className="state">
      <p className="state-title">Page not found</p>
      <p className="state-text">This subject or topic doesn’t exist.</p>
      <Link className="btn" to="/">Back to home</Link>
    </div>
  )
}
