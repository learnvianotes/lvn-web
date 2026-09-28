/* Small, dismissible hint for guests on study pages: what signing in unlocks. */

import './auth.css'
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Sparkles, X } from 'lucide-react'
import { get, set } from '@/services/storage'
import { useAuth } from './auth'

const KEY = 'unlock-hint-dismissed'

export function UnlockHint() {
  const auth = useAuth()
  const location = useLocation()
  const [dismissed, setDismissed] = useState(() => get<number>(KEY) ?? 0)
  // Shown to guests, at most once every 3 days after dismissing.
  if (auth.status !== 'signed-out' || Date.now() - dismissed < 3 * 86_400_000) return null
  return (
    <div className="unlock-hint">
      <Sparkles size={15} aria-hidden className="unlock-hint-icon" />
      <p>
        <Link to={`/login?next=${encodeURIComponent(location.pathname + location.hash)}`}>Sign in</Link> to unlock
        read-aloud, the smart study kit, focus timer, notes and your study streak.
      </p>
      <button className="icon-btn sm" onClick={() => { const now = Date.now(); set(KEY, now); setDismissed(now) }} aria-label="Dismiss">
        <X size={14} />
      </button>
    </div>
  )
}
