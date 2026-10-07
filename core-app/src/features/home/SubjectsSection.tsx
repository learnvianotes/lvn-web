/* ============================================================
   SubjectsSection — the catalog subjects on the landing page.

     All               one section per category (DSA, CS Fundamentals,
                       Engineering, AI & Data, Programming) — compact
                       cards; on phones each section is a swipeable row
     Filter chips      everyone — one category, full cards (?c=dsa)
     Sort              signed-in (recommended, my order, recent, progress, A–Z)
     Rearrange         signed-in: drag cards (desktop) or use the arrow
                       buttons (touch / keyboard); saved to the account
   ============================================================ */

import { forwardRef, useMemo, useRef, useState, type DragEvent } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ArrowLeft, ArrowRight, ArrowUpDown, Check, GripVertical, RotateCcw } from 'lucide-react'
import type { SubjectSort } from '@core-schema/firestore'
import type { Catalog, Subject } from '@core/features/catalog/types'
import { SubjectCard } from '@core/features/catalog/SubjectCard'
import { SubjectIcon } from '@core/features/catalog/SubjectIcon'
import { useUser } from '@core/features/auth/auth'
import { useProgress } from '@core/features/progress/store'
import { useActivity } from '@core/features/progress/activity'
import { setSort, setSubjectOrder, usePrefs } from '@core/features/progress/prefs'
import { subjectProgress } from '@core/features/progress/stats'
import { track } from '@core/features/telemetry/track'
import { SORTS, customOrder, move, sortSubjects } from './subjectOrder'

/** One line under each category heading on the landing page. */
const CATEGORY_BLURB: Record<string, string> = {
  dsa: 'Problem-solving patterns and 150 practice problems.',
  fundamentals: 'The core computer science every interview expects.',
  engineering: 'How real software is built, secured and shipped.',
  ai: 'From classic AI to machine learning, deep learning and generative AI.',
  programming: 'Language notes from the basics to interview level.',
}

interface Props {
  catalog: Catalog
  highlighted?: string
  cardRef: (id: string, el: HTMLAnchorElement | null) => void
}

export function SubjectsSection({ catalog, highlighted, cardRef }: Props) {
  const user = useUser()
  const progress = useProgress()
  const activity = useActivity()
  const prefs = usePrefs()
  const [params, setParams] = useSearchParams()
  const [editing, setEditing] = useState<Subject[] | null>(null)

  const categories = catalog.categories ?? []
  const filter = params.get('c') ?? 'all'
  const sort: SubjectSort = user ? prefs.sort : 'default'

  const ordered = useMemo(
    () => sortSubjects(catalog.subjects, sort, { saved: prefs.subjectOrder, progress, activity }),
    [catalog.subjects, sort, prefs.subjectOrder, progress, activity],
  )
  const visible = filter === 'all' ? ordered : ordered.filter((s) => s.category === filter)
  const counts = useMemo(() => {
    const m = new Map<string, number>()
    for (const s of catalog.subjects) m.set(s.category ?? '', (m.get(s.category ?? '') ?? 0) + 1)
    return m
  }, [catalog.subjects])

  const chooseFilter = (id: string) => {
    const next = new URLSearchParams(params)
    if (id === 'all') next.delete('c')
    else next.set('c', id)
    setParams(next, { replace: true, preventScrollReset: true })
    track('subject_filter', { l: id })
  }
  const chooseSort = (id: SubjectSort) => {
    setSort(id)
    track('subject_sort', { l: id })
  }
  const startEditing = () => {
    chooseFilter('all')
    setEditing(customOrder([...catalog.subjects].sort((a, b) => a.order - b.order), sort === 'default' ? [] : ordered.map((s) => s.id)))
  }
  const save = () => {
    if (editing) setSubjectOrder(editing.map((s) => s.id))
    track('subject_sort', { l: 'custom-saved' })
    setEditing(null)
  }

  const renderCard = (s: Subject) => (
    <SubjectCard
      key={s.id}
      ref={(el) => cardRef(s.id, el)}
      to={`/${s.id}`}
      icon={s.icon}
      title={s.title}
      description={s.description}
      countLabel={`${s.itemCount} ${s.kind === 'problems' ? 'problems' : 'topics'}`}
      progress={user ? subjectProgress(s, progress) : undefined}
      highlighted={highlighted === s.id}
      category={s.category}
    />
  )

  return (
    <section className="home-section" id="subjects" aria-label="Subjects">
      {editing ? (
        <ReorderGrid items={editing} onChange={setEditing} onSave={save} onCancel={() => setEditing(null)} onReset={() => setEditing([...catalog.subjects].sort((a, b) => a.order - b.order))} />
      ) : (
        <>
          <div className="subject-bar">
            {categories.length > 0 && (
              <div className="filter-chips" role="tablist" aria-label="Filter subjects">
                <button role="tab" aria-selected={filter === 'all'} className="filter-chip" onClick={() => chooseFilter('all')}>
                  All <span className="filter-count">{catalog.subjects.length}</span>
                </button>
                {categories.filter((c) => counts.get(c.id)).map((c) => (
                  <button key={c.id} role="tab" aria-selected={filter === c.id} className="filter-chip" onClick={() => chooseFilter(c.id)}>
                    {c.title} <span className="filter-count">{counts.get(c.id)}</span>
                  </button>
                ))}
              </div>
            )}
            {user && (
              <div className="subject-tools">
                <label className="sort-select" title="Sort subjects">
                  <ArrowUpDown size={14} aria-hidden />
                  <span className="sr-only">Sort subjects</span>
                  <select value={sort} onChange={(e) => chooseSort(e.target.value as SubjectSort)}>
                    {SORTS.filter((s) => s.id !== 'custom' || prefs.subjectOrder.length).map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
                  </select>
                </label>
                <button className="icon-btn sm tool-btn" onClick={startEditing} aria-label="Rearrange subjects" title="Rearrange subjects">
                  <GripVertical size={16} />
                </button>
              </div>
            )}
          </div>
          {filter === 'all' && categories.length > 0 ? (
            categories.filter((c) => counts.get(c.id)).map((c) => (
              <section key={c.id} className="subject-group" data-cat={c.id} aria-labelledby={`group-${c.id}`}>
                <div className="subject-group-head">
                  <h2 id={`group-${c.id}`}>
                    <span className="cat-dot" aria-hidden />
                    {c.title}
                    <span className="subject-group-count">{counts.get(c.id)}</span>
                  </h2>
                  <button className="subject-group-more" onClick={() => chooseFilter(c.id)}>
                    See all <ArrowRight size={13} aria-hidden />
                  </button>
                </div>
                {CATEGORY_BLURB[c.id] && <p className="subject-group-blurb">{CATEGORY_BLURB[c.id]}</p>}
                <div className="card-grid subject-group-grid">
                  {ordered.filter((s) => s.category === c.id).map(renderCard)}
                </div>
              </section>
            ))
          ) : (
            <section className="subject-group is-filtered" data-cat={filter} aria-labelledby="group-filtered">
              <div className="subject-group-head">
                <h2 id="group-filtered">
                  <span className="cat-dot" aria-hidden />
                  {categories.find((c) => c.id === filter)?.title ?? 'Subjects'}
                  <span className="subject-group-count">{visible.length}</span>
                </h2>
                <button className="subject-group-more" onClick={() => chooseFilter('all')}>
                  <ArrowLeft size={13} aria-hidden /> All subjects
                </button>
              </div>
              {CATEGORY_BLURB[filter] && <p className="subject-group-blurb">{CATEGORY_BLURB[filter]}</p>}
              <div className="card-grid">{visible.map(renderCard)}</div>
            </section>
          )}
        </>
      )}
    </section>
  )
}

/* ── Rearrange mode ──────────────────────────────────────── */

interface ReorderProps {
  items: Subject[]
  onChange: (items: Subject[]) => void
  onSave: () => void
  onCancel: () => void
  onReset: () => void
}

function ReorderGrid({ items, onChange, onSave, onCancel, onReset }: ReorderProps) {
  const dragFrom = useRef<number | null>(null)
  const [over, setOver] = useState<number | null>(null)

  const onDragStart = (i: number) => (e: DragEvent) => {
    dragFrom.current = i
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/plain', items[i]!.id)
  }
  const onDrop = (i: number) => (e: DragEvent) => {
    e.preventDefault()
    if (dragFrom.current !== null && dragFrom.current !== i) onChange(move(items, dragFrom.current, i))
    dragFrom.current = null
    setOver(null)
  }

  return (
    <>
      <div className="reorder-bar" role="status">
        <p><GripVertical size={15} aria-hidden /> Drag the cards (or use the arrows) into the order you like.</p>
        <div className="reorder-actions">
          <button className="btn btn-sm" onClick={onReset}><RotateCcw size={14} aria-hidden /> Reset</button>
          <button className="btn btn-sm" onClick={onCancel}>Cancel</button>
          <button className="btn btn-sm btn-primary" onClick={onSave}><Check size={14} aria-hidden /> Save order</button>
        </div>
      </div>
      <ol className="card-grid reorder-grid">
        {items.map((s, i) => (
          <ReorderCard
            key={s.id}
            subject={s}
            index={i}
            total={items.length}
            isOver={over === i}
            draggable
            onDragStart={onDragStart(i)}
            onDragOver={(e) => { e.preventDefault(); setOver(i) }}
            onDragLeave={() => setOver((o) => (o === i ? null : o))}
            onDrop={onDrop(i)}
            onDragEnd={() => { dragFrom.current = null; setOver(null) }}
            onMove={(to) => onChange(move(items, i, to))}
          />
        ))}
      </ol>
    </>
  )
}

interface ReorderCardProps extends React.LiHTMLAttributes<HTMLLIElement> {
  subject: Subject
  index: number
  total: number
  isOver: boolean
  onMove: (to: number) => void
}

const ReorderCard = forwardRef<HTMLLIElement, ReorderCardProps>(function ReorderCard(
  { subject: s, index, total, isOver, onMove, ...li },
  ref,
) {
  return (
    <li ref={ref} className={`subject-card is-reorder ${isOver ? 'is-over' : ''}`} {...li}>
      <div className="subject-card-top">
        <span className="subject-card-icon"><SubjectIcon name={s.icon} size={20} /></span>
        <span className="reorder-pos">{index + 1}</span>
        <GripVertical size={18} className="reorder-grip" aria-hidden />
      </div>
      <h3 className="subject-card-title">{s.title}</h3>
      <div className="reorder-arrows">
        <button className="icon-btn sm" onClick={() => onMove(index - 1)} disabled={index === 0} aria-label={`Move ${s.title} earlier`}><ArrowLeft size={15} /></button>
        <button className="icon-btn sm" onClick={() => onMove(index + 1)} disabled={index === total - 1} aria-label={`Move ${s.title} later`}><ArrowRight size={15} /></button>
      </div>
    </li>
  )
})
