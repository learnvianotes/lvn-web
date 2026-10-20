/* ============================================================
   /privacy · /terms · /grievance — one layout, three documents.
   Until src/config.ts → LEGAL is filled in, the missing facts
   show as highlighted gaps (and production builds refuse).
   ============================================================ */

import './legal.css'
import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { LEGAL } from '@/config'
import { formatLegalDate, LEGAL_FIELD_LABELS, LEGAL_PAGES, missingLegalFields, type LegalDoc } from './legal'
import { PrivacyPolicy } from './PrivacyPolicy'
import { Terms } from './Terms'
import { Grievance } from './Grievance'

const BODIES: Record<LegalDoc, () => React.ReactNode> = { privacy: PrivacyPolicy, terms: Terms, grievance: Grievance }

export function LegalPage({ doc }: { doc: LegalDoc }) {
  const { title } = LEGAL_PAGES[doc]
  const Body = BODIES[doc]
  const missing = missingLegalFields()

  return (
    <div className="page page-narrow">
      <Link to="/" className="back-link"><ArrowLeft size={14} aria-hidden /> All subjects</Link>
      <article className="prose legal">
        <h1 className="page-title">{title}</h1>
        <p className="muted legal-effective">Effective {formatLegalDate(LEGAL.effective)}</p>
        {missing.length > 0 && (
          <p className="legal-draft" role="note">
            Draft — still to be filled in: {missing.map((k) => LEGAL_FIELD_LABELS[k]).join(', ')}.
          </p>
        )}
        <Body />
        <nav className="legal-nav" aria-label="Legal">
          {(Object.keys(LEGAL_PAGES) as LegalDoc[]).filter((d) => d !== doc).map((d) => (
            <Link key={d} to={LEGAL_PAGES[d].path}>{LEGAL_PAGES[d].title}</Link>
          ))}
        </nav>
      </article>
    </div>
  )
}
