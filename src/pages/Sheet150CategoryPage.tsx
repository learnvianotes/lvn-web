/* ============================================================
   Sheet150CategoryPage — Problem list for one category
   URL: /sheet-150/category/:categoryId
   Data: getProblemsByCategory(categoryId) → Firestore
   ============================================================ */

import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { PageContainer } from '@/components/layout/PageContainer'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import { Spinner } from '@/components/ui/Spinner'
import { getProblemsByCategory } from '@/lib/sheet150'
import { ProblemCard } from '@/features/sheet150/components/ProblemCard'
import type { Sheet150Problem } from '@/types/sheet150'

function formatCategory(slug: string): string {
  return slug
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
    .replace('And', '&')
}

export function Sheet150CategoryPage() {
  const { categoryId } = useParams<{ categoryId: string }>()
  const [problems, setProblems] = useState<Sheet150Problem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  const categoryLabel = categoryId ? formatCategory(categoryId) : 'Category'

  useEffect(() => {
    if (!categoryId) {
      setLoading(false)
      return
    }

    let cancelled = false
    setLoading(true)
    setError(false)

    getProblemsByCategory(categoryId)
      .then((data) => {
        if (cancelled) return
        setProblems(data)
        setLoading(false)
        document.title = `${categoryLabel} | Sheet 150 — CNotes`
      })
      .catch(() => {
        if (!cancelled) {
          setError(true)
          setLoading(false)
        }
      })

    return () => {
      cancelled = true
    }
  }, [categoryId, categoryLabel])

  return (
    <PageContainer>
      <Breadcrumbs
        items={[
          { label: 'Sheet 150', to: '/sheet-150' },
          { label: categoryLabel },
        ]}
      />

      <div className="page-header">
        <p className="page-header__label">Sheet 150</p>
        <h1 className="page-header__title">{categoryLabel}</h1>
        {!loading && !error && (
          <p className="page-header__description">
            {problems.length} {problems.length === 1 ? 'problem' : 'problems'}
          </p>
        )}
      </div>

      {loading && (
        <div className="s150-problem-page__loading">
          <Spinner size="md" />
          <span>Loading problems…</span>
        </div>
      )}

      {error && (
        <div className="feedback-state">
          <p className="feedback-state__title">Failed to load problems</p>
          <p className="feedback-state__description">Check your connection and try refreshing.</p>
        </div>
      )}

      {!loading && !error && problems.length === 0 && (
        <div className="feedback-state">
          <p className="feedback-state__title">No problems yet</p>
          <p className="feedback-state__description">
            Problems for "{categoryLabel}" haven't been seeded to Firebase yet.
          </p>
          <Link to="/sheet-150" className="btn btn--secondary btn--sm" style={{ marginTop: 16 }}>
            ← Back to Sheet 150
          </Link>
        </div>
      )}

      {!loading && !error && problems.length > 0 && (
        <div className="s150-problem-list">
          {problems.map((p) => (
            <ProblemCard key={p.id} problem={p} />
          ))}
        </div>
      )}
    </PageContainer>
  )
}
