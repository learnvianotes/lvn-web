/* Landing page — subject cards. Progress lives in the right panel (header button). */

import { useEffect, useRef } from 'react'
import { useCatalog } from '@/content/hooks'
import { useProgress } from '@/progress/store'
import { subjectProgress } from '@/progress/stats'
import { SubjectCard } from '@/components/SubjectCard'
import { LoadError, Loading } from '@/components/Status'
import { SiteFooter } from '@/components/SiteFooter'
import { useLayout } from '@/components/layout/LayoutState'
import { APP_NAME } from '@/config'

export function HomePage() {
  const catalog = useCatalog()
  const progress = useProgress()
  const { highlighted, setHighlighted } = useLayout()
  const cardRefs = useRef(new Map<string, HTMLAnchorElement>())

  // Progress wheel selection → bring that subject's card into view.
  useEffect(() => {
    if (highlighted) cardRefs.current.get(highlighted)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }, [highlighted])
  useEffect(() => () => setHighlighted(undefined), [setHighlighted])

  return (
    <div className="page">
      <h1 className="sr-only">{APP_NAME} — subjects</h1>
      {catalog.status === 'loading' && <Loading />}
      {catalog.status === 'error' && <LoadError error={catalog.error} retry={catalog.retry} />}
      {catalog.data && (
        <div className="card-grid">
          {catalog.data.subjects.map((s) => (
            <SubjectCard
              key={s.id}
              ref={(el) => { if (el) cardRefs.current.set(s.id, el); else cardRefs.current.delete(s.id) }}
              to={`/${s.id}`}
              icon={s.icon}
              title={s.title}
              description={s.description}
              countLabel={`${s.itemCount} ${s.kind === 'problems' ? 'problems' : 'topics'}`}
              progress={subjectProgress(s, progress)}
              highlighted={highlighted === s.id}
            />
          ))}
        </div>
      )}
      <SiteFooter />
    </div>
  )
}
