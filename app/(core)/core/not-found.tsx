import type { Metadata } from 'next'
import { CoreApp } from '@core/app/CoreApp'

export const metadata: Metadata = { title: { absolute: 'Page not found · LearnViaNotes' }, robots: { index: false } }

/** A /core path that doesn't exist: the old app's router shows its own "not found" page, as before. */
export default function CoreNotFound() {
  return <CoreApp />
}
