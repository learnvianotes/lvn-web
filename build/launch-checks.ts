/* ============================================================
   LAUNCH CHECKS — every build:
     • uses its own Firebase project: a production build only the
       production project, any other build never it (a test site
       must not write to live accounts). Ids: .firebaserc.
   and a production build stops while the site isn't ready to go
   live: the Privacy Policy, Terms and Grievance pages need the
   operator's details (src/config.ts → LEGAL). Test builds
   (`npm run build:test`) show those gaps on the pages instead.
   ============================================================ */

import { readFileSync } from 'node:fs'
import type { Plugin } from 'vite'
import { LEGAL } from '../src/config'

/** The production Firebase project id (.firebaserc → projects.production). */
export function productionProject(root: string): string {
  const rc = JSON.parse(readFileSync(`${root}/.firebaserc`, 'utf8')) as { projects: Record<string, string> }
  return rc.projects.production
}

/** Why this build may not use this project, or '' when it may. */
export function projectProblem(siteEnv: string, project: string, production: string): string {
  if (siteEnv === 'production' && project !== production) {
    return `a production build must use the production Firebase project "${production}" (got "${project || 'none'}"). Put its keys in .env.production.local or the CI variables.`
  }
  if (siteEnv !== 'production' && project === production) {
    return `a ${siteEnv} build must not use the production Firebase project "${production}". Keep production keys out of .env.local (it loads for every build) — use .env.production.local, and the test project's keys in .env.test.local.`
  }
  return ''
}

export function blankLegalFields(legal: Record<string, string> = LEGAL): string[] {
  return Object.entries(legal).filter(([, v]) => !v.trim()).map(([k]) => k)
}

export function launchChecks(): Plugin {
  return {
    name: 'lvn-launch-checks',
    apply: 'build',
    configResolved(config) {
      const problem = projectProblem(String(config.env.VITE_SITE_ENV), String(config.env.VITE_FIREBASE_PROJECT_ID ?? ''), productionProject(config.root))
      if (problem) throw new Error(`Launch check: ${problem}`)
      if (config.env.VITE_SITE_ENV !== 'production') return
      const blank = blankLegalFields()
      if (blank.length) {
        throw new Error(
          `Launch check: src/config.ts → LEGAL is missing ${blank.join(', ')}. ` +
            'The Privacy Policy, Terms and Grievance pages can’t go live without them. ' +
            'Fill them in, or build for the test site with `npm run build:test`.',
        )
      }
    },
  }
}
