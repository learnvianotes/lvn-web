/* ============================================================
   ConsentBanner — asks once whether Google Analytics may run.
   Both answers weigh the same; the choice can be changed any
   time in Settings → Privacy. Never shown when this build has
   no analytics, or once a choice exists on this device.
   ============================================================ */

import './consent.css'
import { Link } from 'react-router-dom'
import { analyticsAvailable } from '@/services/analytics'
import { setAnalyticsConsent, useAnalyticsConsent } from '@/services/consent'

export function ConsentBanner() {
  const consent = useAnalyticsConsent()
  if (consent !== null || !analyticsAvailable()) return null
  return (
    <section className="consent" role="region" aria-label="Analytics cookies">
      <p>
        Can we use <strong>Google Analytics</strong>? It sets cookies to count visits and show which notes help.
        Nothing is collected unless you allow it; you can change your mind in Settings.{' '}
        <Link to="/privacy">Privacy Policy</Link>
      </p>
      <div className="consent-actions">
        <button className="btn btn-sm" onClick={() => setAnalyticsConsent('denied')}>Don’t allow</button>
        <button className="btn btn-sm" onClick={() => setAnalyticsConsent('granted')}>Allow</button>
      </div>
    </section>
  )
}
