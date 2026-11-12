import { releaseInfo } from '@/lib/release'

/** Build identity: `{ version, commit }`. The commit is baked in at image build time. */
export function GET() {
  return Response.json(releaseInfo(), { headers: { 'cache-control': 'no-store' } })
}
