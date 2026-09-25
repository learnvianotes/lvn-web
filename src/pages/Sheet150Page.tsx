/* ============================================================
   Sheet150Page — Hub / Landing page for Sheet 150
   URL: /sheet-150
   Phase 1: Shows a static list of known categories with links.
   The category list will be Firestore-driven in Phase 3.
   ============================================================ */

import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, ListChecks } from 'lucide-react'
import { PageContainer } from '@/components/layout/PageContainer'
import { seedSheet150Problems } from '@/lib/sheet150'

const PHASE1_CATEGORIES = [
  { id: 'arrays-hashing', label: 'Arrays & Hashing', count: 4 },
  { id: 'binary-search', label: 'Binary Search', count: 1 },
]

const PHASE1_PROBLEMS = [
  { slug: 'contains-duplicate', lcNumber: 217, title: 'Contains Duplicate', difficulty: 'Easy' },
  { slug: 'valid-anagram',       lcNumber: 242, title: 'Valid Anagram',       difficulty: 'Easy' },
  { slug: 'two-sum',             lcNumber: 1,   title: 'Two Sum',             difficulty: 'Easy' },
  { slug: 'group-anagrams',      lcNumber: 49,  title: 'Group Anagrams',      difficulty: 'Medium' },
  { slug: 'binary-search',       lcNumber: 704, title: 'Binary Search',       difficulty: 'Easy' },
]

export function Sheet150Page() {
  // Ensure Firestore is seeded with the enriched schema in background
  useEffect(() => {
    seedSheet150Problems().catch(() => {})
  }, [])

  return (
    <PageContainer>
      {/* Page header */}
      <div className="page-header">
        <div className="s150-hub__title-row">
          <div className="s150-hub__icon">
            <ListChecks size={20} aria-hidden="true" />
          </div>
          <div>
            <p className="page-header__label">DSA</p>
            <h1 className="page-header__title">Sheet 150</h1>
          </div>
        </div>
        <p className="page-header__description">
          150 curated interview problems with brute-force and optimised solutions,
          complexity analysis, and multi-language code.
        </p>
      </div>

      {/* Status callout */}
      <div className="s150-hub__status-callout">
        <span className="s150-hub__status-label">Phase 1 — Architecture Proof</span>
        <p className="s150-hub__status-desc">
          5 problems seeded to Firebase across 2 categories.
          Rendered entirely through React components without iframes or legacy HTML.
        </p>
      </div>

      {/* Category grid */}
      <p className="section-label" style={{ marginTop: 32 }}>Categories</p>
      <div className="s150-category-grid">
        {PHASE1_CATEGORIES.map((cat) => (
          <Link
            key={cat.id}
            to={`/sheet-150/category/${cat.id}`}
            className="s150-category-card"
          >
            <div className="s150-category-card__body">
              <span className="s150-category-card__label">{cat.label}</span>
              <span className="s150-category-card__count">
                {cat.count} {cat.count === 1 ? 'problem' : 'problems'}
              </span>
            </div>
            <ArrowRight size={16} aria-hidden="true" className="s150-category-card__arrow" />
          </Link>
        ))}
      </div>

      {/* Quick access to demo problems */}
      <p className="section-label" style={{ marginTop: 32 }}>Problems seeded in Phase 1</p>
      <div className="s150-problem-list">
        {PHASE1_PROBLEMS.map((p) => (
          <Link
            key={p.slug}
            to={`/sheet-150/problems/${p.slug}`}
            className="s150-problem-card"
            aria-label={`${p.title} — ${p.difficulty}`}
          >
            <span className="s150-problem-card__num">#{p.lcNumber}</span>
            <span className="s150-problem-card__body">
              <span className="s150-problem-card__title">{p.title}</span>
            </span>
            <div className="s150-problem-card__right">
              <span className={`badge badge--difficulty-${p.difficulty.toLowerCase()}`}>{p.difficulty}</span>
              <ArrowRight size={14} aria-hidden="true" className="s150-problem-card__arrow" />
            </div>
          </Link>
        ))}
      </div>
    </PageContainer>
  )
}
