import { redirect } from 'next/navigation'

/** Saved resources are a section of Bookmarks now (lvn-backend ADR-0076): old links land there. */
export default function SavedResourcesPage(): never {
  redirect('/saved')
}
