/* ============================================================
   Landing page
     • Hero                 signed in: streak, goal, continue
                            guests: what the site is + start / sign in
     • Subjects             the 13 catalog subjects — filter for all,
                            sort + rearrange when signed in
     • Problem of the day (one slim bar; on phones it sits right
                            under the hero — a quick win before the list)
     • Explore more courses (upcoming only, behind a button)
   ============================================================ */

import './home.css'
import { useCallback, useEffect, useMemo, useRef } from 'react'
import { useCatalog } from '@/features/catalog/hooks'
import { useUser } from '@/features/auth/auth'
import { LoadError, Loading } from '@/shared/ui/Status'
import { SiteFooter } from '@/app/shell/SiteFooter'
import { useLayout } from '@/app/shell/LayoutState'
import { APP_NAME } from '@/config'
import { GuestHero, HomeHero } from './HomeHero'
import { SubjectsSection } from './SubjectsSection'
import { ProblemOfTheDay } from './ProblemOfTheDay'
import { ExploreCourses } from './ExploreCourses'

export function HomePage() {
  const catalog = useCatalog()
  const user = useUser()
  const { highlighted, setHighlighted } = useLayout()
  const cardRefs = useRef(new Map<string, HTMLAnchorElement>())
  const cardRef = useCallback((id: string, el: HTMLAnchorElement | null) => {
    if (el) cardRefs.current.set(id, el)
    else cardRefs.current.delete(id)
  }, [])

  // Progress wheel selection → bring that subject's card into view.
  useEffect(() => {
    if (highlighted) cardRefs.current.get(highlighted)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [highlighted])
  useEffect(() => () => setHighlighted(undefined), [setHighlighted])

  const available = useMemo(() => new Set(catalog.data?.subjects.map((s) => s.id) ?? []), [catalog.data])

  return (
    <div className="page home">
      {user ? <HomeHero user={user} /> : catalog.data ? <GuestHero catalog={catalog.data} /> : <h1 className="sr-only">{APP_NAME} — subjects</h1>}
      {catalog.status === 'loading' && <Loading />}
      {catalog.status === 'error' && <LoadError error={catalog.error} retry={catalog.retry} />}
      {catalog.data && (
        <>
          <SubjectsSection catalog={catalog.data} highlighted={highlighted} cardRef={cardRef} />
          <ProblemOfTheDay catalog={catalog.data} />
          <ExploreCourses live={available} />
        </>
      )}
      <SiteFooter />
    </div>
  )
}
