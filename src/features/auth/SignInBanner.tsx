/* Sign-in call to action where the streak calendar would be (and on /history). */

import './auth.css'
import { Link, useLocation } from 'react-router-dom'
import { Flame, History, RefreshCw, Sparkles } from 'lucide-react'
import { useAuth } from './auth'

export function SignInBanner({ overlay = false }: { overlay?: boolean }) {
  const auth = useAuth()
  const location = useLocation()
  const next = encodeURIComponent(location.pathname + location.hash)
  const Tag = overlay ? 'div' : 'section'
  return (
    <Tag className={`signin-banner ${overlay ? 'is-overlay' : 'panel'}`}>
      <div className="signin-banner-icon" aria-hidden><Flame size={22} /></div>
      <h2 className="signin-banner-title">Keep your study streak</h2>
      <p className="signin-banner-text">Sign in to track your streak, time spent and history — on every device.</p>
      <ul className="signin-banner-list">
        <li><Flame size={14} aria-hidden /> Daily streak & study calendar</li>
        <li><History size={14} aria-hidden /> Topics visited, time spent, revisits</li>
        <li><Sparkles size={14} aria-hidden /> Read-aloud, smart study kit, focus timer</li>
        <li><RefreshCw size={14} aria-hidden /> Synced across your devices</li>
      </ul>
      {auth.status === 'unavailable' ? (
        <p className="muted small">Sign-in isn’t available right now.</p>
      ) : (
        <div className="signin-banner-actions">
          <Link className="btn btn-primary btn-sm" to={`/login?next=${next}`}>Log in</Link>
          <Link className="btn btn-sm" to={`/signup?next=${next}`}>Create account</Link>
        </div>
      )}
    </Tag>
  )
}
