/* Keeps <title>, the description and the canonical link right as the app moves between pages
   (the build writes the same values into each page's HTML: shared/lib/pages.ts). Unknown
   addresses are left to NotFound, which titles itself and adds noindex. */

import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useCatalog } from '@/features/catalog/hooks'
import { pageFor } from '@/shared/lib/pages'

const SITE = (import.meta.env.VITE_SITE_URL ?? '').replace(/\/+$/, '')

function headTag<T extends HTMLElement>(selector: string, create: () => T): T {
  let el = document.head.querySelector<T>(selector)
  if (!el) {
    el = create()
    document.head.append(el)
  }
  return el
}

export function usePageMeta() {
  const { pathname } = useLocation()
  const { data } = useCatalog()
  useEffect(() => {
    const page = pageFor(pathname.replace(/(.)\/+$/, '$1'), data)
    if (!page) return
    document.title = page.title
    headTag<HTMLMetaElement>('meta[name="description"]', () => Object.assign(document.createElement('meta'), { name: 'description' })).content = page.description
    if (SITE) {
      headTag<HTMLLinkElement>('link[rel="canonical"]', () => Object.assign(document.createElement('link'), { rel: 'canonical' })).href =
        SITE + (page.canonical ?? page.path)
    }
  }, [pathname, data])
}
