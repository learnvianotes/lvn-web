/* ============================================================
   ProblemCard — one Sheet 150 problem, always in this order:
   statement → I/O → constraints → key observations → naive
   approach → intuition → algorithm → optimized code →
   complexity → variants / takeaway → similar problems.
   ============================================================ */

import { memo, type ReactNode } from 'react'
import {
  ArrowLeftRight, Bookmark, Code2, ExternalLink, FileText, Layers, Lightbulb, ListOrdered, Ruler, Sparkles, Timer, Turtle, Youtube,
  type LucideIcon,
} from 'lucide-react'
import type { Problem, Solution } from '@/features/catalog/types'
import { setProblemStatus, type ProblemStatus } from '@/features/progress/store'
import { ContentView } from '@/features/content/ContentView'
import { Difficulty } from './Difficulty'
import { CodeTabs } from '@/features/study/content/CodeTabs'
import { ListenButton } from '@/features/voice/ListenButton'
import { segmentsFrom } from '@/features/voice/speech'


const STATUSES: { id: ProblemStatus; label: string }[] = [
  { id: 'todo', label: 'To do' },
  { id: 'solved', label: 'Solved' },
  { id: 'revisit', label: 'Revisit' },
]

function StatusControl({ problemId, status }: { problemId: string; status: ProblemStatus }) {
  return (
    <div className="segmented" role="radiogroup" aria-label="Status">
      {STATUSES.map((s) => (
        <button
          key={s.id}
          role="radio"
          aria-checked={status === s.id}
          className={`segmented-item is-${s.id}`}
          onClick={() => setProblemStatus(problemId, s.id)}
        >
          {s.label}
        </button>
      ))}
    </div>
  )
}

function Section({ title, icon: Icon, kind, children }: { title: string; icon: LucideIcon; kind?: string; children: ReactNode }) {
  return (
    <section className={`pc-box ${kind ? `pc-box--${kind}` : ''}`}>
      <h3 className="pc-box-head">
        <Icon size={16} aria-hidden />
        <span className="pc-box-title">{title}</span>
      </h3>
      <div className="pc-box-body">{children}</div>
    </section>
  )
}

function Complexity({ items }: { items?: string[] }) {
  if (!items?.length) return null
  return (
    <div className="chips">
      {items.map((c) => <span key={c} className="chip">{c}</span>)}
    </div>
  )
}

function SolutionBody({ solution }: { solution: Solution }) {
  return (
    <>
      {solution.content.length > 0 && <ContentView content={solution.content} />}
      <CodeTabs code={solution.code} />
    </>
  )
}

interface Props {
  problem: Problem
  index: number
  status: ProblemStatus
  /** status + read-aloud are for signed-in learners */
  signedIn: boolean
}

export const ProblemCard = memo(function ProblemCard({ problem: p, index, status, signedIn }: Props) {
  return (
    <article className={`problem-card is-${status}`} id={p.id} aria-labelledby={`${p.id}-title`}>
      <header className="pc-header">
        <div className="pc-heading">
          <span className="pc-eyebrow">#{index} · LeetCode {p.lc}</span>
          <h2 id={`${p.id}-title`}>{p.title}</h2>
        </div>
        <div className="pc-actions">
          <Difficulty level={p.difficulty} />
          {signedIn && <StatusControl problemId={p.id} status={status} />}
          {signedIn && <ListenButton
            title={`LC ${p.lc} · ${p.title}`}
            compact
            segments={() => {
              const card = document.getElementById(p.id)
              return [{ text: `${p.title}.`, el: card?.querySelector('h2') }, ...(card ? segmentsFrom(card).filter((s) => !s.el?.closest('.pc-header')) : [])]
            }}
          />}
          {p.leetcodeUrl && (
            <a className="btn btn-sm" href={p.leetcodeUrl} target="_blank" rel="noopener noreferrer">
              LeetCode <ExternalLink size={14} aria-hidden />
            </a>
          )}
          {p.youtubeUrl ? (
            <a className="icon-btn" href={p.youtubeUrl} target="_blank" rel="noopener noreferrer" aria-label="Video explanation on YouTube">
              <Youtube size={18} />
            </a>
          ) : (
            <span className="icon-btn is-disabled" title="Video explanation coming soon" aria-label="Video explanation coming soon">
              <Youtube size={18} />
            </span>
          )}
        </div>
      </header>

      {p.statement && <Section title="Problem statement" icon={FileText} kind="statement"><ContentView content={p.statement} /></Section>}
      {p.io && <Section title="Input & output" icon={ArrowLeftRight}><ContentView content={p.io} /></Section>}
      {p.constraints && <Section title="Constraints" icon={Ruler}><ContentView content={p.constraints} /></Section>}
      {p.understanding && <Section title="Key observations" icon={Lightbulb}><ContentView content={p.understanding} /></Section>}
      {p.naive && (
        <Section title={p.naive.title || 'Naive approach'} icon={Turtle}>
          <SolutionBody solution={p.naive} />
          {p.naive.complexity?.length ? <div className="pc-complexity"><span>Complexity</span><Complexity items={p.naive.complexity} /></div> : null}
        </Section>
      )}
      {p.intuition && <Section title="Intuition" icon={Sparkles} kind="intuition"><ContentView content={p.intuition} /></Section>}
      {p.approach && <Section title="Algorithm" icon={ListOrdered}><ContentView content={p.approach} /></Section>}
      {p.optimal && (
        <Section title={p.optimal.title || 'Optimized code'} icon={Code2} kind="optimal">
          <SolutionBody solution={p.optimal} />
        </Section>
      )}
      {p.optimal?.complexity?.length ? (
        <Section title="Time & space complexity" icon={Timer} kind="complexity"><Complexity items={p.optimal.complexity} /></Section>
      ) : null}
      {p.variants && <Section title="Variants" icon={Layers}><ContentView content={p.variants} /></Section>}
      {p.takeaway && <Section title="Pattern & takeaway" icon={Bookmark}><ContentView content={p.takeaway} /></Section>}
      {p.extra?.map((x) => <Section key={x.title} title={x.title} icon={Bookmark}><ContentView content={x.content} /></Section>)}
      {p.similar?.length ? (
        <details className="pc-similar">
          <summary>Similar problems ({p.similar.length})</summary>
          <ul>
            {p.similar.map((s) => (
              <li key={s.url || s.title}>
                <a href={s.url} target="_blank" rel="noopener noreferrer">
                  <span>{s.title}</span>
                  {s.lc ? <span className="muted">LC {s.lc}</span> : null}
                  {s.difficulty && <Difficulty level={s.difficulty.charAt(0).toUpperCase() + s.difficulty.slice(1)} />}
                </a>
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </article>
  )
})
