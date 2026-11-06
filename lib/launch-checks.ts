/**
 * Launch checks (lvn-backend ADR-0093), run by next.config.ts on `next build`:
 * - every build uses its own Firebase project: a production build only the production project, any other build never
 *   it, so a test site can't sign anyone into live accounts (ids: config/firebase-projects.json);
 * - a production build stops while the site isn't ready to go live: the Privacy Policy, Terms and Grievance pages need
 *   the operator's details (config/legal.ts → LEGAL). Other builds show those gaps on the pages instead.
 * A production build for this machine (NEXT_PUBLIC_SITE_URL on localhost: scripts/lighthouse.mjs) skips them: its
 * addresses are compiled in, so it can never be deployed.
 * Relative imports only: next.config.ts loads this file without the @/ alias.
 */
import { readFileSync } from 'node:fs'
import { LEGAL, LEGAL_FIELD_LABELS, missingLegalFields, type LegalField } from '../config/legal'

export interface BuildFacts {
  /** NEXT_PUBLIC_APP_ENV */
  appEnv: string
  /** NEXT_PUBLIC_SITE_URL */
  siteUrl?: string
  /** NEXT_PUBLIC_API_URL. A production launch must call the API over https. */
  apiUrl?: string
  /** NEXT_PUBLIC_LIVE_URL. When set on a production launch, it must be wss. */
  liveUrl?: string
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

/** Whether the site's address is this machine: such a build serves only here (audits), never a deployment. */
export const isLocalSite = (siteUrl: string): boolean => /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/|$)/.test(siteUrl)

/**
 * Why this production address is not safe to ship, or null when it is.
 * Empty values are ignored: a missing variable is reported by env validation, not here.
 */
export function transportProblem(kind: 'site' | 'api' | 'live', value: string | undefined): string | null {
  if (!value) return null
  if (kind === 'live') {
    if (value.startsWith('wss://')) return null
    return `NEXT_PUBLIC_LIVE_URL must be wss:// in a production build (got ${value}). Access tokens go over that socket.`
  }
  if (value.startsWith('https://')) return null
  const name = kind === 'site' ? 'NEXT_PUBLIC_SITE_URL' : 'NEXT_PUBLIC_API_URL'
  return `${name} must be https:// in a production build (got ${value}). Session tokens must not travel in cleartext.`
}

/** Why this build may not go ahead; empty when it may. */
export function launchProblems({ appEnv, siteUrl = '', apiUrl, liveUrl, firebaseProject = '', productionProject = productionFirebaseProject(), legal = LEGAL }: BuildFacts): string[] {
  if (appEnv === 'production' && isLocalSite(siteUrl)) return []
  const problems: string[] = []
  if (appEnv === 'production') {
    for (const problem of [transportProblem('site', siteUrl), transportProblem('api', apiUrl), transportProblem('live', liveUrl)]) {
      if (problem) problems.push(problem)
    }
  }
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
