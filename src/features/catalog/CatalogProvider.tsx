/* Loads the catalog once and shares it app-wide (see useCatalog in hooks.ts). */

import type { ReactNode } from 'react'
import { CatalogContext, useCatalogState } from '@/features/catalog/hooks'

export function CatalogProvider({ children }: { children: ReactNode }) {
  const state = useCatalogState()
  return <CatalogContext.Provider value={state}>{children}</CatalogContext.Provider>
}
