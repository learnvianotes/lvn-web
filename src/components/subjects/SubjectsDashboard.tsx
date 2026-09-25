/* ============================================================
   SubjectsDashboard — Complete Subject Explorer
   Search, Category Filtering, Continue Learning, Rearrange Grid
   ============================================================ */

import { useState, useEffect, useMemo, useRef, type DragEvent, type MouseEvent } from 'react'
import { Link } from 'react-router-dom'
import {
  Search,
  X,
  LayoutGrid,
  Cpu,
  GitFork,
  Sparkles,
  Wrench,
  ArrowUpDown,
  Check,
  RotateCcw,
  History,
  ArrowRight,
  GripVertical,
  ChevronLeft,
  ChevronRight,
  SearchX,
} from 'lucide-react'
import { SUBJECTS, SUBJECT_CATEGORIES, type CategoryId } from '@/data/subjects'
import { getSubjectIcon } from '@/data/subjectIcons'
import type { Subject } from '@/types'
import {
  subscribeContinueLearning,
  saveContinueLearning,
  savePreferences,
  getPreferences,
  type ContinueLearningData,
} from '@/lib/firestoreService'

const CATEGORY_ICONS = {
  all: LayoutGrid,
  'core-cs': Cpu,
  dsa: GitFork,
  'ai-ml': Sparkles,
  tools: Wrench,
} as const

type ContinueItem = ContinueLearningData

export function SubjectsDashboard() {
  const searchInputRef = useRef<HTMLInputElement>(null)

  // ── Search State ──────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState('')

  // ── Category Filter State ─────────────────────────────────
  const [selectedCategory, setSelectedCategory] = useState<CategoryId>(() => {
    try {
      const saved = localStorage.getItem('cnote_selected_category') as CategoryId | null
      if (saved && SUBJECT_CATEGORIES.some((c) => c.id === saved)) {
        return saved
      }
    } catch {
      // localStorage unavailable or restricted
    }
    return 'all'
  })

  // ── Rearrange Mode State ──────────────────────────────────
  const [isRearrangeMode, setIsRearrangeMode] = useState(false)
  const [draggedSubjectId, setDraggedSubjectId] = useState<string | null>(null)

  const defaultOrder = useMemo(() => SUBJECTS.map((s) => s.id), [])

  const [subjectOrder, setSubjectOrder] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem('cnote_grid_order')
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed) && parsed.length > 0) {
          const validSaved = parsed.filter((id: string) => SUBJECTS.some((s) => s.id === id))
          const missing = SUBJECTS.filter((s) => !validSaved.includes(s.id)).map((s) => s.id)
          return [...validSaved, ...missing]
        }
      }
    } catch {
      // fallback
    }
    return defaultOrder
  })

  // ── Continue Learning State (Firestore-backed) ────────────
  const [continueItem, setContinueItem] = useState<ContinueItem | null>(() => {
    // Seed from localStorage while Firestore loads
    try {
      const saved = localStorage.getItem('cnote_last_visited')
      if (saved) {
        const parsed = JSON.parse(saved)
        if (parsed?.subjectTitle && parsed?.topicTitle && parsed?.path) {
          return parsed as ContinueItem
        }
      }
    } catch {
      // ignore
    }
    return null
  })

  // Subscribe to Firestore real-time updates for Continue Learning
  useEffect(() => {
    let unsubscribe: (() => void) | undefined

    subscribeContinueLearning((data) => {
      if (data) {
        setContinueItem(data)
        // Mirror to localStorage for offline / instant reads on next mount
        try {
          localStorage.setItem('cnote_last_visited', JSON.stringify(data))
        } catch {
          // ignore
        }
      }
    }).then((unsub) => {
      unsubscribe = unsub
    }).catch(() => {
      // Firebase unavailable — fall back to localStorage (already seeded in state initializer)
    })

    return () => {
      if (unsubscribe) unsubscribe()
    }
  }, [])

  // ── Sync user preferences from Firestore on mount ──────────
  useEffect(() => {
    getPreferences()
      .then((prefs) => {
        if (prefs?.gridOrder && Array.isArray(prefs.gridOrder) && prefs.gridOrder.length > 0) {
          const validSaved = prefs.gridOrder.filter((id: string) => SUBJECTS.some((s) => s.id === id))
          const missing = SUBJECTS.filter((s) => !validSaved.includes(s.id)).map((s) => s.id)
          setSubjectOrder([...validSaved, ...missing])
        }
        if (prefs?.selectedCategory && SUBJECT_CATEGORIES.some((c) => c.id === prefs.selectedCategory)) {
          setSelectedCategory(prefs.selectedCategory as CategoryId)
        }
      })
      .catch(() => {})
  }, [])

  // ── Keyboard shortcut `/` to focus search & `Escape` ─────
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === '/' && document.activeElement?.tagName !== 'INPUT' && document.activeElement?.tagName !== 'TEXTAREA') {
        e.preventDefault()
        searchInputRef.current?.focus()
      } else if (e.key === 'Escape') {
        if (searchQuery) {
          setSearchQuery('')
          searchInputRef.current?.blur()
        }
        if (isRearrangeMode) {
          setIsRearrangeMode(false)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [searchQuery, isRearrangeMode])

  // ── Category Filter Handler ───────────────────────────────
  const handleCategorySelect = (categoryId: CategoryId) => {
    setSelectedCategory(categoryId)
    try {
      localStorage.setItem('cnote_selected_category', categoryId)
    } catch {
      // ignore
    }
    savePreferences({ selectedCategory: categoryId }).catch(() => {})
  }

  // ── Category Counts Map ───────────────────────────────────
  const categoryCounts = useMemo(() => {
    const counts: Record<string, number> = { all: SUBJECTS.length }
    for (const subject of SUBJECTS) {
      counts[subject.category] = (counts[subject.category] ?? 0) + 1
    }
    return counts
  }, [])

  // ── Ordered Subjects ──────────────────────────────────────
  const orderedSubjects = useMemo(() => {
    const map = new Map<string, Subject>()
    for (const s of SUBJECTS) {
      map.set(s.id, s)
    }
    const result: Subject[] = []
    for (const id of subjectOrder) {
      const item = map.get(id)
      if (item) result.push(item)
    }
    // Safety check for any subjects not in subjectOrder
    for (const s of SUBJECTS) {
      if (!subjectOrder.includes(s.id)) {
        result.push(s)
      }
    }
    return result
  }, [subjectOrder])

  // ── Filtered Subjects ─────────────────────────────────────
  const filteredSubjects = useMemo(() => {
    const q = searchQuery.trim().toLowerCase()
    return orderedSubjects.filter((subject) => {
      const matchesCategory = selectedCategory === 'all' || subject.category === selectedCategory
      if (!matchesCategory) return false

      if (!q) return true

      const titleMatches = subject.title.toLowerCase().includes(q)
      const descMatches = subject.description.toLowerCase().includes(q)
      const keywordsMatches = subject.keywords?.toLowerCase().includes(q) ?? false
      const tagsMatches = subject.displayTags?.some((t: string) => t.toLowerCase().includes(q)) ?? false

      return titleMatches || descMatches || keywordsMatches || tagsMatches
    })
  }, [orderedSubjects, selectedCategory, searchQuery])

  // ── Rearrange Actions ─────────────────────────────────────
  const toggleRearrangeMode = () => {
    setIsRearrangeMode((prev) => !prev)
  }

  const resetGridOrder = () => {
    try {
      localStorage.removeItem('cnote_grid_order')
    } catch {
      // ignore
    }
    setSubjectOrder(defaultOrder)
    savePreferences({ gridOrder: defaultOrder }).catch(() => {})
  }

  const moveSubject = (subjectId: string, direction: -1 | 1, e: MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()

    setSubjectOrder((prev) => {
      const idx = prev.indexOf(subjectId)
      if (idx === -1) return prev
      const targetIdx = idx + direction
      if (targetIdx < 0 || targetIdx >= prev.length) return prev

      const next = [...prev]
      const [moved] = next.splice(idx, 1)
      next.splice(targetIdx, 0, moved)

      try {
        localStorage.setItem('cnote_grid_order', JSON.stringify(next))
      } catch {
        // ignore
      }
      savePreferences({ gridOrder: next }).catch(() => {})
      return next
    })
  }

  // ── Drag & Drop Handlers ──────────────────────────────────
  const handleDragStart = (e: DragEvent, subjectId: string) => {
    if (!isRearrangeMode) return
    setDraggedSubjectId(subjectId)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', subjectId)
  }

  const handleDragOver = (e: DragEvent) => {
    if (!isRearrangeMode) return
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
  }

  const handleDrop = (e: DragEvent, targetSubjectId: string) => {
    if (!isRearrangeMode) return
    e.preventDefault()
    const sourceId = e.dataTransfer.getData('text/plain') || draggedSubjectId
    if (!sourceId || sourceId === targetSubjectId) return

    setSubjectOrder((prev) => {
      const sourceIdx = prev.indexOf(sourceId)
      const targetIdx = prev.indexOf(targetSubjectId)
      if (sourceIdx === -1 || targetIdx === -1) return prev

      const next = [...prev]
      const [moved] = next.splice(sourceIdx, 1)
      next.splice(targetIdx, 0, moved)

      try {
        localStorage.setItem('cnote_grid_order', JSON.stringify(next))
      } catch {
        // ignore
      }
      savePreferences({ gridOrder: next }).catch(() => {})
      return next
    })
    setDraggedSubjectId(null)
  }

  const handleDragEnd = () => {
    setDraggedSubjectId(null)
  }

  return (
    <div className="subjects-dashboard">
      {/* ── Continue Learning Section ──────────────────────── */}
      {continueItem && (
        <section className="continue-section" aria-labelledby="continue-learning-title">
          <div className="section-label" id="continue-learning-title">
            <History size={13} aria-hidden="true" />
            <span>Continue Learning</span>
          </div>

          <div className="continue-row">
            <Link
              to={continueItem.path}
              className="continue-card"
              aria-label={`Continue learning ${continueItem.subjectTitle}: ${continueItem.topicTitle}`}
            >
              <div className="continue-card__header">
                <span className="continue-subject" style={{ color: continueItem.color }}>
                  {continueItem.subjectTitle}
                </span>
              </div>
              <div className="continue-card__main">
                <span
                  className="continue-dot"
                  style={{ backgroundColor: continueItem.color }}
                  aria-hidden="true"
                />
                <span className="continue-topic">{continueItem.topicTitle}</span>
                <ArrowRight size={16} className="continue-arrow" aria-hidden="true" />
              </div>
              <div className="continue-card__footer">
                <span className="continue-hint">Continue where you left off</span>
              </div>
            </Link>
          </div>
        </section>
      )}

      {/* ── Search & Filter Controls ───────────────────────── */}
      <div className="controls-wrapper">
        {/* Search input */}
        <div className="search-box">
          <Search size={16} className="search-icon" aria-hidden="true" />
          <input
            ref={searchInputRef}
            type="text"
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search subjects, topics, or tags (e.g. Kafka, Dynamic Programming, ACID, REST, Sheet 150)..."
            aria-label="Search subjects, topics, or tags"
          />
          {searchQuery && (
            <button
              type="button"
              className="clear-search-btn"
              onClick={() => {
                setSearchQuery('')
                searchInputRef.current?.focus()
              }}
              aria-label="Clear search query"
            >
              <X size={15} />
            </button>
          )}
          <span className="kbd-hint" aria-hidden="true">/</span>
        </div>

        {/* Categories and Rearrange Bar */}
        <div className="filter-rearrange-bar">
          <div className="category-filter-bar" role="group" aria-label="Filter subjects by category">
            {SUBJECT_CATEGORIES.map((cat) => {
              const Icon = CATEGORY_ICONS[cat.id]
              const count = categoryCounts[cat.id] ?? 0
              const isActive = selectedCategory === cat.id

              return (
                <button
                  key={cat.id}
                  type="button"
                  className={`cat-pill ${isActive ? 'active' : ''}`}
                  onClick={() => handleCategorySelect(cat.id)}
                  aria-pressed={isActive}
                >
                  <Icon size={14} aria-hidden="true" />
                  <span>{cat.label}</span>
                  <span className="cat-count">{count}</span>
                </button>
              )
            })}
          </div>

          <div className="rearrange-actions">
            <button
              type="button"
              className={`rearrange-toggle-btn ${isRearrangeMode ? 'is-active' : ''}`}
              onClick={toggleRearrangeMode}
              title={isRearrangeMode ? 'Finish reordering subjects' : 'Enter rearrange mode to reorder subject cards'}
            >
              {isRearrangeMode ? (
                <>
                  <Check size={14} />
                  <span>Done Rearranging</span>
                </>
              ) : (
                <>
                  <ArrowUpDown size={14} />
                  <span>Rearrange</span>
                </>
              )}
            </button>

            {isRearrangeMode && (
              <button
                type="button"
                className="rearrange-reset-btn"
                onClick={resetGridOrder}
                title="Reset to default order"
              >
                <RotateCcw size={13} />
                <span>Reset Order</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* ── Subjects Section Heading ───────────────────────── */}
      <div className="section-label" id="subjects-heading">
        <LayoutGrid size={13} aria-hidden="true" />
        <span>Subjects &amp; Roadmaps</span>
      </div>

      {/* ── Cards Grid ─────────────────────────────────────── */}
      <div className="subject-cards" role="list" aria-labelledby="subjects-heading">
        {filteredSubjects.map((subject, index) => {
          const Icon = getSubjectIcon(subject.id)
          const isDragging = draggedSubjectId === subject.id

          return (
            <Link
              key={subject.id}
              to={isRearrangeMode ? '#' : `/subjects/${subject.id}`}
              onClick={(e) => {
                if (isRearrangeMode) {
                  e.preventDefault()
                } else {
                  // Save last visited subject
                  const continueData = {
                    subjectId: subject.id,
                    subjectTitle: subject.title.toUpperCase(),
                    topicTitle: subject.shortTitle || subject.title,
                    path: `/subjects/${subject.id}`,
                    color: '#7c6ff7',
                  }
                  try {
                    localStorage.setItem('cnote_last_visited', JSON.stringify(continueData))
                  } catch {
                    // ignore
                  }
                  saveContinueLearning(continueData).catch(() => {})
                }
              }}
              draggable={isRearrangeMode}
              onDragStart={(e) => handleDragStart(e, subject.id)}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, subject.id)}
              onDragEnd={handleDragEnd}
              className={`subject-card ${isRearrangeMode ? 'is-rearranging' : ''} ${isDragging ? 'is-dragging' : ''}`}
              role="listitem"
              aria-label={subject.title}
            >
              {/* Drag badge & move arrows when rearranging */}
              {isRearrangeMode && (
                <>
                  <div className="drag-badge" aria-hidden="true">
                    <GripVertical size={12} />
                    <span>Drag</span>
                  </div>

                  <div className="rearrange-controls">
                    <button
                      type="button"
                      className="rearrange-btn-move"
                      disabled={index === 0}
                      onClick={(e) => moveSubject(subject.id, -1, e)}
                      title="Move card left"
                      aria-label={`Move ${subject.title} left`}
                    >
                      <ChevronLeft size={14} />
                    </button>
                    <button
                      type="button"
                      className="rearrange-btn-move"
                      disabled={index === filteredSubjects.length - 1}
                      onClick={(e) => moveSubject(subject.id, 1, e)}
                      title="Move card right"
                      aria-label={`Move ${subject.title} right`}
                    >
                      <ChevronRight size={14} />
                    </button>
                  </div>
                </>
              )}

              {/* Card top row: icon + live badge */}
              <div className="subject-card__top">
                <span className="subject-card__icon" aria-hidden="true">
                  <Icon size={20} strokeWidth={1.5} />
                </span>
                <span className="subject-card__live">LIVE</span>
              </div>

              {/* Card body */}
              <div className="subject-card__body">
                <h3 className="subject-card__title">{subject.title}</h3>
                <p className="subject-card__description">{subject.description}</p>
              </div>

              {/* Card footer: tags + arrow */}
              <div className="subject-card__footer">
                <div className="subject-card__tags">
                  {(subject.displayTags ?? []).map((tag: string) => (
                    <span key={tag} className="subject-card__tag">
                      {tag}
                    </span>
                  ))}
                </div>
                <span className="subject-card__arrow" aria-hidden="true">
                  <ArrowRight size={14} />
                </span>
              </div>
            </Link>
          )
        })}

        {/* ── Empty State when no subjects match ───────────── */}
        {filteredSubjects.length === 0 && (
          <div className="no-results" role="status" aria-live="polite">
            <SearchX size={36} className="no-results__icon" aria-hidden="true" />
            <h3 className="no-results__title">No subjects match your search</h3>
            <p className="no-results__desc">
              Try searching for &quot;Kafka&quot;, &quot;Dynamic Programming&quot;, &quot;SQL&quot;, &quot;ACID&quot;, or &quot;Sheet 150&quot;
            </p>
            <button
              type="button"
              className="no-results__clear"
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('all')
              }}
            >
              Clear search &amp; filters
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
