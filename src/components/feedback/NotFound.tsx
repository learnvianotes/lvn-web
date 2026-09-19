/* ============================================================
   NotFound — 404 component (can be used as page or embedded)
   ============================================================ */

import { Link } from 'react-router-dom'
import { FileQuestion, ArrowLeft } from 'lucide-react'

interface NotFoundProps {
  message?: string
}

export function NotFound({
  message = 'The page you are looking for does not exist.',
}: NotFoundProps) {
  return (
    <div className="feedback-state">
      <div className="feedback-state__code" aria-hidden="true">404</div>
      <div className="feedback-state__icon feedback-state__icon--muted" aria-hidden="true">
        <FileQuestion size={24} />
      </div>
      <h2 className="feedback-state__title">Page not found</h2>
      <p className="feedback-state__description">{message}</p>
      <Link to="/" className="btn btn--secondary btn--sm">
        <ArrowLeft size={13} aria-hidden="true" />
        Back to home
      </Link>
    </div>
  )
}
