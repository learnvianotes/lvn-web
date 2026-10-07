/* ============================================================
   HomeHero — the top of the landing page for visitors: what the
   site is, three numbers that prove it, and "Start learning".
   (The old signed-in hero — streak, goal, continue — needs an
   account; the guest-only /core pages show this one.)
   ============================================================ */

import { useMemo } from 'react'
import { ArrowRight } from 'lucide-react'
import type { Catalog } from '@core/features/catalog/types'

/** Landing hero for visitors who aren't signed in. */
export function GuestHero({ catalog }: { catalog: Catalog }) {
  const stats = useMemo(() => {
    let topics = 0
    let problems = 0
    for (const s of catalog.subjects) {
      if (s.kind === 'problems') problems += s.itemCount
      else topics += s.itemCount
    }
    return { subjects: catalog.subjects.length, topics, problems }
  }, [catalog])

  return (
    <section className="hero hero-guest" aria-label="Welcome">
      <div className="hero-guest-text">
        <h1>Interview-ready CS, one note at a time.</h1>
        <p>
          Focused notes and curated problems across DSA, core CS, engineering, AI and programming.
          Free to read.
        </p>
      </div>
      <ul className="hero-stats" aria-label="What's inside">
        <li><strong>{stats.subjects}</strong><span>subjects</span></li>
        <li><strong>{stats.topics}</strong><span>topics</span></li>
        <li><strong>{stats.problems}</strong><span>problems</span></li>
      </ul>
      <div className="hero-actions">
        <a className="btn btn-primary hero-cta" href="#subjects">Start learning <ArrowRight size={15} aria-hidden /></a>
      </div>
    </section>
  )
}
