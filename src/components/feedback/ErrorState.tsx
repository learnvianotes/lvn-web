/* ============================================================
   ErrorState — visual error message component
   ============================================================ */

import { AlertTriangle, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/Button'

interface ErrorStateProps {
  title?: string
  description?: string
  onRetry?: () => void
}

export function ErrorState({
  title = 'Something went wrong',
  description = 'An unexpected error occurred. Please try refreshing the page.',
  onRetry,
}: ErrorStateProps) {
  return (
    <div className="feedback-state" role="alert">
      <div className="feedback-state__icon feedback-state__icon--danger" aria-hidden="true">
        <AlertTriangle size={24} />
      </div>
      <h2 className="feedback-state__title">{title}</h2>
      <p className="feedback-state__description">{description}</p>
      {onRetry ? (
        <Button variant="secondary" size="sm" onClick={onRetry}>
          <RefreshCw size={13} aria-hidden="true" />
          Try again
        </Button>
      ) : null}
    </div>
  )
}
