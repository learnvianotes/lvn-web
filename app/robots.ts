import type { MetadataRoute } from 'next'
import { env } from '@/lib/env'
import { ROBOTS_DISALLOW } from '@/lib/site'

/**
 * /robots.txt. Public pages are allowed; private areas are not. The Sitemap line uses NEXT_PUBLIC_SITE_URL.
 * This file is a metadata route, outside the signed-in and auth layouts, so session guards never redirect it.
 * Non-production HTML pages still send noindex from the root layout.
 */
export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: '*', allow: '/', disallow: [...ROBOTS_DISALLOW] },
    sitemap: `${env.NEXT_PUBLIC_SITE_URL}/sitemap.xml`,
  }
}
