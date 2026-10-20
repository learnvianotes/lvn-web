/* ============================================================
   LAUNCH CHECKS — a production build stops while the site isn't
   ready to go live. Today: the Privacy Policy, Terms and
   Grievance pages need the operator's details (src/config.ts →
   LEGAL). Test builds (`npm run build:test`) skip the checks and
   show the gaps on the pages instead.
   ============================================================ */

import type { Plugin } from 'vite'
import { LEGAL } from '../src/config'

export function blankLegalFields(legal: Record<string, string> = LEGAL): string[] {
  return Object.entries(legal).filter(([, v]) => !v.trim()).map(([k]) => k)
}

export function launchChecks(): Plugin {
  return {
    name: 'lvn-launch-checks',
    apply: 'build',
    configResolved(config) {
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
