/* ============================================================
   Sheet150ProblemPage — THE CORE PROOF OF ARCHITECTURE
   Loads a single problem from Firestore by slug and renders it
   using generic, reusable components.

   URL: /sheet-150/problems/:slug
   Data: getProblemBySlug(slug) → Firestore

   There is NO TwoSumPage, NO ValidAnagramPage.
   This one component renders every Sheet 150 problem.
   ============================================================ */

import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { PageContainer } from '@/components/layout/PageContainer'
import { Breadcrumbs } from '@/components/navigation/Breadcrumbs'
import { Spinner } from '@/components/ui/Spinner'
import { getProblemBySlug } from '@/lib/sheet150'
import type { Sheet150Problem } from '@/types/sheet150'

import { ProblemHeader } from '@/features/sheet150/components/problem/ProblemHeader'
import { ProblemStatement } from '@/features/sheet150/components/problem/ProblemStatement'
import { KeyInsightSection } from '@/features/sheet150/components/problem/KeyInsightSection'
import { ApproachSection } from '@/features/sheet150/components/problem/ApproachSection'
import { SimilarQuestions } from '@/features/sheet150/components/problem/SimilarQuestions'

type LoadState = 'loading' | 'not-found' | 'error' | 'ready'

export function Sheet150ProblemPage() {
  const { slug } = useParams<{ slug: string }>()
  const [problem, setProblem] = useState<Sheet150Problem | null>(null)
  const [state, setState] = useState<LoadState>('loading')

  useEffect(() => {
    if (!slug) {
      setState('not-found')
      return
    }

    let cancelled = false
    setState('loading')

    getProblemBySlug(slug)
      .then((data) => {
        if (cancelled) return
        if (!data) {
          setState('not-found')
        } else {
          setProblem(data)
          setState('ready')
          // Update document title for SEO + browser history
          document.title = `${data.title} | Sheet 150 — CNotes`
        }
      })
      .catch(() => {
        if (!cancelled) setState('error')
      })

    return () => {
      cancelled = true
    }
  }, [slug])

  // Restore default title when navigating away
  useEffect(() => {
    return () => {
      document.title = 'CNotes'
    }
  }, [])

  /* ── Loading ─────────────────────────────────────── */
  if (state === 'loading') {
    return (
      <PageContainer narrow>
        <div className="s150-problem-page__loading">
          <Spinner size="md" />
          <span>Loading problem…</span>
        </div>
      </PageContainer>
    )
  }

  /* ── Not found ───────────────────────────────────── */
  if (state === 'not-found' || !problem) {
    return (
      <PageContainer narrow>
        <div className="feedback-state">
          <p className="feedback-state__code">404</p>
          <p className="feedback-state__title">Problem not found</p>
          <p className="feedback-state__description">
            "{slug}" doesn't exist in Sheet 150 yet.
          </p>
          <Link to="/sheet-150" className="btn btn--secondary btn--sm" style={{ marginTop: 16 }}>
            ← Back to Sheet 150
          </Link>
        </div>
      </PageContainer>
    )
  }

  /* ── Error ───────────────────────────────────────── */
  if (state === 'error') {
    return (
      <PageContainer narrow>
        <div className="feedback-state">
          <p className="feedback-state__title">Failed to load problem</p>
          <p className="feedback-state__description">
            Check your connection and try refreshing.
          </p>
        </div>
      </PageContainer>
    )
  }

  /* ── Problem render ──────────────────────────────── */
  return (
    <PageContainer narrow>
      {/* Breadcrumb navigation */}
      <Breadcrumbs
        items={[
          { label: 'Sheet 150', to: '/sheet-150' },
          { label: problem.category.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ').replace('And', '&'), to: `/sheet-150/category/${problem.category}` },
          { label: problem.title },
        ]}
      />

      {/* Problem title, difficulty, tags, LeetCode link */}
      <ProblemHeader problem={problem} />

      {/* Problem statement, examples, constraints */}
      <ProblemStatement problem={problem} />

      {/* Key insight / understanding */}
      {problem.keyInsight && (
        <KeyInsightSection insight={problem.keyInsight} />
      )}

      {/* Brute force approach */}
      {problem.naiveSolution && (
        <ApproachSection variant="brute-force" solution={problem.naiveSolution} />
      )}

      {/* Optimized approach */}
      {problem.optimalSolution && (
        <ApproachSection variant="optimized" solution={problem.optimalSolution} />
      )}

      {/* Similar questions */}
      {problem.similarQuestions && problem.similarQuestions.length > 0 && (
        <SimilarQuestions questions={problem.similarQuestions} />
      )}
    </PageContainer>
  )
}
