/* ============================================================
   LoadingState — full-area loading indicator
   ============================================================ */

import { Spinner } from '@/components/ui/Spinner'

interface LoadingStateProps {
  message?: string
}

export function LoadingState({ message = 'Loading…' }: LoadingStateProps) {
  return (
    <div className="feedback-state" role="status" aria-live="polite">
      <Spinner size="lg" label={message} />
      <p className="feedback-state__description" aria-hidden="true">{message}</p>
    </div>
  )
}
