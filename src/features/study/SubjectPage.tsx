/* ============================================================
   /:subjectId
   Notes subjects open straight into their first topic.
   Problem sheets show their categories first (intermediate page).
   ============================================================ */

import { Link, Navigate, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useCatalog, useSubject } from '@/features/catalog/hooks'
import type { Subject } from '@/features/catalog/types'
import { useProgress } from '@/features/progress/store'
import { SubjectCard } from '@/features/catalog/SubjectCard'
import { LoadError, Loading, NotFound } from '@/shared/ui/Status'

export function SubjectPage() {
  const { subjectId } = useParams()
  const catalog = useCatalog()
  const subject = useSubject(subjectId)

  if (catalog.status === 'loading') return <Loading />
  if (catalog.status === 'error') return <LoadError error={catalog.error} retry={catalog.retry} />
  if (!subject || !subject.topics.length) return <NotFound />
  if (subject.kind === 'notes') return <Navigate to={`/${subject.id}/${subject.topics[0].id}`} replace />
  return <CategoryIndex subject={subject} />
}

function CategoryIndex({ subject }: { subject: Subject }) {
  const progress = useProgress()
  const solved = (ids: string[]) => ids.filter((id) => progress.problems[id] === 'solved').length
  const total = subject.itemCount
  const allSolved = solved(subject.topics.flatMap((t) => (t.problems ?? []).map((p) => p.id)))

  return (
    <div className="page">
      <div className="page-head">
        <Link to="/" className="back-link"><ArrowLeft size={14} aria-hidden /> All subjects</Link>
        <h1 className="page-title">{subject.title}</h1>
        <p className="page-desc">{subject.description}</p>
        <p className="muted">{allSolved} of {total} solved</p>
      </div>
      <div className="card-grid">
        {subject.topics.map((t) => {
          const ids = (t.problems ?? []).map((p) => p.id)
          const done = solved(ids)
          return (
            <SubjectCard
              key={t.id}
              to={`/${subject.id}/${t.id}`}
              title={t.title}
              countLabel={`${ids.length} problems`}
              progress={{ done, total: ids.length, ratio: ids.length ? done / ids.length : 0 }}
            />
          )
        })}
      </div>
    </div>
  )
}
