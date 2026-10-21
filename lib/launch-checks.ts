/**
 * Launch checks (lvn-backend ADR-0093), run by next.config.ts on `next build`: a production build stops while the
 * site isn't ready to go live. Today: the Privacy Policy, Terms and Grievance pages need the operator's details
 * (config/legal.ts → LEGAL). Other builds show those gaps on the pages instead.
 * Relative imports only: next.config.ts loads this file without the @/ alias.
 */
import { LEGAL, LEGAL_FIELD_LABELS, missingLegalFields, type LegalField } from '../config/legal'

export interface BuildFacts {
  /** NEXT_PUBLIC_APP_ENV */
  appEnv: string
  legal?: Record<LegalField, string>
}

/** Why this build may not go ahead; empty when it may. */
export function launchProblems({ appEnv, legal = LEGAL }: BuildFacts): string[] {
  const problems: string[] = []
  if (appEnv === 'production') {
    const missing = missingLegalFields(legal)
    if (missing.length) {
      problems.push(
        `config/legal.ts → LEGAL is missing the ${missing.map((k) => LEGAL_FIELD_LABELS[k]).join(', ')}. The Privacy Policy, ` +
          'Terms and Grievance pages can’t go live without them: fill them in, or build for the sandbox (NEXT_PUBLIC_APP_ENV=sandbox).',
      )
    }
  }
  return problems
}
