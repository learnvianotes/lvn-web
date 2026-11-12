/** Twelve hex characters: the length `.github/workflows/deploy.yml` pins (`GITHUB_SHA::12`). */
const SHORT_SHA = 12
const SHA = /^[0-9a-f]{7,40}$/i

export type ReleaseInfo = { version: string; commit: string }

/**
 * The running build. `version` is `package.json`, copied to `NEXT_PUBLIC_APP_VERSION` by `next.config.ts`.
 * `commit` is the build-time `NEXT_PUBLIC_GIT_SHA` (Dockerfile `ARG`, default `unknown`). A missing value or
 * anything that is not a git SHA is reported as `unknown`.
 */
export function releaseInfo(
  source: { version?: string | null; commit?: string | null } = {
    version: process.env.NEXT_PUBLIC_APP_VERSION,
    commit: process.env.NEXT_PUBLIC_GIT_SHA,
  },
): ReleaseInfo {
  const version = (source.version ?? '').trim().replace(/^[vV]/, '')
  const commit = (source.commit ?? '').trim()
  return {
    version: version || 'unknown',
    commit: SHA.test(commit) ? commit.toLowerCase().slice(0, SHORT_SHA) : 'unknown',
  }
}
