import type { MetadataRoute } from 'next'
import { env } from '@/lib/env'

export default function robots(): MetadataRoute.Robots {
  if (env.NEXT_PUBLIC_APP_ENV !== 'production') return { rules: { userAgent: '*', disallow: '/' } }
  return { rules: { userAgent: '*', allow: '/' }, sitemap: `${env.NEXT_PUBLIC_SITE_URL}/sitemap.xml` }
}
