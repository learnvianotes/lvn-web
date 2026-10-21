/**
 * Launch checks (lvn-backend ADR-0093), run by next.config.ts on `next build`:
 * - every build uses its own Firebase project: a production build only the production project, any other build never
 *   it, so a test site can't sign anyone into live accounts (ids: config/firebase-projects.json);
 * - a production build stops while the site isn't ready to go live: the Privacy Policy, Terms and Grievance pages need
 *   the operator's details (config/legal.ts → LEGAL). Other builds show those gaps on the pages instead.
 * Relative imports only: next.config.ts loads this file without the @/ alias.
 */
import { readFileSync } from 'node:fs'
import { LEGAL, LEGAL_FIELD_LABELS, missingLegalFields, type LegalField } from '../config/legal'

export interface BuildFacts {
  /** NEXT_PUBLIC_APP_ENV */
  appEnv: string
  /** NEXT_PUBLIC_FIREBASE_PROJECT_ID; empty when this build has no Google sign-in */
  firebaseProject?: string
  /** The production project's id (config/firebase-projects.json) */
  productionProject?: string
  legal?: Record<LegalField, string>
}

/** The production Firebase project's id, from config/firebase-projects.json. */
export function productionFirebaseProject(root = process.cwd()): string {
  return (JSON.parse(readFileSync(`${root}/config/firebase-projects.json`, 'utf8')) as { production: string }).production
}

/** Why this build may not use this Firebase project, or '' when it may. */
export function firebaseProblem(appEnv: string, project: string, production: string): string {
  if (appEnv === 'production' && project !== production) {
    return `a production build must use the production Firebase project "${production}" (got "${project || 'none'}"): set its web config in NEXT_PUBLIC_FIREBASE_*.`
  }
  if (appEnv !== 'production' && project === production) {
    return `a ${appEnv} build must not use the production Firebase project "${production}": give it the test project's keys (sandbox) or your own (development).`
  }
  return ''
}

/** Why this build may not go ahead; empty when it may. */
export function launchProblems({ appEnv, firebaseProject = '', productionProject = productionFirebaseProject(), legal = LEGAL }: BuildFacts): string[] {
  const problems: string[] = []
  const firebase = firebaseProblem(appEnv, firebaseProject, productionProject)
  if (firebase) problems.push(firebase)
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
